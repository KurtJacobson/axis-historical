import hal, time
h = hal.component("test")
h.newpin("i", hal.HAL_S32, hal.HAL_RD)
while 1:
    time.sleep(.2)
    h.i = h.i + 1
