import cv2
import time
import numpy as np
import HandModule as htm
import math
# Importing pycaw file
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

########################
wCam, hcam = 640, 580
########################


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()

minVol = volRange[0]
maxVol = volRange[1]

vol=0
volBar = 300
volPer = 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(3, wCam)
cap.set(4, hcam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7)

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) !=0:
        #print(lmList[4], lmList[8]) # Thumb_tip and index_finger_tip

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        # creating center from index to thumb
        cx, cy = (x1+x2)//2, (y1+y2)//2

    # circle around index and thumb
        cv2.circle(img, (x1, y1), 5, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 5, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

        # doing math on line
        length = math.hypot(x2-x1, y2-y1)
        print(length)

        # Hand range 50-300, hence convert it to volume range i.e -65 - 0
        vol = np.interp(length, [50,300], [minVol, maxVol])
        volBar = np.interp(length, [50, 300], [300, 100])
        volPer = np.interp(length, [50, 300], [0,100])
        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length <= 50:
            cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)

    # creating a a volume bar
    cv2.rectangle(img, (50,100), (85, 300),(0,255,0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 300), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'Volume:{int(volPer)} %', (40, 350), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img,f'FPS:{int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    cv2.imshow("img", img)
    cv2.waitKey(1)
