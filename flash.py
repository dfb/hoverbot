'''
./ST-LINK_CLI.exe -c SWD -P ~/dev/hoverbot/hoverboard-firmware-hack/build/hover.bin 0x08000000
'''

import os, sys, subprocess, time

which = sys.argv[1] # orig or foc
if which == 'orig':
    os.chdir('hoverboard-firmware-hack')
elif which == 'foc':
    os.chdir('hoverboard-firmware-hack-FOC')
else:
    assert 0, 'orig or foc'

stLinkExe = '/mnt/c/Program Files (x86)/STMicroelectronics/STM32 ST-LINK Utility/ST-LINK Utility/ST-LINK_CLI.exe'
assert os.path.exists(stLinkExe), 'Cannot find ST-Link utility'

ret = os.system('make')
if ret != 0:
    print('BUILD FAILED')

hoverBin = 'build/hover.bin'
assert os.path.exists(hoverBin)

input('Press ENTER to reset')
ret = os.system('"%s" -c SWD -Rst' % stLinkExe)
input('Press ENTER to flash')
ret = os.system('"%s" -c SWD -P "%s" 0x08000000' % (stLinkExe, hoverBin))
print(ret)
