# MSF60 decoder

Simple script to decode the MSF60 signal that is broadcast from Anthorn, England.

Written for a Pi Pico, however the library MSF.py could be used in isolation within another project.

Tested using a generic module from eBay that is for the WWVB signal which also works at 60 kHz

The module has the following pinouts which have been connected to a Raspberry Pi Pico (although should work on a )

Module Pinout | Pico Pinout
---|---
VDD | 3v3 (out)
Gnd (not marked)| Gnd (any)
P | GP1
T | GP2

P acts as the switch and must be logic low to begin the pulses on T

Once the signal is received, it is validated to ensure that it produces the correct time.

Given the nature of the MSF60 signal - the library takes *at least* one minute to return, so may be best to either run on the Pico's second core, or as a completely separate device

The Code is heavily commented to provide an understanding of what is happening. In summary, the Minute Marker is searched for with it's unique pattern which begins the process of decoding, then each second's distinct pattern is found to allow Bit A and Bit B to be read from the signal. Finally after the whole minute is read, the signal is validated and the results provided back

