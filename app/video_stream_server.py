import asyncio
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


class VideoStreamServer:
    def __init__(self, server_config, face_detector):
        self.app = FastAPI()
        self.server_config = server_config
        self.face_detector = face_detector
        self.templates = Jinja2Templates(directory="templates")
        self.app.mount('/static', StaticFiles(directory='static'), name='static')

        self.app.add_api_route("/video_feed", self.video_feed)
        self.app.add_api_route("/", self.index, methods=["GET"])
        self.app.add_api_route("/update_threshold", self.update_threshold, methods=["POST"])

    async def generate_frames(self):
        """Generate video frames for streaming."""
        while self.face_detector.running:
            frame = self.face_detector.get_frame()
            if frame is None:
                continue
            await asyncio.sleep(0.1)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    async def video_feed(self):
        """Route to display the video stream."""
        return StreamingResponse(self.generate_frames(),
                                 media_type='multipart/x-mixed-replace; boundary=frame')

    async def index(self, request: Request):
        """Render the main page with the threshold form."""
        return self.templates.TemplateResponse("index.html",
                                               {"request": request,
                                                "current_threshold": self.face_detector.state_manager.max_no_face_count})

    async def update_threshold(self, threshold: int = Form(...)):
        """Update the frame count threshold."""
        try:
            self.face_detector.state_manager.max_no_face_count = threshold
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid threshold value")
        return RedirectResponse(url='/', status_code=303)

    def run(self):
        """Run the FastAPI server."""
        import uvicorn
        print(self.server_config)
        uvicorn.run(self.app, host=self.server_config['host'], port=self.server_config['port'], log_level="info")
