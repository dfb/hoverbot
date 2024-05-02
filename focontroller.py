import time, sys, math
import serial, binascii
from ctypes import *
import joystick

ser = serial.Serial(
 port='/dev/ttyS0',
 baudrate = 38400,
 parity=serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS,
 timeout=1
)

class SerialCommand(Structure):
  _fields_ = [('start', c_ushort), ('steer', c_short), ('speed', c_short), ('checksum', c_ushort)]

class SerialFeedback(Structure):
  _fields_ = [('start', c_ushort), ('cmd1', c_short), ('cmd2', c_short),
              ('speedR', c_short), ('speedL', c_short), ('speedR_meas', c_short), ('speedL_meas', c_short),
              ('batVoltage', c_short), ('boardTemp', c_short), ('checksum', c_ushort)]

class GV:
    recvBuffer = b''

def Receive():
    MSG_LEN = sizeof(SerialFeedback)
    if len(GV.recvBuffer) < MSG_LEN:
        more = ser.read(MSG_LEN)
        if more:
            GV.recvBuffer += more

    msgStart = GV.recvBuffer.find(b'\xaa\xaa')
    if msgStart == -1:
        return

    s = GV.recvBuffer[msgStart:msgStart+MSG_LEN]
    GV.recvBuffer = GV.recvBuffer[len(s):]
    if len(s) != sizeof(SerialFeedback):
        print('Skipping', len(s), 'bad msg', s)
    else:
        fb = SerialFeedback.from_buffer_copy(s)
        cs = c_ushort(fb.start ^ fb.cmd1 ^ fb.cmd2 ^ fb.speedR ^ fb.speedL ^ fb.speedR_meas ^ fb.speedL_meas ^ fb.batVoltage ^ fb.boardTemp).value
        if fb.start == 0xaaaa and cs == fb.checksum:
            print('speed:', fb.speedL, fb.speedR, 'speedMeas:', fb.speedL_meas, fb.speedR_meas, 'volts:', fb.batVoltage, 'temp:', fb.boardTemp)
        else:
            print('Rejecting corrupt msg:', fb.start == 0xaaaa, cs, fb.checksum)

def Send(steer, speed):
    c = SerialCommand()
    c.start = 0xaaaa
    c.steer = steer
    c.speed = speed
    c.checksum = c.start ^ c.steer ^ c.speed
    ser.write(bytes(c))

j = joystick.Joystick()
j.Start()
try:
    nextSend = time.time()+0.5
    test = 0
    while 1:
        data = Receive()

        now = time.time()
        if nextSend <= now:
            nextSend = now + 0.1

            steer = int(j.THUMB_LX / 32.768)
            steer = int(steer / 3)
            s = j.TRIGGER_L + 32767
            if s > 0:
                speed = -int(s/200)
            else:
                # only do forward if reverse (brake) is not on
                s = j.TRIGGER_R + 32767
                divBy = 100
                if j.Y: # turbo!
                    divBy = 50
                speed = int(s/divBy)
            print(steer, -speed)
            Send(steer, -speed)

finally:
    j.Stop()
