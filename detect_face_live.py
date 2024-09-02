import cv2
import face_recognition
import time

class VideoFaceDetector:
    def __init__(self, scale_factor=0.5):
        # Initialize the webcam
        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            raise Exception("Error: Could not open webcam.")
        
        self.scale_factor = scale_factor
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
    
    def _resize_frame(self, frame):
        """Resize the frame to improve processing speed."""
        return cv2.resize(frame, (0, 0), fx=self.scale_factor, fy=self.scale_factor)
    
    def _detect_faces(self, rgb_frame):
        """Detect faces in the frame using face_recognition."""
        face_locations = face_recognition.face_locations(rgb_frame)
        # Scale back bounding boxes to the original frame size
        return [(int(top / self.scale_factor), int(right / self.scale_factor),
                 int(bottom / self.scale_factor), int(left / self.scale_factor))
                for (top, right, bottom, left) in face_locations]
    
    def _calculate_fps(self):
        """Calculate and update the FPS."""
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            self.fps = self.frame_count / elapsed_time
    
    def _draw_face_boxes(self, frame, face_locations):
        """Draw bounding boxes around detected faces."""
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, 'Face', (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    def _display_fps(self, frame):
        """Display FPS on the frame."""
        fps_text = f"FPS: {self.fps:.2f}"
        cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    
    def run(self):
        """Run the video stream and face detection."""
        while True:
            ret, frame = self.video_capture.read()
            if not ret:
                print("Error: Failed to capture image.")
                break
            
            # Resize the frame
            small_frame = self._resize_frame(frame)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = self._detect_faces(rgb_small_frame)
            
            # Draw bounding boxes and FPS
            self._draw_face_boxes(frame, face_locations)
            self._calculate_fps()
            self._display_fps(frame)
            
            # Show the frame
            cv2.imshow('Video', frame)
            
            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Release resources
        self.video_capture.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = VideoFaceDetector(scale_factor=0.5)
    detector.run()
