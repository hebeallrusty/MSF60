# MSF60 decoder

Simple script to decode the MSF60 signal that is broadcast from Anthorn, England.

Written with Micropython in mind, however `utime` can be swapped for `time` and the code *should* still function 

Tested using a generic module from eBay that is for the WWVB signal which also works at 60 kHz
The module has the following pinouts which have been connected to a Raspberry Pi Pico (although should work on a )

Module Pinout | Pico Pinout
---|---
VDD | 3v3 (out)
Gnd (not marked)| Gnd (any)
P | GP1
T | GP2

P acts as the switch and must be logic low to begin the pulses on T

