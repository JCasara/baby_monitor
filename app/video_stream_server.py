from flask import Flask, Response, redirect, render_template, request, url_for


class VideoStreamServer:
    def __init__(self, server_config, face_detector):
        self.app = Flask(__name__, template_folder='../templates')
        self.server_config = server_config
        self.face_detector = face_detector
        self.app.add_url_rule('/video_feed', 'video_feed', self.video_feed)
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/update_threshold', 'update_threshold', self.update_threshold, methods=['POST'])

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

    def index(self):
        """Render the main page with the threshold form."""
        return render_template('index.html', current_threshold=self.face_detector.state_manager.max_no_face_count)
    
    def update_threshold(self):
        """Update the frame count threshold."""
        try:
            new_threshold = int(request.form['threshold'])
            self.face_detector.state_manager.max_no_face_count = new_threshold
        except ValueError:
            pass
        return redirect(url_for('index'))
    
    def run(self):
        """Run the Flask server."""
        self.app.run(host=self.server_config['host'], port=self.server_config['port'], debug=False, threaded=True, use_reloader=False)
