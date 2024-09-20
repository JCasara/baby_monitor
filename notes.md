# Auto Exposure will affect frame rate
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)

User Controls
                     brightness 0x00980900 (int)    : min=0 max=255 step=1 default=128 value=128
                       contrast 0x00980901 (int)    : min=0 max=255 step=1 default=32 value=32
                     saturation 0x00980902 (int)    : min=0 max=100 step=1 default=64 value=64
                            hue 0x00980903 (int)    : min=-2000 max=2000 step=1 default=0 value=0
        white_balance_automatic 0x0098090c (bool)   : default=1 value=0
                          gamma 0x00980910 (int)    : min=90 max=150 step=1 default=120 value=120
                           gain 0x00980913 (int)    : min=4 max=8 step=1 default=4 value=4
           power_line_frequency 0x00980918 (menu)   : min=0 max=3 default=1 value=1 (50 Hz)
      white_balance_temperature 0x0098091a (int)    : min=2800 max=6500 step=1 default=4600 value=4600
                      sharpness 0x0098091b (int)    : min=1 max=7 step=1 default=2 value=2
         backlight_compensation 0x0098091c (int)    : min=0 max=2 step=1 default=0 value=0

Camera Controls
                  auto_exposure 0x009a0901 (menu)   : min=0 max=3 default=3 value=3 (Aperture Priority Mode)
         exposure_time_absolute 0x009a0902 (int)    : min=3 max=2500 step=1 default=156 value=156 flags=inactive
     exposure_dynamic_framerate 0x009a0903 (bool)   : default=0 value=1

# User Controls
cap.set(cv2.CAP_PROP_BRIGHTNESS, 128)                # Brightness
cap.set(cv2.CAP_PROP_CONTRAST, 32)                   # Contrast
cap.set(cv2.CAP_PROP_SATURATION, 64)                 # Saturation
cap.set(cv2.CAP_PROP_HUE, 0)                          # Hue
cap.set(cv2.CAP_PROP_AUTO_WB, 0)                     # White balance automatic (0 = off)
cap.set(cv2.CAP_PROP_GAMMA, 120)                      # Gamma
cap.set(cv2.CAP_PROP_GAIN, 8)                         # Gain
cap.set(cv2.CAP_PROP_POWER_LINE_FREQUENCY, 1)        # Power line frequency (1 = 50Hz)
cap.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, 4600)     # White balance temperature
cap.set(cv2.CAP_PROP_SHARPNESS, 2)                    # Sharpness
cap.set(cv2.CAP_PROP_BACKLIGHT, 0)                    # Backlight compensation

# Camera Controls
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)                # Auto exposure (1 = manual mode)
cap.set(cv2.CAP_PROP_EXPOSURE, 156)                    # Exposure time absolute
cap.set(cv2.CAP_PROP_EXPOSURE_DYNAMIC_FRAMERATE, 1)   # Exposure dynamic framerate (0 = off)

