#!/bin/sh
USBPOWER_FILE=`echo /sys/devices/platform/soc/*.usb/buspower`
#Haaaxxxx
#Somebody knows a better way?
echo 0 > $USBPOWER_FILE
echo 1 > $USBPOWER_FILE
