
# domoticz_plugins_pi_fan
Fan control after exceeding the CPU temperature threshold

## Wymagane komponenty dodatkowe
The fan is controlled by setting the high state to Pin indicated in the plugin configuration. For this purpose [Wiring Pi](http://wiringpi.com/) was used. The step-by-step installation instructions are described in [Installation wiringpi](#installation-wiringpi) 

## Assumptions

## Required additional components
The fan is controlled by setting the high state to Pin indicated in the plugin configuration. For this purpose [Wiring Pi](http://wiringpi.com/) was used. The step-by-step installation instructions are described in [Installation wiringpi](#installation-wiringpi)


## Installation wiringpi
Repairing wiringPi installation

`$ gpio -v`

If you install the package, you can uninstall it by:
`$ sudo apt-get purge wiringpi`

`$ hash -r`

System update:

`$ sudo apt-get update`

`$ sudo apt-get upgrade`

If you do not have Git installed, you can install it from:

`$ sudo apt-get install git-core`

WiringPi installation using the GIT tool:

`$ cd`

`$ git clone git://git.drogon.net/wiringPi`

`$ cd ~/wiringPi`

`$ git pull origin`

Compilation and installation:

`$ cd ~/wiringPi`

`$ sudo ./build`

# Implementation

## The appearance of connections

![The appearance of connections](https://github.com/abrzoza/domoticz_plugins_pi_fan/blob/master/images/PiFan_bb.png)

Of course, the above image is only demonstrative. Ultimately, I placed the transistor, resistor and diode on the side of the fan and glued it, and at the same time protected it with hot glue.

![Image origin](https://github.com/abrzoza/domoticz_plugins_pi_fan/blob/master/images/PiFan_bb_o.png)

## Wiring diagram

![Wiring diagram](https://github.com/abrzoza/domoticz_plugins_pi_fan/blob/master/images/PiFan_schem.png)
<!--stackedit_data:
eyJoaXN0b3J5IjpbNTQ1ODQzMjQxLDIxMzMwMzQxMDMsMTA0OD
AzNDI1OSw4OTk5NjkwNzksODM3NDM0MTU0LDc0NzcyMjcyOF19

-->
