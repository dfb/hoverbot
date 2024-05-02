#!/usr/bin/env python
import time, sys
import serial, binascii
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
  _fields_ = [('steer', c_short), ('speed', c_short), ('crc', c_ulong)]

class SerialFeedback(Structure):
  _fields_ = [('speedL', c_short), ('speedR', c_short), ('hallSkippedL', c_ushort),
              ('hallSkippedR', c_ushort), ('temp', c_ushort), ('volt', c_ushort),
              ('ampL', c_short), ('ampR', c_short), ('debug0', c_short), ('debug1', c_short),
              ('crc', c_uint32)]

lastSend = 0
while 1:
  try:
    s = ser.read(sizeof(SerialCommand))
  except KeyboardInterrupt:
    break

  if len(s) == sizeof(SerialCommand):
    crc = binascii.crc32(s[:-4])
    cmd = SerialCommand.from_buffer_copy(s)
    if cmd.crc != crc:
      pass #print('Got bad msg:', cmd.steer, cmd.speed, cmd.crc, crc)
    else:
      print(cmd.steer, cmd.speed)

  now = time.time()
  if now >= lastSend + 0.1:
    lastSend = now
    f = SerialFeedback()
    f.speedL=1
    f.speedR=2
    f.hallSkippedL = 3
    f.hallSkippedR = 4
    f.crc = binascii.crc32(bytes(f)[:SerialFeedback.crc.offset])
    print('sending', bytes(f))
    ser.write(bytes(f))
