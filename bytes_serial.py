import time
import serial

ser = serial.Serial('COM13', 115200)
#ard = serial.Serial('COM19', 9600)
TF_buff = [b'0' for i in range(9)]
b = b'0xff'
dis_list = []

def bytes_serial():
    checksum = 0
    start = time.time()
    TF_buff[0] = ser.read()
    checksum += int.from_bytes(TF_buff[0], 'big')
    if(TF_buff[0] == b'Y'):
        TF_buff[1] = bytes(ser.read())
        checksum += int.from_bytes(TF_buff[1], 'big')
        if(TF_buff[1] == b'Y'):
            for i in range(2, 9):
                TF_buff[i] = bytes(ser.read())
                checksum += int.from_bytes(TF_buff[i], 'big')
            checksum = checksum.to_bytes(2, 'big')
            checksum = (checksum[1] & b[0]).to_bytes(2, 'big')
            #print(checksum)
            #print(TF_buff)
            distance = int.from_bytes(TF_buff[2], 'big') + int.from_bytes(TF_buff[3], 'big') * 256
            dt = round((time.time()-start),4)
            return distance, dt
            #print(TF_buff)
            if( checksum == TF_buff[8]):
                distance = int.from_bytes(TF_buff[2]) + int.from_bytes(TF_buff[3]) * 256
                #print(distance)
            else:
                checksum = 0
        else:
            checksum = 0
    else:
        checksum = 0


def get_pos_vel(prev_dis):
    dist_sum = 0
    dt_sum = 0
    for i in range(15):
        dist, dt = bytes_serial()
        dist_sum += dist
        dt_sum += dt

    dis_mean = dist_sum / 15000      #m 단위
    vel = (dis_mean-prev_dis) / (dt_sum)     #m/s단위
    vel = round(vel, 2)
    return dis_mean, vel

def get_movemean(prev_dis):
    dis_sum = 0
    dt_sum = 0

    while (len(dis_list) < 5 ):
        dis_list.append(bytes_serial())
        
    for dis, dt in dis_list:
        dis_sum += dis
        dt_sum += 0.01

    dis_mean = dis_sum /5000
    dis_mean = round(dis_mean,3)
    vel = (dis_mean - prev_dis) / dt_sum
    vel = round(vel,2)
    dis_list.remove(dis_list[0])

    return dis_mean, vel


if __name__ == "__main__":
    dis = 0
    vel = 1
    TTC = 10
    while(True):
        start = time.time()
        dis, vel = get_movemean(dis)
        print(dis)
        print(vel)
        vel = -vel
        if (vel == 0):
            pass
        elif vel < 0:
            pass
        else:
            TTC = dis/vel

        #print(TTC)
        if TTC < 0.26:
            print("==============================")


