import serial
ard = serial.Serial('COM19')


def algo(TTC, cTTC):
    try:
        if TTC < cTTC:
            ard.write(b'Q')

    except Exception as E:
        print(E)


def curve_algo(curve):
    try:
        if curve > 10:
            ard.write(b'R')
        elif curve < -10:
            ard.write(b'L')
        else:
            ard.write(b'a')

    except Exception as E:
        print(E)