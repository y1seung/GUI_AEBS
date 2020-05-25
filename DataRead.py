# Use multi thread method to get data from arduino and lidar simultaneously and draw TTC graph 

from concurrent.futures import ThreadPoolExecutor
from rplidar import RPLidar
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import time
import serial

#Arduino connection
ard = serial.Serial('COM22',115200)


#Lidar connection
LIDAR_PORT_NAME = 'COM17'  
lidar = RPLidar(LIDAR_PORT_NAME)
iterator = lidar.iter_scans(max_buf_meas=1000, min_len=0)

#Plot variables
x_num = 100
x = np.arange(x_num)
y = np.empty(x_num)
y[:] = np.NaN

fig = plt.figure(figsize = (17,6))

ax = plt.subplot(121,xlim = (0,x_num),ylim = (0,4))
plt.title('TTC Graph')
plt.xlabel('time')
plt.ylabel('TTC')


ax2 = plt.subplot(122, projection='polar') # the lidar graph
plt.title('LIDAR')


line1, = ax.plot(x,y,lw = 2,label = 'TTC')
line2 = ax2.scatter([0, 0], [0, 0], s=5, c=[0, 50],cmap=plt.cm.rainbow, lw=0)
ax2.set_rmax(5000)   #set the maximum R

line = [line1,line2]


ax.grid()
ax2.grid(True)
pool_executor = ThreadPoolExecutor(1)


def init():
    line1.set_data([],[])
    return line1,


#Get data from arduino
def get_arduino_data():
    ard.flushInput()
    while ard.readline() == None:
        continue

    vel_read = ard.readline().decode()
    vel = float(vel_read)

    return vel

#Get data from lidar
def get_value_list():
    
    scan = next(iterator)
    offsets = np.array([(np.radians(meas[1]), meas[2]) for meas in scan])
    line2.set_offsets(offsets)  

    return line2


def run(i):    
        
    start = time.time()
    pool = pool_executor.submit(get_value_list)

    while not pool.done():
        data = get_arduino_data()

    line = [animate(i,data), pool.result()]
    print(time.time()-start)

    return line       

def animate(i,data):
    global y

    if data == 0:
        pass
    else:
        y[i] = data # it should be the data read from arduino, type = float
    print('TTC:  ',y[i])

    line1.set_data(x,y)

    if i == x_num - 1 :
        y[:] = np.NaN
        line1.set_data(x,y)
    
    return line1,
                      
    
if __name__ == '__main__': 
    ani = animation.FuncAnimation(fig, run, init_func = init, frames = x_num ,interval = 50)
    ax.plot([0,100],[2.6,2.6],label = 'Criteria TTC') # 기준 TTC를 직선으로 그림
    ax.legend()
    plt.show()
   