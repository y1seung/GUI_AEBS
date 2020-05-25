
import sys
import time
import threading
import matplotlib
import cv2
import numpy as np
import LineDetection as ld
import DataRead as dr
import Kalman
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.figure import Figure
from matplotlib.animation import TimedAnimation
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

matplotlib.use("QT5Agg")

def setCustomSize(x, width, height):
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(x.sizePolicy().hasHeightForWidth())
    x.setSizePolicy(sizePolicy)
    x.setMaximumSize(QtCore.QSize(width, height))


class CustomMainWindow(QtWidgets.QMainWindow, QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CustomMainWindow, self).__init__(parent)
        vid = ShowVideo()
        print("START CUSTOMWINDOW")

        # Define the geometry of the main window
        self.setGeometry(300, 50, 1000, 1000)
        self.setWindowTitle("AEBs")
        self.LAYOUT_A = QtWidgets.QGridLayout()  # setting layout
        self.LAYOUT_B = QtWidgets.QHBoxLayout()

        # Create FRAME_A for matplotlib
        self.FRAME_A = QtWidgets.QFrame(self)
        self.FRAME_A.setLayout(self.LAYOUT_A)
        self.setCentralWidget(self.FRAME_A)

        # Place the matplotlib figure
        self.myFig = CustomFigCanvas()
        self.LAYOUT_A.addWidget(self.myFig, *(1, 0))

        # Place the video image
        self.ImageViewer = ImageViewer()
        self.LAYOUT_B.addStretch(1)
        self.LAYOUT_B.addWidget(self.ImageViewer)
        self.LAYOUT_B.addStretch(1)
        self.LAYOUT_A.addLayout(self.LAYOUT_B, *(0, 0))

        #Place the Options 
        self.btn_exit = QtWidgets.QPushButton('EXIT', self)
        self.btn_exit.move(800,20)
        self.btn_exit.setCheckable(True)
        self.btn_exit.clicked.connect(self.exit_event)

        self.lbl_TTC = QtWidgets.QLabel('Setting Criteria TTC',self)
        self.lbl_TTC.move(800,100)

        self.cTTC_spinbox = QtWidgets.QDoubleSpinBox(self)
        self.cTTC_spinbox.move(800,200)
        self.cTTC_spinbox.setMinimum(0.0)
        self.cTTC_spinbox.setMaximum(9.9)
        self.cTTC_spinbox.setSingleStep(0.1)
        self.cTTC_spinbox.setValue(2.6)
        self.cTTC_spinbox.valueChanged.connect(self.change_criteria_TTC)


        vid.VideoSignal1.connect(self.ImageViewer.setImage)
        thread2 = threading.Thread(name='thread2', target=vid.startVideo, daemon=True)
        thread2.start()
        
        # Add the callbackfunc to ..
        myDataLoop = threading.Thread(name='myDataLoop', target=dataSendLoop, daemon=True, args=(self.addData_callbackFunc,))
        myDataLoop.start()


        self.show()

    def addData_callbackFunc(self, value):
        # print("Add data: " + str(value))
        self.myFig.addData(value)

    def exit_event(self):
        sys.exit(app.exec_())

    def change_criteria_TTC(self):
        self.myFig.Criteria_TTC = round(self.cTTC_spinbox.value(),2)


class ImageViewer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self.image = QtGui.QImage()
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, self.image)
        self.image = QtGui.QImage()

    @QtCore.pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        if image.isNull():
            print("Viewer Dropped frame!")

        self.image = image
        if image.size() != self.size():
            pass
            self.setFixedSize(image.size())
            #self.setFixedSize(1000,1000) #adjust size of the widget
        self.update()



#Capture video from camera
class ShowVideo(QtCore.QObject):

    camera = cv2.VideoCapture(0)

    ret, image = camera.read()
    height, width = image.shape[:2]

    VideoSignal1 = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, parent=None):
        super(ShowVideo, self).__init__(parent)

    @QtCore.pyqtSlot()
    def startVideo(self):
        global image

        run_video = True
        while run_video:
            ret, image = self.camera.read()
            image = ld.linedetection(image)
            color_swapped_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            qt_image1 = QtGui.QImage(color_swapped_image.data,
                                    self.width,
                                    self.height,
                                    color_swapped_image.strides[0],
                                    QtGui.QImage.Format_RGB888)
            self.VideoSignal1.emit(qt_image1)

            loop = QtCore.QEventLoop()
            QtCore.QTimer.singleShot(50, loop.quit) # The number depends on the video
            loop.exec_()
            
class CustomFigCanvas(FigureCanvas, TimedAnimation):
    def __init__(self):
        self.addedData = []
        self.Criteria_TTC = 2.6
        print('Matplotlib Version:', matplotlib.__version__)

        # The data
        self.xlim = 30
        self.n = np.linspace(0, self.xlim - 1, self.xlim)
        self.y = (self.n * 0.0) + 0

        # The window
        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax1 = self.fig.add_subplot(111)

        # self.ax1 settings
        self.ax1.set_xlabel('time')
        self.ax1.set_ylabel('TTC')
        self.line1 = Line2D([], [], color='blue', label='TTC')
        self.line1_tail = Line2D([], [], color='blue', linewidth=2)
        self.line1_head = Line2D([], [], color='black', marker='o', markeredgecolor='k')
        self.Criteria_TTC_line = Line2D([], [],color='red', label = 'Criteria TTC')
        self.ax1.add_line(self.line1)
        self.ax1.add_line(self.line1_tail)
        self.ax1.add_line(self.line1_head)
        self.ax1.add_line(self.Criteria_TTC_line)
        self.ax1.set_xlim(0, self.xlim - 1)
        self.ax1.set_ylim(0, 300)
        self.ax1.grid(True)
        self.ax1.legend()

        FigureCanvas.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval=50, blit=True)

    def new_frame_seq(self):
        return iter(range(self.n.size))

    def _init_draw(self):
        lines = [self.line1, self.line1_tail, self.line1_head, self.Criteria_TTC_line]
        for l in lines:
            l.set_data([], [])

    def addData(self, value):
        self.addedData.append(value)

    def _step(self, *args):
        # Extends the _step() method for the TimedAnimation class.
        try:
            TimedAnimation._step(self, *args)
        except Exception as e:
            print("GRAPH ERROR")
            TimedAnimation._stop(self)
            pass

    def _draw_frame(self, framedata):
        margin = 1
        while(len(self.addedData) > 0):
            self.y = np.roll(self.y, -1)
            self.y[-1] = self.addedData[0]
            del(self.addedData[0])

        self.line1.set_data(self.n[0:self.n.size - margin], self.y[0:self.n.size - margin])
        self.line1_tail.set_data(np.append(self.n[-5:-1 - margin], self.n[-1 - margin]), np.append(self.y[-5:-1 - margin], self.y[-1 - margin]))
        self.line1_head.set_data(self.n[-1 - margin], self.y[-1 - margin])
        self.Criteria_TTC_line.set_data(self.n[0:self.n.size - margin], [self.Criteria_TTC for i in self.y[0:self.n.size - margin]])
        self._drawn_artists = [self.line1, self.line1_tail, self.line1_head,self.Criteria_TTC_line]

        

# You need to setup a signal slot mechanism, to
# send data to your GUI in a thread-safe way.
# Believe me, if you don't do this right, things 
# go very very wrong..
class Communicate(QtCore.QObject):
    data_signal = QtCore.pyqtSignal(float)



def dataSendLoop(addData_callbackFunc):
    # Setup the signal-slot mechanism.
    mySrc = Communicate()
    mySrc.data_signal.connect(addData_callbackFunc)
    while(True):
        pos, vel = dr.get_arduino_data()
        pos, vel = Kalman.Kalman(pos, vel)
        TTC = pos/vel
        mySrc.data_signal.emit(TTC)  # <- Here you emit a signal!

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Plastique'))
    myGUI = CustomMainWindow()

    sys.exit(app.exec_())