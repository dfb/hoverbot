# hoverbot
Hoverboard + Raspberry Pi

# mounting from pi to dev machine
sudo mount.cifs //loki.local/hoverbot /home/dave/loki -o user=dave,uid=$(id -u),gid=$(id -g)

# TODO

hoverboard's responsibilities:
- reporting current state - battery, temperature, wheel speeds
- adjust speed to target speed, but in such a way that the transition is smooth
- safely slow down and stop if there's no msg from the app
- power on/off, including auto poweroff if no activity for awhile

app's responsibilities:
- receive inputs from joystick
- send target speeds for each wheel to hoverboard
- read status data from hoverboard and shutdown on low power or high temp or whatever
- figure out and impose safety limits: top wheel speeds, top opposite wheel speeds, acceleration rates, turning rates

msg TO hoverboard:
16b msgID (a counter, so we can detect skipped)
8b cmd - the command defines the length
payload - maybe it's fixed sized?

TO commands:
- heartbeat, just a way to say "keep going". payload:null
- poweroff - stop listening for new data, set speed goal=0, and when reached, power off. payload: null
- echomode. payload: on or off. maybe an echo debug mode where all it does is send back ACKs?
- turn on/off various debug flags/values. payload: 1Bknob num, 2B:value
- set max acceleration. payload: max pwm diff in... a second maybe?
- set max speed. payload: max pwm value perhaps?
- set max turn rate - maybe max wheel differential. payload: 2B int max diff
- set target speed for each wheel. payload: 2B *per wheel*

msg FROM hoverboard:
16b msgID (a counter, so we can detect skipped)
8b cmd - the command defines the length
payload - maybe it's fixed sized (but not necessarily the same as the IN msg size)

FROM commands:
- startup / hello msg
- unknown msg
- heartbeat. just some stats on current speed, voltage, power draw, missed messages, speed goal, powering down or not
- ACK any set commands?
- auto powerdown w/ reason ID

main:
    all the init stuff
    set state = running # running, powerdown, echo
    speedL,R=0
    speedGoalL,R=0
    maxAccel = X
    maxTurn = X
    haveMsg = false
    trigger interrupt listener
    send a version / hello msg
    loop:
        sleep a little
        if state == echo:
            if haveMsg:
                loopsWithoutMsg = 0
                if msg == echo and payload=off
                    state = running
                else:
                    echo the msg back
                trigger interrupt listener to start again
            else:
                need to do same no-msg countdown

        if state == running:
            if battery is too low:
                state = powerdown
                speedGoalL,R=0
                send auto-powerdown msg, reason=low battery
            if haveMsg:
                loopsWithoutMsg = 0
                make a note of any skipped msgs
                haveMsg = false
                if msg == heartbeat:
                    pass
                elif msg == poweroff:
                    state = powerdown
                    speedGoalL,R=0
                    send a powerdown msg, reason=host initiated
                elif msg == echomode:
                    if payload == on:
                        state = echo
                #elif msg == set debug knob <-- implement this once we have a use case
                elif msg == set max accel
                    set
                elif msg == set max speed
                    set
                elif msg == set max turnrate
                    set
                elif msg == set speed goal
                    set
                else:
                    send unknown msg msg

                trigger interrupt listener to start again
            else: # no msg ready
                loopsWithoutMsg++
                if loopsWithoutMsg > TOO_MANY:
                    state = powerdown
                    speedGoalL,R=0
                    maybe send a msg indicating auto-powerdown w/ reason=listen timeout

        if state == powerdown:
            if speedL,R==0
                break

        # TODO: adjust speeds to get closer to goals, but also apply limits

        # TODO: if enough time has elapsed since last heartbeat out, send a status msg out

    # post-loop
    beep
    poweroff

on interrupt:
    haveMsg = true

    

