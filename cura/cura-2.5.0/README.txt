Cura 2.5.0 loads the settings from cura 2.4.0 hooray.

But they introduced a new issue: Starting cura with stl files on the command
line only works when a full path is given. See the cura.sh script for a
workaround.

The x-endstop is defined to be at -10mm in the Firmware.
With the larger bed, we can gain another 10mm in x, by redefining it to be at 0mm

; directly after xy home, do:
G92 X0


