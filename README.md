# Baby Monitor is a program that uses your webcam to detect people and more specifically their face. The main purpose is to act as a baby monitor that will send your phone a push notification in the event that your baby rolls over or something covers their face.

# Running the program
Execute the following command
```bash
pip install -r requirements.txt
```

Then you can run the `main.py` script
```bash
python main.py
```

This will start streaming the video feed to the following URL
```
http://localhost:8080/
```

# Considerations
I built this application as a pet project to play around with writing well structured code. I know that this code is not very "Pythonic", but it is very modular and tries to follow SOLID principles.
