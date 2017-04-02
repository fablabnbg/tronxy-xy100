#! /usr/bin/python
#
# tempinjector.py
#
# Original code from: http://www.thingiverse.com/thing:1952380/#files
# Distribute under https://creativecommons.org/licenses/by-nc-sa/3.0/

# 2017-04-02, juergen@fabmail.org    
#  - added G0 and G1 detection.
#  - Z detection also if not first parameter
#  - lowering nozzle detection (to survive initial 15mm jump)
#  - handle nozzle lowering correctly.
#  - added option for an initial offset
#  - added printing of final element height (nice plausibility check of initial offset)
#  - diagnostics show mm, to avoid confusion with layer numbers.

#
import sys

class TempTower():
  def __init__(self):
    pass
  def parse(self, infl, outfl, temp, tstep, hstep, h_off=0.0):
    fi = open(infl, "r")
    try:
      fo = open(outfl, "w")
      try:
        h = hstep + h_off
        wasM104 = False
        started = False
        lastz   = 0
        lastset = 0
        lastzmax = 0
        layerh  = 0
        for l in fi:
          l = l.strip()
          if (len(l) == 0):
            fo.write("\n")
            continue

          cmd = l.split(" ")

          cmd[0] = cmd[0].upper()

          if cmd[0] in ("G0", "G1"):
             for i in range(1, len(cmd)):
               p = cmd[i].upper()
               if len(p) and p[0] in (';', 'Z'):
                 break

             if (p.find("Z") == 0):
                lastz = float(p[1:])
                if lastz > lastzmax:
                  lastzmax = lastz
                if started and (layerh == 0):
                  layerh = lastz
                  print "Layer height detected = ", layerh, "mm, cmd: ", " ".join(cmd)
                if started and (lastz < layerh):
                  layerh = lastz
                  lastzmax = lastz
                  print "Lowering to ", layerh, "mm"

                if started and (lastz >= (h+layerh)):
                  h = h + hstep
                  temp = temp + tstep
                  fo.write("M104 S" + str(temp) + "\n")
                  print "Setting temperature ", temp, "at ", lastz, "mm"
                  lastset = lastz

             if ((p.find("X") == 0) or (p.find("Y") == 0)) and not started:
              started = True

          elif cmd[0] == "M104":
            if not wasM104:
              cmd[1] = "S" + str(temp)   #write new init temp
              print "Initial temperature updated to ", temp
            else:
              print "\tOriginal temp reconfiguration ignored: ", " ".join(cmd)
              cmd = ["; ignored"] + cmd
            wasM104 = True

          elif cmd[0] == "M109":
            cmd[1]  = "S" + str(temp) # update wait for temperature to current
            print "Wait temperature updated to ", temp
            started = True

          else:
            pass # OK other command/comment

          fo.write( " ".join(cmd) + "\n")
      finally:
        fo.write("M104 S0") # for sure :)
        print "\tExtruder off command added: M104 S0"
        print "Height of final element:", lastzmax-lastset, "mm"

        fo.close()
    finally:
      fi.close()

  def help(self):
    print "usage:", sys.argv[0], " input_file.gcode output_file.gcode initial_temp temp_step element_height_mm [start_height_mm]"
    print "\nExample (http://www.thingiverse.com/thing:2184626):"
    print "\t", sys.argv[0], "STX_Better_Temperature_Tower_v5_240-160.gcode STX_TempTow240.gcode 240 -5 7 2.4"
    print "\t", sys.argv[0], "STX_Better_Temperature_Tower_v5_200-160.gcode STX_TempTow200.gcode 200 -5 7 2.4"


if __name__ == "__main__":
  tt = TempTower()
  if len(sys.argv) == 6:
    tt.parse(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]))
    print "Done"
  elif len(sys.argv) == 7:
    tt.parse(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]))
  else:
    tt.help()


