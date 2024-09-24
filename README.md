# Baby Monitor
This is a program that uses your webcam to detect people and more specifically their face. The main purpose is to act as a baby monitor that will send your phone a push notification in the event that your baby rolls over or something covers their face.

# Setup
Execute the following command to install the python libraries needed for this project.
```bash
pip install -r requirements.txt
```
Next, you will need to have a Pushover account, which you can setup by going to their website and signing up. https://pushover.net/

Lastly, you will want to copy the default_config.yaml and add your Pushover USER_KEY and API_TOKEN, if you want to enable the push notifications.
The file config/config.yaml is in the .gitignore, so your private USER_KEY and API_TOKEN will not be git tracked.
```bash
cp config/default_config.yaml config/config.yaml
```

# Running the program
Then you can run the `main.py` script
```bash
python main.py
```

This will start streaming the video feed to the following URL
```
http://localhost:8080/
```

# Discussion
As far as a pet project goes, this one was pretty fun and I was able to kill two birds with one stone, so-to-speak, since this application actually serves the purpose of a baby monitor for my newborn baby girl. I think I spent the most time playing around with the ffmpeg_camera_service, and ultimately have not gotten it to work quite yet. The reason I even attempted to use FFMPEG, as opposed to the current OpenCV camera service, is because I was experiencing some latency issues as well as a frame rate bottleneck of around 16.67fps. I spent a lot of time debugging the code in the terminal with direct FFMPEG commands to see if it was network issues or just driver-related issues. It turns out that, in the end, it was actually the camera settings themself that were causing the bottleneck. Most specifically, the auto exposure setting for the camera was setting too high of an exposure time to compensate for my dimly lit office environment. Once I manually set the exposure time to a value that was less than 0.0333seconds (the limit for 30fps), I was able to see the frame rate jump back up to the desired value. I also prototyped the build with Flask before migrating to FastAPI for serving the video stream to the browser. All-in-all, this was a fun project and I learned a lot about streaming HD video from a webcam to the browser, as well as implementing some out-of-the-box computer vision techniques like person (using YOLOv5) and face detection (using the face_recognition library, which uses dlib under the hood), and lastly I got to play around with sending push notifications to my iPhone through the Pushover API.

# Considerations
I built this application as a pet project to play around with writing well structured code. I know that this code is not very "Pythonic", but it is very modular and tries to follow SOLID principles.

# Future Work
I still plan on playing around with this code a bit more. 

Some features I would like to add are: 
* A more interactive user interface for the web app
* Ability to control the camera settings through the FastAPI interface
