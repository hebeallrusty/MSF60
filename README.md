# MSF60 decoder

*still work in progress but produces the correct time and date (from the signal)and validates those component parts for accuracy.*

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

