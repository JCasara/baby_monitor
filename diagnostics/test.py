import subprocess

def display_webcam_video():
    # Command to capture video from the webcam and display it using ffplay

    command = [
        'ffmpeg',
        '-f', 'v4l2',          # Use the Video4Linux2 input format (for Linux)
        '-framerate', '30',
        '-video_size', '648x480',
        '-i', '/dev/video0',   # Input device (change if necessary)
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-tune', 'zerolatency',
        '-f', 'mpegts',
        'pipe:1'               # Output to stdout
    ]

    # Start the ffmpeg process
    ffmpeg_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Command to play the output using ffplay
    play_command = ['ffplay', '-fflags', 'nobuffer', '-flags', 'low_delay', '-strict', '-2', 'pipe:0']

    # Start ffplay to display the video
    play_process = subprocess.Popen(play_command, stdin=ffmpeg_process.stdout, stderr=subprocess.PIPE)

    try:
        # Wait for the ffplay process to complete
        play_process.wait()
    except KeyboardInterrupt:
        # Terminate the processes on interrupt
        ffmpeg_process.terminate()
        play_process.terminate()

if __name__ == "__main__":
    display_webcam_video()

