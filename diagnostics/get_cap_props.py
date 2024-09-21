import cv2

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)                # Auto exposure (1 = manual mode)
cap_prop = {key: value for key, value in cv2.__dict__.items() if key.startswith('CAP_PROP_')}

for key, value in cap_prop.items():
    print(f"{key} = {cap.get(value)}")
