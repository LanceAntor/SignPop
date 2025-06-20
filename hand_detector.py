import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import math
import os

class HandSignDetector:
    def __init__(self, model_path, labels_path):
        # Initialize hand detector
        self.detector = HandDetector(maxHands=1)
        
        # Load the classifier
        self.classifier = Classifier(model_path, labels_path)
        
        # Load labels
        self.labels = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
                      "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", 
                      "U", "V", "W", "X", "Y", "Z"]
        
        self.imageSize = 300
        self.offset = 20
        
    def detect_hand_sign(self, img):
        """
        Detects hand signs in the image and returns the predicted label, confidence,
        and processed images for debugging.
        """
        imgOutput = img.copy()
        
        # Find hands
        hands, img = self.detector.findHands(img)
        
        if not hands:
            return None, 0, imgOutput, None
        
        # Process the first detected hand
        hand = hands[0]
        x, y, w, h = hand['bbox']
        
        # Create white background image
        imgWhite = np.ones((self.imageSize, self.imageSize, 3), np.uint8) * 255
        
        # Crop the hand region with offset
        try:
            imgCrop = img[max(0, y-self.offset):min(img.shape[0], y+h+self.offset), 
                         max(0, x-self.offset):min(img.shape[1], x+w+self.offset)]
            
            # Check if the crop is valid
            if imgCrop.size == 0:
                return None, 0, imgOutput, None
                
            # Calculate aspect ratio of the cropped image
            aspectRatio = h/w
            
            # Resize and position on white image based on aspect ratio
            if aspectRatio > 1:
                k = self.imageSize / h
                wCal = math.ceil(k * w)
                imgResize = cv2.resize(imgCrop, (wCal, self.imageSize))
                wGap = math.ceil((self.imageSize - wCal) / 2)
                imgWhite[:, wGap:wCal+wGap] = imgResize
                prediction, index = self.classifier.getPrediction(imgWhite, draw=False)
            else:
                k = self.imageSize / w
                hCal = math.ceil(k * h)
                imgResize = cv2.resize(imgCrop, (self.imageSize, hCal))
                hGap = math.ceil((self.imageSize - hCal) / 2)
                imgWhite[hGap:hCal+hGap, :] = imgResize
                prediction, index = self.classifier.getPrediction(imgWhite, draw=False)
            
            confidence = float(prediction[index]) * 100  # Convert to percentage
            predicted_label = self.labels[index]
            
            # Draw on output image just like in your code
            cv2.rectangle(imgOutput, (x-self.offset, y-self.offset-50), 
                         (x-self.offset + 90, y-self.offset-50+ 50), (255, 0, 255), cv2.FILLED)
            cv2.putText(imgOutput, predicted_label, (x, y - 26), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.7, (255, 255, 255), 2)
            cv2.rectangle(imgOutput, (x-self.offset, y-self.offset), 
                         (x + w+self.offset, y + h+self.offset), (255, 0, 255), 4)
            
            # Add confidence display
            conf_text = f"{confidence:.1f}%"
            conf_width = cv2.getTextSize(conf_text, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 1)[0][0]
            cv2.putText(imgOutput, conf_text, (x + 30, y - 26 + 45), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 1)
            
            return predicted_label, confidence, imgOutput, imgWhite
            
        except Exception as e:
            print(f"Error in hand sign detection: {e}")
            return None, 0, imgOutput, None