
import cv2
import sys
import math
import numpy as np
 

def hsv_filter(img):
    hsv= cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_thre = np.array([20, 10, 100], dtype="uint8")
    upper_thre = np.array([30, 255, 255], dtype="uint8")
    mask1 = cv2.inRange(hsv, lower_thre, upper_thre)
    #mask1 = cv2.inRange(hsv,np.array([0,70,50]),np.array([10,255,255]))
    #mask2 = cv2.inRange(hsv, np.array([170,70,50]), np.array([180,255,255]))
    mask2 = cv2.inRange(img, 200, 255)
    #mask = mask1|mask2
    mask = cv2.bitwise_or(mask2, mask1)
    res = cv2.bitwise_and(img, img, mask=mask)
    return res

def gaussian_blur(img):
    kernel_size = 5
    gauss_gray = cv2.GaussianBlur(img, kernel_size)

def ROI(img):
    img_h = img.shape[0]
    img_w = img.shape[1]
    region = np.array([[(-0.4*img_w,0.9*img_h),(1.4*img_w,0.9*img_h),(0.65*img_w, 0.5*img_h),(0.4*img_w, 0.5*img_h)]], dtype = np.int32)
    mask = np.zeros_like(img)
    cv2.fillPoly(mask,region,(255,255,255))
    masked_img = cv2.bitwise_and(img,mask)
    return masked_img

def ROI2(img):
    img_h = img.shape[0]
    img_w = img.shape[1]

    region = np.array([[(-0.3*img_w,0.85*img_h),(0.82*img_w,0.85*img_h),(0.5*img_w, 0.52*img_h)]], dtype = np.int32)

    mask = np.zeros_like(img)
    cv2.fillPoly(mask,region,(255,255,255))
    masked_img = cv2.bitwise_and(img,mask)
    return masked_img


def bev(img):
    IMAGE_H = img.shape[0]
    IMAGE_W = img.shape[1]
    src = np.float32([[0, IMAGE_H], [IMAGE_W, IMAGE_H], [0.6*IMAGE_W, 0.5*IMAGE_H], [0.4*IMAGE_W, 0.5*IMAGE_H]]) #좌하우하우상좌상
    dst = np.float32([[0.46*IMAGE_W, IMAGE_H], [0.54*IMAGE_W, IMAGE_H], [0.6*IMAGE_W, 0.5*IMAGE_H], [0.4*IMAGE_W, 0.5*IMAGE_H]])
    M = cv2.getPerspectiveTransform(src, dst) # The transformation matrix
    warped_img = cv2.warpPerspective(img, M, (IMAGE_W, IMAGE_H))
    return warped_img


def bev_inv(img):
    IMAGE_H = img.shape[0]
    IMAGE_W = img.shape[1]
    src = np.float32([[0, IMAGE_H], [IMAGE_W, IMAGE_H], [0.6 * IMAGE_W, 0.5 * IMAGE_H], [0.4 * IMAGE_W, 0.5 * IMAGE_H]])  # 좌하우하우상좌상
    dst = np.float32([[0.46 * IMAGE_W, IMAGE_H], [0.54 * IMAGE_W, IMAGE_H], [0.6 * IMAGE_W, 0.5 * IMAGE_H],[0.4 * IMAGE_W, 0.5 * IMAGE_H]])
    Minv = cv2.getPerspectiveTransform(dst, src) # Inverse transformation
    inversed_img = cv2.warpPerspective(img, Minv, (IMAGE_W, IMAGE_H))
    return inversed_img

# Used by GUI.py
def linedetection(img):
    img2 = ROI(img)
    img2 = bev(img2)

    #src = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    src = hsv_filter(img)
    canny = cv2.Canny(src, 100, 200, None, 3)

    linesP = cv2.HoughLinesP(canny, 1, np.pi/180, 50, None, 20, 6)

    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            cv2.line(img2, (l[0], l[1]), (l[2], l[3]), (0, 0, 255), 3, cv2.LINE_AA)
    final = bev_inv(img2)
    final = ROI2(final)
    final = hsv_filter(final)
    final = cv2.addWeighted(img,1,final,1,0.0)
    return final
    

def run():
    cap = cv2.VideoCapture('line.mp4')
    #out = cv2.VideoWriter('outpy.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (640, 480))
    while (True):
        ret, src1 = cap.read()
        #src = cv2.resize(src1, (640, 640))
        src = ROI(src1)
        #src = bev(src)

        dst = cv2.Canny(src, 50, 150, None, 3)
        cdst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)

        cdstP = np.copy(cdst)
    
        lines = cv2.HoughLines(dst, 1, np.pi / 180, 100, 100, 50, 20)
    
        if lines is not None:
            for i in range(0, len(lines)):
                rho = lines[i][0][0]
                theta = lines[i][0][1]
                a = math.cos(theta)
                b = math.sin(theta)
                x0 = a * rho
                y0 = b * rho
                pt1 = (int(x0 + 1000 * (-b)), int(y0 + 1000 * (a)))
                pt2 = (int(x0 - 1000 * (-b)), int(y0 - 1000 * (a)))
                cv2.line(cdst, pt1, pt2, (0, 0, 255), 3, cv2.LINE_AA)
    
        linesP = cv2.HoughLinesP(dst, 1, np.pi / 180, 100, 100, 50, 20)
        #print(linesP)
        if linesP is not None:
            for i in range(0, len(linesP)):
                l = linesP[i][0]

                cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0, 0, 255), 3, cv2.LINE_AA)

        #final = bev_inv(cdstP)
        #final = ROI2(cdstP)
        #final = hsv_filter(cdstP)
        final = cv2.addWeighted(src1, 1, cdst, 1, 0.0)

        cv2.imshow("Source", src)
        cv2.imshow("Detected Lines (in red) - Standard Hough Line Transform", cdst)
        #cv2.imshow("Detected Lines (in red) - Probabilistic Line Transform", cdstP)
        cv2.imshow("final", final)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows() 

if __name__ == "__main__":
    run()