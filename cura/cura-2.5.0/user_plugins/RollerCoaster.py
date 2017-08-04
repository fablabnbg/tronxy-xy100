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
      """ code all parameters here, for standalone usage """
      if name == "max_grade_perc": return 50
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
    version = "0.1"
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        """
           A json structure to be parsed by 
           https://github.com/Ultimaker/Uranium/blob/2.5/UM/Settings/SettingFunction.py
        """

        return """{
            "name":"RollerCoaster """ + self.version + """ (layer height manipulation)",
            "key": "RollerCoaster",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "max_grade_perc":
                {
                    "label": "Maximum grade",
                    "description": "Percentage rise over run [0..100..], limited e.g. by nozzle geometry.",
                    "unit": "%",
                    "type": "float",
                    "default_value": 50.0,
                    "minimum_value": 10.0,
                    "maximum_value_warning": 100.0
                },
                "mode":
                {
                    "label": "Linear or polar modes",
                    "description": "Apply in X or Y orientation or radial or along the circumfere.",
                    "type": "enum",
                    "options": { "x": "X-axis (linear)", "y": "Y-axis (linear)", "c": "Circumfere (polar)", "r": "Radial (from center)" },
                    "default_value": "x"
                },
                "periods":
                {
                    "label": "Nr. of periods",
                    "description": "how often to swing back and forth in the horizontal.",
                    "unit": "periods",
                    "type": "float",
                    "default_value": 0.5,
                    "minimum_value": 0.1,
                    "minimum_value_warning": 0.49,
                    "maximum_value_warning": 100
                },
                "start_perc":
                {
                    "label": "Start offset percentage",
                    "description": "0%: start low at minimum X/Y or at center (if radial). 100% starts high (at half a period)",
                    "unit": "%",
                    "type": "float",
                    "default_value": 0,
                    "minimum_value": 0,
                    "maximum_value": 200
                },
                "max_layer_mul":
                {
                    "label": "Maxiumum multiplier for layer height",
                    "description": "Factor for maximum enlargement of a single layer.",
                    "unit": "layer heights",
                    "type": "float",
                    "default_value": 2.0,
                    "minimum_value": 1.0,
                    "maximum_value_warning": 4.0
                },
                "min_layer_mul":
                {
                    "label": "Minimum multiplier for layer height",
                    "description": "Factor for smallest compression of a single layer.",
                    "unit": "layer heights",
                    "type": "float",
                    "default_value": 0.5,
                    "minimum_value": 0.1,
                    "minimum_value_warning": 0.25,
                    "maximum_value": 1.0
                },
                "use_bb":
                {
                    "label": "Use automatic bounding box",
                    "description": "auto: determine maximum and minimum coordinates from the object bounding box; or manual: specify manually.",
                    "type": "enum",
                    "options": { "auto": "Automatic", "manual": "Manual" },
                    "default_value": "auto"
                },
                "min_x":
                {
                    "label": "Minimum X Coordinate",
                    "description": "X position where the first period begins. Everything beyond remains flat.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": -30,
                    "enabled": "use_bb == 'manual'"
                },
                "max_x":
                {
                    "label": "Maximum X Coordinate",
                    "description": "X position where the last period ends. Everything beyond remains flat.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 30,
                    "enabled": "use_bb == 'manual'"
                },
                "min_y":
                {
                    "label": "Minimum Y Coordinate",
                    "description": "Y position where the first period begins. Everything beyond remains flat.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": -30,
                    "enabled": "use_bb == 'manual'"
                },
                "max_y":
                {
                    "label": "Maximum Y Coordinate",
                    "description": "Y position where the last period ends. Everything beyond remains flat.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 30,
                    "enabled": "use_bb == 'manual'"
                },
                "adaptive_flow_perc":
                {
                    "label": "Adapt flow rate",
                    "description": "0%: do not adapt flow rate; 100%: compensate flow for thicker and thinner layers",
                    "type": "float",
                    "default_value": 100,
                    "minimum_value": 0,
                    "maximum_value_warning": 200
                },
                "shape":
                {
                    "label": "Pattern Shape",
                    "description": "Repetitive shape of the pattern.",
                    "type": "enum",
                    "options": { "triangular": "Triangles", "sinuide": "Sinus", "concave": "Concave", "convex": "Convex" },
                    "default_value": "triangular"
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

