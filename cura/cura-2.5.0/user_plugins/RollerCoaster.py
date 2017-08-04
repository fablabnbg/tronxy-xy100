#! /usr/bin/python3
#
# (c) 2017 juergen@fabmail.org et al.
# Distribute under GPL-v2 or ask.
#
if __name__ != '__main__':
  from ..Script import Script
else:
  import re, sys

  class Script:
    def __init__(self):
      pass

    def getSettingValueByKey(self, name):
      if name == "pause_height": return 4
      return 0

    ##  Copied from Script.py:
    ##  Convenience function that finds the value in a line of g-code.
    #   When requesting key = 'X' from line "G1 X100" the value 100 is returned.
    def getValue(self, line, key, default = None):
        if not key in line or (';' in line and line.find(key) > line.find(';')):
            return default
        sub_part = line[line.find(key) + 1:]
        m = re.search('^-?[0-9]+\.?[0-9]*', sub_part)
        if m is None:
            return default
        try:
            return float(m.group(0))
        except:
            return default


class RollerCoaster(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name":"RollerCoaster layer height manipulation",
            "key": "RollerCoaster",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "pause_height":
                {
                    "label": "RollerCoaster height",
                    "description": "RollerCoaster At what height should the pause occur",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 5.0
                },
                "head_park_x":
                {
                    "label": "RollerCoaster Park print head X",
                    "description": "RollerCoaster What x location does the head move to when pausing.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 190
                },
                "head_park_y":
                {
                    "label": "RollerCoaster Park print head Y",
                    "description": "RollerCoaster What y location does the head move to when pausing.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 190
                },
                "retraction_amount":
                {
                    "label": "RollerCoaster Retraction",
                    "description": "RollerCoaster How much fillament must be retracted at pause.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0
                },
                "extrude_amount":
                {
                    "label": "RollerCoaster Extrude amount",
                    "description": "RollerCoaster How much filament should be extruded after pause. This is needed when doing a material change on Ultimaker2's to compensate for the retraction after the change. In that case 128+ is recommended.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0
                },
                "redo_layers":
                {
                    "label": "RollerCoaster Redo layers",
                    "description": "RollerCoaster Redo a number of previous layers after a pause to increases adhesion.",
                    "unit": "layers",
                    "type": "int",
                    "default_value": 0
                }
            }
        }"""

    def execute(self, data):
        x = 0.
        y = 0.
        prev_e = 0.
        current_z = 0.
        pause_z = self.getSettingValueByKey("pause_height")
        retraction_amount = self.getSettingValueByKey("retraction_amount")
        extrude_amount = self.getSettingValueByKey("extrude_amount")
        park_x = self.getSettingValueByKey("head_park_x")
        park_y = self.getSettingValueByKey("head_park_y")

        layers_started = False
        prev_layer_z = None
        data_out = []
        for layer in data:
            layer_z = None
            layer_out = []
            index = data.index(layer)
            lines = layer.split("\n")
            for line in lines:
                if ";LAYER:0" in line:
                    layers_started = True

                if not layers_started:
                    layer_out.append(line)
                    continue

                if self.getValue(line, 'G') == 1 or self.getValue(line, 'G') == 0:
                    z = self.getValue(line, 'Z')
                    x = self.getValue(line, 'X', x)
                    y = self.getValue(line, 'Y', y)
                    e = self.getValue(line, 'E', prev_e)
                    if z is not None and layer_z is None: layer_z = z
                    if prev_layer_z is not None and layer_z is not None:
                            line = line + "\t; H%g d%g" % (layer_z - prev_layer_z, e - prev_e)
                    prev_e = e
                layer_out.append(line)
            data_out.append('\n'.join(layer_out))
            prev_layer_z = layer_z
        return data_out

if __name__ == '__main__':
    # Prepare the input gcode file as a list of layers.
    r = RollerCoaster()
    txt = open(sys.argv[1]).read()
    layers = data=re.split('\n(?=;LAYER:)', txt)
    # Mimic how PostProcessPlugin runs the code.
    data = r.execute(layers)
    # Send the gcode output to stdout.
    print('\n'.join(data))

