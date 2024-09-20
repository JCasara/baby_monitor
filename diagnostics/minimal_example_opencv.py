import time

import cv2
from numpy import who

# Initialize the video capture object (0 for the default webcam)
cap = cv2.VideoCapture(0)

# Set the camera frame rate and dimensions
frame_width = 640
frame_height = 480
frame_rate = 30  # Frames per second
FOURCC = 'MJPG'
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*FOURCC))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
cap.set(cv2.CAP_PROP_FPS, frame_rate)
# cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)  # Manual exposure
# cap.set(cv2.CAP_PROP_GAIN, 120)  # Fixed gain
# cap.set(cv2.CAP_PROP_AUTO_WB, 0)  # Disable auto white balance

# User Controls
cap.set(cv2.CAP_PROP_BRIGHTNESS, 128)                # Brightness
cap.set(cv2.CAP_PROP_CONTRAST, 32)                   # Contrast
cap.set(cv2.CAP_PROP_SATURATION, 64)                 # Saturation
cap.set(cv2.CAP_PROP_HUE, 0)                          # Hue
cap.set(cv2.CAP_PROP_AUTO_WB, 0)                     # White balance automatic (0 = off)
cap.set(cv2.CAP_PROP_GAMMA, 150)                      # Gamma
cap.set(cv2.CAP_PROP_GAIN, 8)                         # Gain
cap.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, 4600)     # White balance temperature
cap.set(cv2.CAP_PROP_SHARPNESS, 2)                    # Sharpness
cap.set(cv2.CAP_PROP_BACKLIGHT, 0)                    # Backlight compensation

# Camera Controls
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)                # Auto exposure (1 = manual mode)
cap.set(cv2.CAP_PROP_EXPOSURE, 333)                    # Exposure time absolute

print("Width:", cap.get(cv2.CAP_PROP_FRAME_WIDTH))
print("Height:", cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("FPS (Set):", cap.get(cv2.CAP_PROP_FPS))
print("FOURCC:", cap.get(cv2.CAP_PROP_FOURCC))
print("FOURCC SETTING:", cv2.VideoWriter_fourcc(*FOURCC))

# Function to display the video feed
def display_video():
    fps_frame_count = 0
    last_time = time.time()
    fps = 0

    while True:
        start_reading = time.time()
        success, frame = cap.read()
        read_time = time.time() - start_reading
        print(f"Read time: {read_time:.4f} seconds")

        if not success:
            break

        fps_frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - last_time
        
        if elapsed_time > 1.0:
            fps = fps_frame_count / elapsed_time
            last_time = current_time
            fps_frame_count = 0

        # Display FPS on the frame
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Show the frame in a window
        cv2.imshow("Video Feed", frame)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture object and close the window
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    display_video()
