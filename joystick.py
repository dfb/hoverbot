'''
Read joystick inputs. Heavily specific to reading Xbox controller inputs

See https://www.kernel.org/doc/Documentation/input/joystick-api.txt for details on binary data
'''

import os, subprocess, time, threading, traceback, struct

log = print
def logTB():
    for line in traceback.format_exc().split('\n'):
        log(line)

BUTTON_NAMES = {0:'A', 1:'B', 2:'X', 3:'Y', 4:'BUMPER_L', 5:'BUMPER_R', 6:'BACK', 7:'START', 8:'XBOX',9:'THUMB_L', 10:'THUMB_R'}
AXIS_NAMES = {0:'THUMB_LX', 1:'THUMB_LY', 2:'THUMB_RX', 3:'THUMB_RY', 4:'TRIGGER_R', 5:'TRIGGER_L', 6:'DPAD_X', 7:'DPAD_Y'}

class Joystick:
    '''Converts a stream of joystick command data into a state holder class'''
    def __init__(self):
        assert os.geteuid() == 0, 'This class must be used as root currently, sorry!'
        self.proc = None
        self.f = None
        self.keepRunning = False
        self.isRunning = False

        # Note that we don't have to init our state to anything, because on start, the driver emits fake events
        # for all buttons and axes to tell us their current value

    def Start(self):
        self.proc = subprocess.Popen(['/usr/bin/xboxdrv', '--quiet', '--silent', '--detach-kernel-driver'])
        time.sleep(0.25)
        self.keepRunning = True
        self.isRunning = True
        t = threading.Thread(target=self._Thread)
        t.daemon = True
        t.start()

    def Stop(self):
        self.keepRunning = False
        try:
            self.proc.kill()
        except:
            logTB()

    def _Thread(self):
        f = open('/dev/input/js0', 'rb')
        try:
            while self.keepRunning:
                more = f.read(8)
                if not more:
                    break # should never happen

                ts, value, type, number = struct.unpack('<LhBB', more)
                if type & 1:
                    # a button
                    name = BUTTON_NAMES.get(number)
                    if name is not None:
                        setattr(self, name, value)
                    else:
                        print('Unknown button:', number)
                elif type & 2:
                    # an axis
                    name = AXIS_NAMES.get(number)
                    if name is not None:
                        setattr(self, name, value)
                    else:
                        print('Unknown axis:', number)
                #print(ts, value, type, number)
        finally:
            print('threads topping')
            self.isRunning = False

if __name__ == '__main__':
    j = Joystick()
    j.Start()
    try:
        import time
        while 1:
            try:
                time.sleep(0.5)
                vals = []
                for name in BUTTON_NAMES.values():
                    vals.append('%s:%s' % (name, getattr(j, name, '?')))
                for name in AXIS_NAMES.values():
                    vals.append('%s:%s' % (name, getattr(j, name, '?')))
                print(' '.join(vals))
            except KeyboardInterrupt:
                break
    finally:
        j.Stop()

