"""Worker manager for coordinating multiple async camera workers.

This module manages a pool of async worker processes, distributing cameras
across them and monitoring their health.
"""
import logging
import multiprocessing
import time
import signal
from typing import List, Dict, Any, Optional
from pathlib import Path

from .async_camera_worker import run_async_worker
from .encoding_pool_manager import EncodingPoolManager


class WorkerManager:
    """Manages multiple async camera worker processes.

    This manager coordinates 20 worker processes, each handling multiple cameras
    concurrently using async I/O. It provides health monitoring, graceful shutdown,
    and automatic worker recovery.
    """

    def __init__(
        self,
        camera_configs: List[Dict[str, Any]],
        stream_config: Dict[str, Any],
        num_workers: int = 20,
        num_encoding_workers: Optional[int] = None
    ):
        """Initialize worker manager.

        Args:
            camera_configs: List of all camera configurations
            stream_config: Streaming configuration (Redis, Kafka, etc.)
            num_workers: Number of async I/O worker processes (default: 20)
            num_encoding_workers: Number of encoding workers (default: CPU_count - 2)
        """
        self.camera_configs = camera_configs
        self.stream_config = stream_config
        self.num_workers = num_workers
        self.num_encoding_workers = num_encoding_workers

        self.logger = logging.getLogger(__name__)

        # Multiprocessing primitives
        self.stop_event = multiprocessing.Event()
        self.health_queue = multiprocessing.Queue()

        # Worker processes
        self.workers: List[multiprocessing.Process] = []
        self.worker_camera_assignments: Dict[int, List[Dict[str, Any]]] = {}

        # Encoding pool
        self.encoding_pool_manager: Optional[EncodingPoolManager] = None
        self.encoding_pool: Optional[multiprocessing.Pool] = None

        # Health monitoring
        self.last_health_reports: Dict[int, Dict[str, Any]] = {}

        self.logger.info(
            f"WorkerManager initialized: {num_workers} workers, "
            f"{len(camera_configs)} cameras total"
        )

    def start(self):
        """Start all workers and begin streaming."""
        try:
            # Distribute cameras across workers (static partitioning)
            self._distribute_cameras()

            # Note: Encoding pool not needed - each worker uses asyncio.to_thread()
            # which provides good enough parallelism for JPEG encoding (mostly C code)

            # Start worker processes
            self.logger.info(f"Starting {self.num_workers} worker processes...")
            for worker_id in range(self.num_workers):
                self._start_worker(worker_id)

            self.logger.info(
                f"All workers started! "
                f"Streaming {len(self.camera_configs)} cameras across {self.num_workers} workers"
            )

        except Exception as exc:
            self.logger.error(f"Failed to start workers: {exc}")
            self.stop()
            raise

    def _distribute_cameras(self):
        """Distribute cameras across workers using static partitioning."""
        total_cameras = len(self.camera_configs)
        cameras_per_worker = total_cameras // self.num_workers
        remainder = total_cameras % self.num_workers

        self.logger.info(
            f"Distributing {total_cameras} cameras: "
            f"~{cameras_per_worker} per worker"
        )

        camera_idx = 0
        for worker_id in range(self.num_workers):
            # Some workers get 1 extra camera if there's a remainder
            num_cameras = cameras_per_worker + (1 if worker_id < remainder else 0)

            worker_cameras = self.camera_configs[camera_idx:camera_idx + num_cameras]
            self.worker_camera_assignments[worker_id] = worker_cameras

            self.logger.info(
                f"Worker {worker_id}: {len(worker_cameras)} cameras "
                f"(indices {camera_idx} to {camera_idx + num_cameras - 1})"
            )

            camera_idx += num_cameras

    def _start_worker(self, worker_id: int):
        """Start a single worker process.

        Args:
            worker_id: Worker identifier
        """
        worker_cameras = self.worker_camera_assignments.get(worker_id, [])

        if not worker_cameras:
            self.logger.warning(f"Worker {worker_id} has no cameras assigned, skipping")
            return

        try:
            worker = multiprocessing.Process(
                target=run_async_worker,
                args=(
                    worker_id,
                    worker_cameras,
                    self.stream_config,
                    self.stop_event,
                    self.health_queue
                ),
                name=f"AsyncWorker-{worker_id}",
                daemon=False  # Non-daemon so we can properly wait for shutdown
            )
            worker.start()
            self.workers.append(worker)

            self.logger.info(
                f"Started worker {worker_id} (PID: {worker.pid}) "
                f"with {len(worker_cameras)} cameras"
            )

        except Exception as exc:
            self.logger.error(f"Failed to start worker {worker_id}: {exc}")
            raise

    def monitor(self, duration: Optional[float] = None):
        """Monitor workers and collect health reports.

        Args:
            duration: How long to monitor (None = indefinite)
        """
        self.logger.info("Starting health monitoring...")

        start_time = time.time()
        last_summary_time = start_time

        try:
            while not self.stop_event.is_set():
                # Check if duration exceeded
                if duration and (time.time() - start_time) >= duration:
                    self.logger.info(f"Monitoring duration ({duration}s) complete")
                    break

                # Collect health reports
                while not self.health_queue.empty():
                    try:
                        report = self.health_queue.get_nowait()
                        worker_id = report['worker_id']
                        self.last_health_reports[worker_id] = report

                        # Log significant status changes
                        if report['status'] in ['error', 'stopped']:
                            self.logger.warning(
                                f"Worker {worker_id} status: {report['status']}"
                                f" (error: {report.get('error', 'None')})"
                            )

                    except Exception as exc:
                        self.logger.error(f"Error processing health report: {exc}")

                # Check worker processes
                for i, worker in enumerate(self.workers):
                    if not worker.is_alive() and not self.stop_event.is_set():
                        self.logger.error(
                            f"Worker {i} (PID: {worker.pid}) died unexpectedly! "
                            f"Exit code: {worker.exitcode}"
                        )

                # Print summary every 10 seconds
                if time.time() - last_summary_time >= 10.0:
                    self._print_health_summary()
                    last_summary_time = time.time()

                time.sleep(0.5)

        except KeyboardInterrupt:
            self.logger.info("Monitoring interrupted by user")

    def _print_health_summary(self):
        """Print summary of worker health."""
        running_workers = sum(1 for w in self.workers if w.is_alive())
        total_cameras = sum(
            report.get('active_cameras', 0)
            for report in self.last_health_reports.values()
        )

        self.logger.info(
            f"Health Summary: {running_workers}/{len(self.workers)} workers alive, "
            f"{total_cameras} active cameras"
        )

        # Detailed per-worker status
        for worker_id, report in sorted(self.last_health_reports.items()):
            status = report.get('status', 'unknown')
            cameras = report.get('active_cameras', 0)
            age = time.time() - report.get('timestamp', 0)

            self.logger.debug(
                f"  Worker {worker_id}: {status}, {cameras} cameras, "
                f"last report {age:.1f}s ago"
            )

    def stop(self, timeout: float = 15.0):
        """Stop all workers gracefully.

        Args:
            timeout: Maximum time to wait per worker (seconds)
        """
        self.logger.info("Stopping all workers...")

        # Signal stop
        self.stop_event.set()

        # Wait for workers to finish
        for i, worker in enumerate(self.workers):
            if worker.is_alive():
                self.logger.info(f"Waiting for worker {i} to stop...")
                worker.join(timeout=timeout)

                if worker.is_alive():
                    self.logger.warning(
                        f"Worker {i} did not stop gracefully, terminating..."
                    )
                    worker.terminate()
                    worker.join(timeout=5.0)

                    if worker.is_alive():
                        self.logger.error(f"Worker {i} could not be stopped!")
                    else:
                        self.logger.info(f"Worker {i} terminated")
                else:
                    self.logger.info(f"Worker {i} stopped gracefully")

        # Final summary
        self.logger.info("="*60)
        self.logger.info("SHUTDOWN COMPLETE")
        self.logger.info("="*60)
        self._print_final_summary()

    def _print_final_summary(self):
        """Print final summary of worker status."""
        total_cameras_assigned = sum(
            len(cameras)
            for cameras in self.worker_camera_assignments.values()
        )

        self.logger.info(f"Total cameras assigned: {total_cameras_assigned}")
        self.logger.info(f"Workers started: {len(self.workers)}")

        # Count workers by exit status
        normal_exits = sum(1 for w in self.workers if w.exitcode == 0)
        error_exits = sum(1 for w in self.workers if w.exitcode != 0 and w.exitcode is not None)
        still_alive = sum(1 for w in self.workers if w.is_alive())

        self.logger.info(
            f"Exit status: {normal_exits} normal, {error_exits} errors, "
            f"{still_alive} still alive"
        )

        # Last health reports
        if self.last_health_reports:
            self.logger.info("Last health reports:")
            for worker_id in sorted(self.last_health_reports.keys()):
                report = self.last_health_reports[worker_id]
                self.logger.info(
                    f"  Worker {worker_id}: {report['status']}, "
                    f"{report.get('active_cameras', 0)} cameras"
                )

    def run(self, duration: Optional[float] = None):
        """Start workers and monitor until stopped.

        This is the main entry point that combines start(), monitor(), and stop().

        Args:
            duration: How long to run (None = until interrupted)
        """
        try:
            # Setup signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

            # Start all workers
            self.start()

            # Monitor
            self.monitor(duration=duration)

        except Exception as exc:
            self.logger.error(f"Error in run loop: {exc}", exc_info=True)

        finally:
            # Always cleanup
            self.stop()

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        signal_name = signal.Signals(signum).name
        self.logger.info(f"Received {signal_name}, initiating graceful shutdown...")
        self.stop_event.set()

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
