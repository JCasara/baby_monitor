import cv2
import face_recognition
import time

# Initialize the webcam (0 is the default device ID)
video_capture = cv2.VideoCapture(0)

if not video_capture.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Initialize variables to calculate FPS
fps = 0
frame_count = 0
start_time = time.time()


scale_factor = 0.5  # Adjust this scale factor as needed

while True:
    # Capture a single frame from the video stream
    ret, frame = video_capture.read()

    if not ret:
        print("Error: Failed to capture image.")
        break

    # Convert the frame from BGR (OpenCV format) to RGB (face_recognition format)
    small_frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    # rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # # Find all face locations in the frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_locations = [(int(top / scale_factor), int(right / scale_factor),
                       int(bottom / scale_factor), int(left / scale_factor))
                      for (top, right, bottom, left) in face_locations]

    # Draw bounding boxes around detected faces
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, 'Face', (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Calculate the current FPS
    frame_count += 1
    elapsed_time = time.time() - start_time
    if elapsed_time > 0:
        fps = frame_count / elapsed_time

    # Display the FPS on the frame
    fps_text = f"FPS: {fps:.2f}"
    cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Display the resulting frame
    cv2.imshow('Video', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close the window
video_capture.release()
cv2.destroyAllWindows()

