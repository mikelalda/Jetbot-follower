import argparse
import socket
import jetson.inference
import jetson.utils
import additionals.globals as gv

import urllib.request
import http
import numpy as np
import cv2
from jetbot import Robot

base = "http://192.168.1.107/" # Arduino prints the IP of the ESP8266


def transfer(my_url):   #use to send and receive data
    try:
        n = urllib.request.urlopen(base + my_url).read()
        n = n.decode("utf-8")
        return n

    except http.client.HTTPException as e:
        print(e)
        return e

def detection_center(detection):
    """Computes the center x, y coordinates of the object"""
    bbox = detection['bbox']
    center_x = (bbox[0] + bbox[2]) / 2.0 - 0.5
    center_y = (bbox[1] + bbox[3]) / 2.0 - 0.5
    return (center_x, center_y)

net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)
camera = jetson.utils.videoSource("/dev/video0")      # '/dev/video0' for V4L2 and 'csi://0' for csi
display = jetson.utils.videoOutput("display://0") # 'my_video.mp4' for file
render_img = False
robot = Robot()

speed = 0.5
turn_gain = 0.8

names = ['person']

def main():

    while True:
        img = camera.Capture()
        height, width, channels = img.shape
        detections = net.Detect(img)
        if render_img:
            display.Render(img)
            display.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))
        for detection in detections:
            class_id = names[detection.ClassID]
            x1 = detection.Left/width 
            y1 = detection.Top/height
            x2 = detection.Right/width
            y2 = detection.Bottom/height
            if class_id in gv.DETECTIONS:
                color = transfer("")
                # Si la persona detectada tiene algo verde
                if color == "1":
                    check = True
                    lower = np.array([0, 0, 0], np.uint8)
                    upper = np.array([180, 255, 200], np.uint8)
                # Si la persona detectada tiene algo rojo
                elif color == "2":
                    check = True
                    lower = np.array([0, 0, 0], np.uint8)
                    upper = np.array([180, 255, 200], np.uint8)
                # Si la persona detectada tiene algo azul
                elif color == "3":
                    check = True
                    lower = np.array([0, 0, 0], np.uint8)
                    upper = np.array([180, 255, 200], np.uint8)
                    
                else:
                    check = False

            if check:
                cropped_img = img[y1:y2, x1:x2,:]
                hsv = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(hsv, lower, upper)
                unique_counts = dict(zip(np.unique(mask, return_counts=True)))
                if unique_counts['0'] >= 30:
                    center = detection_center(detection)
                    robot.set_motors(
                        float(speed + turn_gain * center[0]),
                        float(speed - turn_gain * center[0])
                    )


                    
            
    
if __name__ == '__main__':
    main()
