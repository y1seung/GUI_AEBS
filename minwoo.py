import time
f = open(r"C:\Users\82108\Desktop\BW_TFDS_x86_EN_V1.2.6.20181129_Alpha\Data\hi22-오전 12_36_29.txt",'rt', encoding='UTF8')

while (True):
    try:
        a = f.readline()
        print(a)
    except:
        time.sleep(0.001)
