import asyncio
from typing import Any, AsyncGenerator, Coroutine, Optional

import cv2
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.interfaces.camera_interface import CameraInterface
from app.interfaces.server_interface import ServerInterface
from app.interfaces.state_manager_interface import StateManagerInterface


class ServerService(ServerInterface):
    def __init__(self, config: dict, camera_service: CameraInterface, state_manager: StateManagerInterface):
        self.app = FastAPI()
        self.server_config: dict = config['server']
        self.video_config: dict = config['video']
        self.frame_rate: Optional[int] = self.video_config.get('frame_rate', 30)
        self.camera_service: CameraInterface = camera_service
        self.state_manager: StateManagerInterface = state_manager
        self.templates: Jinja2Templates = Jinja2Templates(directory="templates")
        self.app.mount('/static', StaticFiles(directory='static'), name='static')

        self.app.add_api_route("/video_feed", self.video_feed)
        self.app.add_api_route("/", self.index, methods=["GET"])
        self.app.add_api_route("/update_threshold", self.update_threshold, methods=["POST"])

    async def generate_frames(self) -> AsyncGenerator[bytes, Any]:
        """Generate a frame for the video server."""
        while self.camera_service.running:
            frame = await asyncio.to_thread(self.camera_service.get_frame)
            # frame = self.camera_service.get_frame()
            if frame is None:
                continue
            ret, encoded_data = cv2.imencode('.jpg', frame)
            if ret:
                byte_data = encoded_data.tobytes()
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + byte_data + b'\r\n')
            await asyncio.sleep(0.01)

    async def video_feed(self) -> StreamingResponse:
        """Video feed page of the server."""
        async_gen = self.generate_frames()
        return StreamingResponse(async_gen,
                                 media_type='multipart/x-mixed-replace; boundary=frame')

    async def index(self, request: Request) -> HTMLResponse:
        """Main page of server."""
        return self.templates.TemplateResponse("index.html",
                                               {"request": request,
                                                "image_width": self.video_config.get('image_width', 640),
                                                "image_height": self.video_config.get('image_height', 480),
                                                "current_threshold": self.state_manager.max_no_face_count})

    async def update_threshold(self, threshold: int = Form(...)) -> RedirectResponse:
        """Updates the notification threshold (number of frames) for detections."""
        # Calculate bounds based on frame_rate
        min_threshold: int = self.frame_rate * 1 if self.frame_rate else 5 # Minimum of 1 second
        max_threshold: int = self.frame_rate * 20 if self.frame_rate else 100 # Maximum of 20 seconds

        # Ensure the threshold is within bounds
        if threshold < min_threshold or threshold > max_threshold:
            raise HTTPException(status_code=400, detail=f"Threshold must be between {min_threshold} and {max_threshold} frames.")

        try:
            self.state_manager.max_no_face_count = threshold
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid threshold value")

        return RedirectResponse(url='/', status_code=303)

    def run(self) -> None:
        """Runs the FastAPI server with uvicorn."""
        import uvicorn
        uvicorn.run(self.app, host=self.server_config['host'], port=self.server_config['port'], log_level="info", timeout_keep_alive=5, timeout_graceful_shutdown=5)
