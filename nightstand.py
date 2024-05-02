import time, sys, math
import serial, binascii
import joystick
from ctypes import *

ser = serial.Serial(
 port='/dev/ttyS0',
 baudrate = 9600,
 parity=serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS,
 timeout=1
)

class SerialCommand(Structure):
  _fields_ = [('steer', c_short), ('speed', c_short), ('crc', c_uint32)]

class SerialFeedback(Structure):
  _fields_ = [('speedL', c_short), ('speedR', c_short), ('hallSkippedL', c_ushort),
              ('hallSkippedR', c_ushort), ('temp', c_ushort), ('volt', c_ushort),
              ('ampL', c_short), ('ampR', c_short), ('debug0', c_short), ('debug1', c_short),
              ('crc', c_uint32)]

j = joystick.Joystick()
j.Start()
try:
    lastSend = 0
    start = time.time()
    while 1:
        time.sleep(0.05)
        if 0:
            try:
                s = ser.read(sizeof(SerialFeedback))
            except KeyboardInterrupt:
                break

            if len(s) == sizeof(SerialFeedback):
                crc = binascii.crc32(s[:-4])
                fb = SerialFeedback.from_buffer_copy(s)
                if fb.crc != crc:
                    print('Got bad msg:', fb.crc, crc)
                else:
                    print(fb.speedL, fb.speedR)

        cmd = SerialCommand()
        cmd.steer = 0
        cmd.speed = 0
        s = j.TRIGGER_L + 32767
        if s > 0:
            cmd.speed = -int(s/4)
        else:
            # only do forward if reverse (brake) is not on
            s = j.TRIGGER_R + 32767
            cmd.speed = int(s/4)
        print(cmd.speed)
        cmd.crc = binascii.crc32(bytes(cmd)[:SerialCommand.crc.offset])
        ser.write(bytes(cmd))
finally:
    j.Stop()
