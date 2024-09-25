from typing import Any, Generator

import numpy as np
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.interfaces.camera_interface import CameraInterface
from app.interfaces.detector_interface import DetectorInterface
from app.interfaces.server_interface import ServerInterface
from app.interfaces.state_manager_interface import StateManagerInterface
from app.utils.opencv_utils import encode_image


class ServerService(ServerInterface):
    def __init__(self, config: dict, camera_service: CameraInterface, state_manager_service: StateManagerInterface, detector_service: DetectorInterface):
        self.app = FastAPI()
        self.camera_service: CameraInterface = camera_service
        self.state_manager_service: StateManagerInterface = state_manager_service
        self.detector_service: DetectorInterface = detector_service
        self.server_config: dict = config['server']
        self.video_config: dict = config['video']
        self.frame_rate: int = self.camera_service.frame_rate
        self.templates: Jinja2Templates = Jinja2Templates(directory="templates")
        self.app.mount('/static', StaticFiles(directory='static'), name='static')

        self.app.add_api_route("/video_feed", self.video_feed)
        self.app.add_api_route("/", self.index, methods=["GET"])
        self.app.add_api_route("/update_threshold", self.update_threshold, methods=["POST"])

        self.running = True

    async def video_feed(self) -> StreamingResponse:
        """Video feed page of the server."""
        return StreamingResponse(self.serve_frame(),
                                 media_type='multipart/x-mixed-replace; boundary=frame')

    async def index(self, request: Request) -> HTMLResponse:
        """Main page of server."""
        return self.templates.TemplateResponse("index.html",
                                               {"request": request,
                                                "image_width": self.video_config.get('image_width', 640),
                                                "image_height": self.video_config.get('image_height', 480),
                                                "current_threshold": self.state_manager_service.max_no_face_count})

    async def update_threshold(self, threshold: int = Form(...)) -> RedirectResponse:
        """Updates the notification threshold (number of frames) for detections."""
        # Calculate bounds based on frame_rate
        min_threshold: int = self.frame_rate * 1 if self.frame_rate else 5 # Minimum of 1 second
        max_threshold: int = self.frame_rate * 20 if self.frame_rate else 100 # Maximum of 20 seconds

        # Ensure the threshold is within bounds
        if threshold < min_threshold or threshold > max_threshold:
            raise HTTPException(status_code=400, detail=f"Threshold must be between {min_threshold} and {max_threshold} frames.")

        try:
            self.state_manager_service.max_no_face_count = threshold
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid threshold value")

        return RedirectResponse(url='/', status_code=303)

    async def serve_frame(self) -> Generator[Any, Any, Any]:
        """Serve a frame to the video server."""
        while self.running:
            frame = await self.detector_service.process_frame()
            if frame.size == 0:
                continue
            ret, encoded_data = encode_image(frame)
            if ret:
                byte_data = encoded_data.tobytes()
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + byte_data + b'\r\n')

    def run(self) -> None:
        """Runs the FastAPI server with uvicorn."""
        import uvicorn
        uvicorn.run(self.app, host=self.server_config['host'], port=self.server_config['port'], log_level="info", timeout_keep_alive=5, timeout_graceful_shutdown=5)
