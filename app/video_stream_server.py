import asyncio

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .interfaces.camera_interface import CameraInterface
from .interfaces.state_manager_interface import StateManagerInterface
from .interfaces.video_stream_server_interface import \
    VideoStreamServerInterface


class VideoStreamServer(VideoStreamServerInterface):
    def __init__(self, config, face_detector: CameraInterface, state_manager: StateManagerInterface):
        self.app = FastAPI()
        self.server_config = config['server']
        self.video_config = config['video']
        self.face_detector = face_detector
        self.state_manager = state_manager
        self.templates = Jinja2Templates(directory="templates")
        self.app.mount('/static', StaticFiles(directory='static'), name='static')

        self.app.add_api_route("/video_feed", self.video_feed)
        self.app.add_api_route("/", self.index, methods=["GET"])
        self.app.add_api_route("/update_threshold", self.update_threshold, methods=["POST"])

    async def generate_frames(self):
        while self.face_detector.running:
            frame = self.face_detector.get_frame()
            if frame is None:
                continue
            await asyncio.sleep(0.1)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    async def video_feed(self):
        return StreamingResponse(self.generate_frames(),
                                 media_type='multipart/x-mixed-replace; boundary=frame')

    async def index(self, request: Request):
        return self.templates.TemplateResponse("index.html",
                                               {"request": request,
                                                "image_width": self.video_config.get('image_width', 640),
                                                "image_height": self.video_config.get('image_height', 480),
                                                "current_threshold": self.state_manager.max_no_face_count})

    async def update_threshold(self, threshold: int = Form(...)):
        try:
            self.state_manager.max_no_face_count = threshold
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid threshold value")
        return RedirectResponse(url='/', status_code=303)

    def run(self):
        import uvicorn
        uvicorn.run(self.app, host=self.server_config['host'], port=self.server_config['port'], log_level="info", timeout_keep_alive=5, timeout_graceful_shutdown=5)
