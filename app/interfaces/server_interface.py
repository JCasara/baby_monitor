from abc import ABC, abstractmethod
from typing import Any, Generator

import numpy as np
from fastapi import Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse


class ServerInterface(ABC):
    @abstractmethod
    async def video_feed(self) -> StreamingResponse:
        """Video feed page of server."""
        pass

    @abstractmethod
    async def index(self, request: Request) -> HTMLResponse:
        """Main page of server."""
        pass
        
    @abstractmethod
    async def update_threshold(self, threshold: int = Form(...)) -> RedirectResponse:
        """Calculate notification threshold bounds."""
        pass

    @abstractmethod
    def generate_frames(self, source) -> Generator[Any, Any, Any]:
        """Generate a frame for the video server."""
        pass

    @abstractmethod
    def get_frame(self, source) -> None | np.ndarray:
        """Get frame from frame_bufer."""
        pass

    @abstractmethod
    def run(self) -> None:
        """Run video server."""
        pass
