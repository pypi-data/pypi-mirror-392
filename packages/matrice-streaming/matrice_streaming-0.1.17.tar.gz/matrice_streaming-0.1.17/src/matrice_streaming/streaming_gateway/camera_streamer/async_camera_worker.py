"""Async camera worker process for handling multiple cameras concurrently.

This module implements an async event loop worker that handles multiple cameras
in a single process using asyncio for efficient I/O-bound operations.
"""
import asyncio
import logging
import time
import multiprocessing
from typing import Dict, Any, Optional, List, Union
import cv2
from pathlib import Path

from .video_capture_manager import VideoCaptureManager
from .frame_processor import FrameProcessor
from .message_builder import StreamMessageBuilder
from .stream_statistics import StreamStatistics


class AsyncCameraWorker:
    """Async worker process that handles multiple cameras concurrently.

    This worker runs an async event loop to handle I/O-bound operations
    (video capture, Redis writes) for multiple cameras efficiently.
    """

    def __init__(
        self,
        worker_id: int,
        camera_configs: List[Dict[str, Any]],
        stream_config: Dict[str, Any],
        stop_event: multiprocessing.Event,
        health_queue: multiprocessing.Queue
    ):
        """Initialize async camera worker.

        Args:
            worker_id: Unique identifier for this worker
            camera_configs: List of camera configurations to handle
            stream_config: Streaming configuration (Redis, Kafka, etc.)
            stop_event: Event to signal worker shutdown
            health_queue: Queue for reporting health status
        """
        self.worker_id = worker_id
        self.camera_configs = camera_configs
        self.stream_config = stream_config
        self.stop_event = stop_event
        self.health_queue = health_queue

        # Setup logging with worker ID
        self.logger = logging.getLogger(f"AsyncWorker-{worker_id}")
        self.logger.info(f"Initializing worker {worker_id} with {len(camera_configs)} cameras")

        # Initialize components
        self.capture_manager = VideoCaptureManager()
        self.message_builder = StreamMessageBuilder(
            service_id=stream_config.get('service_id', 'streaming_gateway'),
            strip_input_content=False
        )
        self.statistics = StreamStatistics()

        # Track camera tasks
        self.camera_tasks: Dict[str, asyncio.Task] = {}
        self.captures: Dict[str, cv2.VideoCapture] = {}

        # Setup async Redis client
        self.redis_client = None

    async def initialize(self):
        """Initialize async resources (Redis client, etc.)."""
        try:
            # Import and initialize async Redis client
            from matrice_common.stream import MatriceStream, StreamType

            # Create MatriceStream with async support
            self.stream = MatriceStream(
                stream_type=StreamType.REDIS,
                config=self.stream_config
            )

            # Use async client
            self.redis_client = self.stream.async_client
            await self.redis_client.setup_client()

            self.logger.info(f"Worker {self.worker_id}: Initialized async Redis client")

        except Exception as exc:
            self.logger.error(f"Worker {self.worker_id}: Failed to initialize: {exc}")
            raise

    async def run(self):
        """Main worker loop - starts async tasks for all cameras."""
        try:
            # Initialize async resources
            await self.initialize()

            # Start camera tasks
            for camera_config in self.camera_configs:
                stream_key = camera_config['stream_key']
                task = asyncio.create_task(
                    self._camera_handler(camera_config),
                    name=f"camera-{stream_key}"
                )
                self.camera_tasks[stream_key] = task
                self.logger.info(f"Worker {self.worker_id}: Started task for camera {stream_key}")

            # Report initial health
            self._report_health("running")

            # Monitor tasks and stop event
            while not self.stop_event.is_set():
                # Check for completed/failed tasks
                for stream_key, task in list(self.camera_tasks.items()):
                    if task.done():
                        try:
                            # Check if task raised exception
                            task.result()
                            self.logger.warning(f"Worker {self.worker_id}: Camera {stream_key} task completed")
                        except Exception as exc:
                            self.logger.error(f"Worker {self.worker_id}: Camera {stream_key} task failed: {exc}")

                        # Remove completed task
                        del self.camera_tasks[stream_key]

                # Report health periodically
                self._report_health("running", len(self.camera_tasks))

                # Sleep briefly
                await asyncio.sleep(1.0)

            # Stop event set - graceful shutdown
            self.logger.info(f"Worker {self.worker_id}: Stop event detected, shutting down...")
            await self._shutdown()

        except Exception as exc:
            self.logger.error(f"Worker {self.worker_id}: Fatal error in run loop: {exc}")
            self._report_health("error", error=str(exc))
            raise

    async def _camera_handler(self, camera_config: Dict[str, Any]):
        """Handle a single camera with async I/O.

        Args:
            camera_config: Camera configuration dictionary
        """
        stream_key = camera_config['stream_key']
        stream_group_key = camera_config.get('stream_group_key', 'default')
        source = camera_config['source']
        topic = camera_config['topic']
        fps = camera_config.get('fps', 30)
        quality = camera_config.get('quality', 90)
        width = camera_config.get('width')
        height = camera_config.get('height')
        camera_location = camera_config.get('camera_location', 'Unknown')

        cap = None
        consecutive_failures = 0
        max_failures = 10

        try:
            # Prepare source (download if URL)
            prepared_source = self.capture_manager.prepare_source(source, stream_key)

            # Open capture in thread pool (blocking operation)
            cap, source_type = await asyncio.to_thread(
                self.capture_manager.open_capture,
                prepared_source, width, height
            )
            self.captures[stream_key] = cap

            # Get video properties
            video_props = self.capture_manager.get_video_properties(cap)
            original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            actual_width, actual_height = FrameProcessor.calculate_actual_dimensions(
                original_width, original_height, width, height
            )

            self.logger.info(
                f"Worker {self.worker_id}: Camera {stream_key} opened - "
                f"{actual_width}x{actual_height} @ {fps} FPS"
            )

            frame_counter = 0

            # Main camera loop
            while not self.stop_event.is_set():
                try:
                    # Read frame (blocking - run in thread pool)
                    read_start = time.time()
                    ret, frame = await asyncio.to_thread(cap.read)
                    read_time = time.time() - read_start

                    if not ret:
                        consecutive_failures += 1
                        if consecutive_failures >= max_failures:
                            self.logger.error(
                                f"Worker {self.worker_id}: Camera {stream_key} - "
                                f"Max consecutive failures ({max_failures}) reached"
                            )
                            break
                        await asyncio.sleep(0.1)
                        continue

                    # Reset failure counter
                    consecutive_failures = 0
                    frame_counter += 1

                    # Resize if needed
                    if width or height:
                        frame = FrameProcessor.resize_frame(frame, width, height)

                    # Process and send frame
                    await self._process_and_send_frame(
                        frame, stream_key, stream_group_key, topic,
                        source, video_props, fps, quality,
                        actual_width, actual_height, source_type,
                        frame_counter, camera_location, read_time
                    )

                    # Maintain FPS for video files
                    if source_type == "video_file":
                        await asyncio.sleep(1.0 / fps)

                except asyncio.CancelledError:
                    self.logger.info(f"Worker {self.worker_id}: Camera {stream_key} task cancelled")
                    break
                except Exception as exc:
                    self.logger.error(f"Worker {self.worker_id}: Error in camera {stream_key}: {exc}")
                    consecutive_failures += 1
                    if consecutive_failures >= max_failures:
                        break
                    await asyncio.sleep(1.0)

        finally:
            # Cleanup
            if cap and stream_key in self.captures:
                cap.release()
                del self.captures[stream_key]
                self.logger.info(f"Worker {self.worker_id}: Released camera {stream_key}")

    async def _process_and_send_frame(
        self,
        frame,
        stream_key: str,
        stream_group_key: str,
        topic: str,
        source: Union[str, int],
        video_props: Dict[str, Any],
        fps: int,
        quality: int,
        actual_width: int,
        actual_height: int,
        source_type: str,
        frame_counter: int,
        camera_location: str,
        read_time: float
    ):
        """Process frame and send to Redis asynchronously.

        Args:
            frame: Frame data
            stream_key: Stream identifier
            stream_group_key: Stream group identifier
            topic: Topic name
            source: Video source
            video_props: Video properties
            fps: Target FPS
            quality: JPEG quality
            actual_width: Frame width
            actual_height: Frame height
            source_type: Type of source
            frame_counter: Current frame number
            camera_location: Camera location
            read_time: Time taken to read frame
        """
        # Build metadata
        metadata = self.message_builder.build_frame_metadata(
            source, video_props, fps, quality, actual_width, actual_height,
            source_type, frame_counter, False, None, None, camera_location
        )
        metadata["feed_type"] = "disk" if source_type == "video_file" else "camera"
        metadata["frame_count"] = 1
        metadata["stream_unit"] = "frame"

        # Encode frame in process pool (CPU-bound)
        encoding_start = time.time()
        frame_data, codec = await self._encode_frame_async(frame, quality)
        encoding_time = time.time() - encoding_start
        metadata["encoding_type"] = "jpeg"

        # Get timing stats
        last_read, last_write, last_process = self.statistics.get_timing(stream_key)
        input_order = self.statistics.get_next_input_order(stream_key)

        # Build message
        message = self.message_builder.build_message(
            frame_data, stream_key, stream_group_key, codec, metadata, topic,
            self.stream_config.get('bootstrap_servers', 'localhost:9092'),
            input_order, last_read, last_write, last_process
        )

        # Send to Redis asynchronously
        write_start = time.time()
        await self.redis_client.add_message(topic, message)
        write_time = time.time() - write_start

        # Update statistics
        self.statistics.increment_frames_sent()
        process_time = read_time + write_time
        frame_size = len(frame_data) if frame_data else 0
        self.statistics.update_timing(stream_key, read_time, write_time, process_time, frame_size)

    async def _encode_frame_async(self, frame, quality: int) -> tuple:
        """Encode frame using thread pool asynchronously.

        Args:
            frame: Frame data
            quality: JPEG quality

        Returns:
            Tuple of (encoded_data, codec)
        """
        # Use asyncio.to_thread for encoding (threads work fine for OpenCV C code)
        encode_success, jpeg_buffer = await asyncio.to_thread(
            _encode_frame_worker,
            frame,
            quality
        )

        if encode_success:
            # ZERO-COPY: Use buffer directly
            frame_data = bytes(jpeg_buffer.data)
            return frame_data, "h264"
        else:
            # Fallback to raw
            frame_data = bytes(memoryview(frame).cast('B'))
            return frame_data, "h264"

    async def _shutdown(self):
        """Gracefully shutdown worker - cancel tasks and cleanup."""
        self.logger.info(f"Worker {self.worker_id}: Starting graceful shutdown")

        # Cancel all camera tasks
        for stream_key, task in self.camera_tasks.items():
            if not task.done():
                task.cancel()
                self.logger.info(f"Worker {self.worker_id}: Cancelled task for {stream_key}")

        # Wait for tasks to complete
        if self.camera_tasks:
            await asyncio.gather(*self.camera_tasks.values(), return_exceptions=True)

        # Release all captures
        for stream_key, cap in list(self.captures.items()):
            cap.release()
            self.logger.info(f"Worker {self.worker_id}: Released capture {stream_key}")
        self.captures.clear()

        # Close Redis client
        if self.redis_client:
            await self.redis_client.close()
            self.logger.info(f"Worker {self.worker_id}: Closed Redis client")

        # Report final health
        self._report_health("stopped")

        self.logger.info(f"Worker {self.worker_id}: Shutdown complete")

    def _report_health(self, status: str, active_cameras: int = 0, error: Optional[str] = None):
        """Report health status to main process.

        Args:
            status: Worker status (running, stopped, error)
            active_cameras: Number of active camera tasks
            error: Error message if status is error
        """
        try:
            health_report = {
                'worker_id': self.worker_id,
                'status': status,
                'active_cameras': active_cameras,
                'timestamp': time.time(),
                'error': error
            }
            self.health_queue.put_nowait(health_report)
        except Exception as exc:
            self.logger.warning(f"Worker {self.worker_id}: Failed to report health: {exc}")


def _encode_frame_worker(frame, quality: int):
    """Worker function for encoding frames in process pool.

    This runs in a separate process for true parallel execution.

    Args:
        frame: Frame data (numpy array)
        quality: JPEG quality

    Returns:
        Tuple of (success, encoded_buffer)
    """
    import cv2
    return cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])


def run_async_worker(
    worker_id: int,
    camera_configs: List[Dict[str, Any]],
    stream_config: Dict[str, Any],
    stop_event: multiprocessing.Event,
    health_queue: multiprocessing.Queue
):
    """Entry point for async worker process.

    This function is called by multiprocessing.Process to start a worker.

    Args:
        worker_id: Worker identifier
        camera_configs: List of camera configurations
        stream_config: Streaming configuration
        stop_event: Shutdown event
        health_queue: Health reporting queue
    """
    # Setup logging for this process
    logging.basicConfig(
        level=logging.INFO,
        format=f'%(asctime)s - Worker-{worker_id} - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(f"AsyncWorker-{worker_id}")
    logger.info(f"Starting async worker {worker_id}")

    try:
        # Create worker
        worker = AsyncCameraWorker(
            worker_id=worker_id,
            camera_configs=camera_configs,
            stream_config=stream_config,
            stop_event=stop_event,
            health_queue=health_queue
        )

        # Run event loop
        asyncio.run(worker.run())

    except Exception as exc:
        logger.error(f"Worker {worker_id} failed: {exc}", exc_info=True)
        raise
