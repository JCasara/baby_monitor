from flask import Flask, Response
from video_face_detector import VideoFaceDetector

class VideoStreamServer:
    def __init__(self, face_detector):
        self.app = Flask(__name__)
        self.face_detector = face_detector
        self.app.add_url_rule('/video_feed', 'video_feed', self.video_feed)
    
    def generate_frames(self):
        """Generate video frames for streaming."""
        while self.face_detector.running:
            frame = self.face_detector.get_frame()
            if frame is None:
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    def video_feed(self):
        """Route to display the video stream."""
        return Response(self.generate_frames(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    def run(self):
        """Run the Flask server."""
        self.app.run(host='0.0.0.0', port=8080, debug=False, threaded=True, use_reloader=False)

