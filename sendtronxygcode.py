#! /usr/bin/python
#
# sendtinyboy.py -- most simpilistic gcode forwarder for my 3d printer
#
# (C) 2016 juewei@fabmail.org
# distribute under GPLv2.0 or ask.
#
# 2016-06-23, jw -- initial draught.
# 2016-08-14, jw -- fixed upward move to be really relative.
# 2016-09-05, jw -- better exception handling.
# 2016-10-01, jw -- tested and fixed error handling in ser_readline()
# 2016-10-14, jw -- est_time_min from cura ;TIME: string
#
import sys, re, serial, time
import os.path


verbose=False

ser=None
errorcount=0
def ser_readline():
  global errorcount
  global ser

  try:
    line = ser.readline()
    errorcount=0
  except Exception as e:
    line = ''
    print "ser.readline() error: " + str(e)
    time.sleep(1)
    errorcount += 1
    if errorcount == 5:
      # full re-init: close and open.
      print "ser.readline() re-initializing serial device ..."
      ser.close()
      ser_open()
    if errorcount > 10: 
      raise e
  return line

def ser_open(device=None, baud=115200, timeout=3, writeTimeout=10000):
  global ser

  if device is None:
    devicelist = [ '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3' ]
  else:
    devicelist = [ device ]

  ser = None
  for dev in devicelist:
    try:
      ser = serial.Serial(dev, 115200, timeout=3, writeTimeout=10000)
    except:
      pass
    if ser is not None: break

  if ser is None:
    print("failed to open device: " + str(devicelist))
    sys.exit(0)

  # gobble away initial boiler plate output, if any
  seen = ser_readline()
  if len(seen) == 6 and seen[:4] == 'wait': seen = ''
  while len(seen):
    print "seen: ", seen[:4], len(seen), "xx"
    seen = ser_readline()
    if len(seen) == 6 and seen[:4] == 'wait': seen = ''

def ser_check():
  empty_count = 0
  while True:
    seen = ser_readline()
    if len(seen) == 6 and seen[:4] == 'wait': seen = ''
    if seen[:2] == 'ok':
      if verbose: print seen
      break
    elif seen == '':
      time.sleep(0.1)
      empty_count += 1
      if empty_count > 50:
        break
    else:
      print "check", seen,

def ser_write(line):
  global verbose
  global ser

  if len(line) > 0:
    if verbose: print "out", line
    line += "\n"
    while len(line):
      n = ser.write(line)
      if n < 0: raise WriteError()
      line = line[n:]

## not available on tronxy: M21 says format error:
"""
   	sdcard list [DIR]			; list SDcard contents
   	sdcard delete [DIR/]FILENAME		; 
   	sdcard print [DIR/]FILENAME		; starts a print.
"""

if len(sys.argv) <= 1 or ( sys.argv[1][0] == '-' and sys.argv[1][1] not in "gcf" ):
  print """
Usage
%s [-g|-c|-f] ...

If no option is given, -f is default.

-f FILENAME
    Sends a gcode file to the printer.

-c CMD args ...
   Most commands can be abbreviated to one or two letters. 
   Available commands are:
	up 10mm					; move the printhead up 10mm
	home [all|xy|x|y|z]			; home all or some axis.
	off					; cancel all action and turn motors off.
   	sdcard upload FILENAME [DIR]		; store a file on SDcard

-g CMD args ...
    followed by gcode arguments. E.g. 
	M117 Hello World	; print text on display
	M107			; Fan off
	M106 P0 S127		; Fan 0 speed to 127
	M104 S190		; set extruder temperature to 190 C
        M84			; motors off
	M42 Pxxx Syyy		; set GPIO pin xxx to value yyy.
	G92 X0 Y0 Z0 E0		; define the current positions as origin.
    The full list of supported commands differs per firmware. 
    See http://reprap.org/wiki/G-code
"""
  sys.exit(0)


ser_open()


if sys.argv[1] == '-c':
  if sys.argv[2] in ('u', 'up'):
    ser.write("G21\n");		# ;metric values
    ser.write("G90\n");		# ;absolute positioning
    ser.write("G92 Z0\nG1 Z10.0 F2400\n")	# zero z, then move (relative)
    ser_check()
    print("move up 10mm")
    # ser.write("M109 S190.0\n");		# wait for heat

  elif sys.argv[2] in ('p', 'preheat'):
    ser.write("M104 S190.0\n");		# 190

  elif sys.argv[2] in ('c', 'cool', 'cooldown'):
    ser.write("M104 S0\n");		# cooldown

  elif sys.argv[2] in ('h', 'home'):
    if len(sys.argv) <= 3 or sys.argv[3] in ('all', 'xyz'):
      ser.write("G28 X0 Y0 Z0\n");
    elif sys.argv[3] == 'xy':
      ser.write("G28 X0 Y0\n");
    elif sys.argv[3] == 'x':
      ser.write("G28 X0\n");
    elif sys.argv[3] == 'y':
      ser.write("G28 Y0\n");
    elif sys.argv[3] == 'z':
      ser.write("G28 Z0\n");
    else:
      print "unknown home command. Try all, xy, z."

  elif sys.argv[2] in ('s', 'sdcard'):
    if sys.argv[3] in ('u', 'up', 'upload'):
      ser.write("M21\n")
      print "uploading %s to %s" % (sys.argv[4], "/")
      fd = open(sys.argv[4], 'r')
      ser.write("M28 %s\n" % os.path.basename(sys.argv[4]));
      while True:
        line = fd.readline()
        ser_write(line)
        ser_check()
      ser.write("M29\n")
      
    elif sys.argv[3] in ('d', 'rm', 'del', 'remove', 'delete'):
      print "delete a file from sdcard ..."
      ser.write("M21\n")
      ser.write("M30 %s\n" % (sys.argv[4]))

    elif sys.argv[3] in ('p', 'print'):
      print "start printing a file from sdcard ..."
      ser.write("M21\n")
      ser.write("M23 %s\n" % (sys.argv[4]))
      ser.write("M24\n")

    elif sys.argv[3] in ('stop', 'pause'):
      print "stop printing from sdcard"
      ser.write("M25\n")

    elif sys.argv[3] in ('l', 'ls', 'list', 'dir'):
      print "list files on sdcard"
    else:
      print "unknown sdcard command. Try list, upload, delete, print"
    
  elif sys.argv[2] in ('0', 'o', 'off', 'cancel', 'reset'):
    ser.write("M108\n");
    ser.write("M104 S0\n");
    ser.write("M84\n");

  else:
    print "unkown command, try -h for a list."
    
  ser_check()
  ser.close()
  sys.exit(0)


if sys.argv[1] == '-g':
  # upper case the first word, Mxxx or Gxxx command, keep the rest as they are...
  if sys.argv[2].upper() != sys.argv[2]:
    print "Error: Please use uppercase for G and M commands."
  else:
    line = ' '.join(sys.argv[2:])
    ser_write(line)
    ser_check()
  ser.close()
  sys.exit(0)


file = sys.argv[1]
if file == '-f': file = sys.argv[2]
fd = open(file, 'r')

fd.seek(0,2)	# end
total = fd.tell()
if total == 0: total = 1
fd.seek(0,0)
count = 0
tstamp = time.time()
start_tstamp = tstamp

est_time_min = 0

while True:
  line = fd.readline()
  count += len(line)
  if line == '': break
  m = re.match(';TIME:(\d*)', line)
  if (m):
    est_time_min = int(int(m.group(1))/60.)
    print("Estimated print time: %d min." % est_time_min)
  line = re.sub(';.*', '', line)
  line = re.sub('\s*[\n\r]+$', '', line)
  if line == '': continue

  ser_write(line)

  ser_check()

  now = time.time()
  if (now > tstamp + 10):
    bps = float(count) / (1 + now - start_tstamp) 
    eta = ''
    elapsed = "%d min" % (int((now - start_tstamp)/60))
    if (est_time_min): elapsed += " / %d min" % est_time_min
    if (now > start_tstamp + 2*60):	# start eta calc after 2 min
      secs = int(float(total-count)/bps)
      min = int(secs/60)
      eta = "ETA %d min" % (min)
    print "%.1f %%, %s" % (count * 100. / total, elapsed)
    tstamp = now
    

