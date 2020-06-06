import numpy as np
import cv2
import utilities as utlis
import time

class LaneDetection():
    def __init__(self):
        self.frameWidth = 640
        self.frameHeight = 480
        self.count = 0
        self.noOfArrayValues = 10
        self.arrayCounter = 0
        self.arrayCurve = np.zeros([self.noOfArrayValues])

    def laneDetect(self, img):
        img = cv2.resize(img, (self.frameWidth, self.frameHeight), None)

        imgUndis = utlis.undistort(img)
        img2, imgCanny, imgColor = utlis.thresholding(imgUndis)
        src = np.float32([(0.24, 0.55), (0.76, 0.55), (0.12, 1.0), (0.88, 1.0)])
        img2 = utlis.perspective_warp(img2, dst_size=(self.frameWidth, self.frameHeight), src=src)
        imgSliding, curves, lanes, ploty = utlis.sliding_window(img2, 5, draw_windows=False)

        try:
            curverad = utlis.get_curve(img, curves[0], curves[1])
            lane_curve = np.mean([curverad[0], curverad[1]])
            img = utlis.draw_lanes(img, curves[0], curves[1], self.frameWidth, self.frameHeight, src=src)
            # ## Average
            currentCurve = lane_curve // 50

            if int(np.sum(self.arrayCurve)) == 0:
                averageCurve = currentCurve
            else:
                averageCurve = np.sum(self.arrayCurve) // self.arrayCurve.shape[0]

            if abs(averageCurve - currentCurve) > 200:
                self.arrayCurve[self.arrayCounter] = averageCurve
            else:
                self.arrayCurve[self.arrayCounter] = currentCurve

            self.arrayCounter += 1

            if self.arrayCounter >= self.noOfArrayValues:
                self.arrayCounter = 0

            cv2.putText(img, str(int(averageCurve)), (self.frameWidth // 2 - 70, 70), cv2.FONT_HERSHEY_DUPLEX, 1.75,
                        (0, 0, 255), 2, cv2.LINE_AA)
            img = utlis.drawLines(img, lane_curve)
            return img, int(averageCurve)

        except Exception as ex:
            lane_curve = 00
            print(ex)
            pass
            img = utlis.drawLines(img, lane_curve)
            return img, 0

