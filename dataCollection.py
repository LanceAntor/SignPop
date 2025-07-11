import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
import time

cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1)

offset = 20
imageSize = 300

folder = "Data/Z"
counter = 0

while True:
    success, img = cap.read()
    hands,img = detector.findHands(img)

    if hands:
        hand = hands[0]
        x, y, w, h = hand['bbox']

        imgWhite = np.ones((imageSize, imageSize, 3), np.uint8) * 255
        imgCrop = img[y - offset:y + h + offset, x - offset: x + w + offset]

        imgCropShape = imgCrop.shape

        aspecRatio = h / w 

        if aspecRatio > 1:
            k = imageSize / h
            wCal = math.ceil(k * w)
            imgResize = cv2.resize(imgCrop, (wCal, imageSize))
            imgResizeShape = imgResize.shape
            wGap = math.ceil((imageSize - wCal) / 2)
            imgWhite[:, wGap:wCal+wGap] = imgResize
        else:
            k = imageSize / w
            hCal = math.ceil(k * h)
            imgResize = cv2.resize(imgCrop, (imageSize, hCal))
            imgResizeShape = imgResize.shape
            hGap = math.ceil((imageSize - hCal) / 2)
            imgWhite[hGap:hCal +hGap, :] = imgResize


        cv2.imshow("Cropped Image", imgCrop)
        cv2.imshow("White Image", imgWhite)


    cv2.imshow("Image", img)
    cv2.waitKey(1)

    # For saving images

    key = cv2.waitKey(1) 
    if key == ord("s"):
        counter += 1
        cv2.imwrite(f"{folder}/Image_{time.time()}.jpg", imgWhite)
        print(counter)