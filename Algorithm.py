import serial
ard = serial.Serial('COM8')

def algo(TTC, cTTC):
    if TTC < cTTC:
        ard.write(b'Q')
    
    