# LM Sensors stats on Cacti (via SNMP)

## Sensors

PC Motherboards contain an array of sensors and data captured from the system. This may include Motherboard Voltages, Temperatures, Fan speeds among other things.

The Linux package "lmsensors" provides tools to interrogate many popular Motherboard sensors chips and extract useful data from them. This article can't cover the particular setup required for your Motherboard sensor chip. There is plenty of docs and example config around to help you get the LM Sensors package configured.

Where we need to get to for this to work is being able to execute the "sensors" command as a regular user and getting back a load of correct data from different sensors on the Motherboard.

## Sensors over SNMP

Fortunately as sensors are available to unprivileged users the acrobatics discussed previously are not needed to get this data into snmpd. A bunch of extension scripts and some config is all that is needed.

Note that this is an indexed query so the available graphs depends on the sensors that can be read.

I place these **sensors\_generic.py** scripts (make it executable first: chmod +x sensors\_generic.py) in **/etc/snmp/**

Then include the lines from **snmpd.conf.cacti-sensors** in snmpd.conf and restart snmp. You should then be able to test with snmpwalk.

## Cacti Templates

I have generated some basic Cacti Templates for my sensors outputs.

Simply import the template **cacti_host_template_lm_sensors_parameters.xml**, and add the graphs you want in Cacti. It should just work if your SNMP is working correctly for that device (ensure other SNMP parameters are working for that device).
