import shrike
import machine

shrike.flash("FPGA_bitstream_MCU_<NAME>.bin") # depending on ur bitstream update bin file name
a = machine.Pin(1, machine.Pin.OUT) #GPIO4_IN [PIN 17]
b = machine.Pin(3, machine.Pin.OUT) #GPIO5_IN [PIN 18]
#c = machine.Pin(2, machine.Pin.OUT) #GPIO3_IN [PIN 16]
# uncomment above for 3 input bitstreams -> Has to match according to u IO Planning
    
a.value(1)
b.value(0)
#c.value(0)
# uncomment above for 3 input bitstreams
