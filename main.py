import threading
import time
from video_face_detector import VideoFaceDetector
from video_stream_server import VideoStreamServer

if __name__ == "__main__":
    frame_rate = 30  # Desired frame rate
    detector = VideoFaceDetector(scale_factor=0.5, buffer_size=10, frame_rate=frame_rate)
    server = VideoStreamServer(face_detector=detector)

    # Start a thread for frame updating
    def update_frames():
        while detector.running:
            start_time = time.time()
            detector.update_frame()
            elapsed_time = time.time() - start_time
            sleep_time = max(0, detector.frame_interval - elapsed_time)
            time.sleep(sleep_time)

    frame_thread = threading.Thread(target=update_frames)
    frame_thread.daemon = True
    frame_thread.start()

    try:
        server.run()
    finally:
        detector.release_resources()

