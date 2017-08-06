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
      if name == "add_comments": return 1
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


class ExampleScript(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name":"Example Script adding comments",
            "key": "ExampleScript",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "add_comments":
                {
                    "label": "Add Comments",
                    "description": "Add to each G1 and G0, a comment with H&lt;relative to prev layer&gt;",
                    "unit": "bool",
                    "type": "int",
                    "default_value": 1 
                }
            }
        }"""

    def execute(self, data):
        x = 0.
        y = 0.
        prev_e = 0.
        current_z = 0.
        add_comments = self.getSettingValueByKey("add_comments")

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
                    e = self.getValue(line, 'E', prev_e)
                    if z is not None and layer_z is None: layer_z = z
                    if add_comments and prev_layer_z is not None and layer_z is not None:
                            line = line + "\t; H%g d%g" % (layer_z - prev_layer_z, e - prev_e)
                    prev_e = e
                layer_out.append(line)
            data_out.append('\n'.join(layer_out))
            prev_layer_z = layer_z
        return data_out

if __name__ == '__main__':
    # Prepare the input gcode file as a list of layers.
    txt = open(sys.argv[1]).read()
    layers = data=re.split('\n(?=;LAYER:)', txt)
    # Mimic how PostProcessPlugin runs the code.
    r = ExampleScript()
    data = r.execute(layers)
    # Send the gcode output to stdout.
    print('\n'.join(data))

