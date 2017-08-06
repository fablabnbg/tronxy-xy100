#! /usr/bin/python3
#
# (c) 2017 juergen@fabmail.org et al.
# Distribute under GPL-v2 or ask.
#

import math

if __name__ != '__main__':
  from ..Script import Script
else:
  import re, sys

  class Script:
    def __init__(self):
      pass

    def getSettingValueByKey(self, name):
      """ code all parameters here, for standalone usage """
      if name == "max_grade_perc"     : return 50.0
      if name == "mode"               : return "x"
      if name == "shape"              : return "triangular"
      if name == "periods"            : return 1.0
      if name == "start_phase_perc"   : return 0.0
      if name == "max_layer_mul"      : return 2.0
      if name == "min_layer_mul"      : return 0.5
      if name == "use_bb"             : return "auto"
      if name == "min_x"              : return -30.0
      if name == "max_x"              : return 30.0
      if name == "min_y"              : return -30.0
      if name == "max_y"              : return 30.0
      if name == "max_segment_len"    : return 2.0
      if name == "adaptive_flow_perc" : return 100.0
      return None

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
        self.opt = {}

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
                    "options": { "x": "X-axis (linear)", "y": "Y-axis (linear)", "c": "Circular (polar, about center)", "r": "Radial (from center)" },
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
                    "maximum_value_warning": 100.0
                },
                "shape":
                {
                    "label": "Pattern Shape",
                    "description": "Repetitive shape of the pattern.",
                    "type": "enum",
                    "options": { "triangular": "Triangles", "sinuid": "Sinus", "concave": "Concave", "convex": "Convex" },
                    "default_value": "triangular"
                },
                "start_phase_perc":
                {
                    "label": "Start offset percentage",
                    "description": "0%: start low at minimum X/Y or at center (if radial). 100% starts high (at half a period)",
                    "unit": "%",
                    "type": "float",
                    "default_value": 0.0,
                    "minimum_value": 0.0,
                    "maximum_value": 200.0
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
                    "default_value": -30.0,
                    "enabled": "use_bb == 'manual'"
                },
                "max_x":
                {
                    "label": "Maximum X Coordinate",
                    "description": "X position where the last period ends. Everything beyond remains flat.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 30.0,
                    "enabled": "use_bb == 'manual'"
                },
                "min_y":
                {
                    "label": "Minimum Y Coordinate",
                    "description": "Y position where the first period begins. Everything beyond remains flat.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": -30.0,
                    "enabled": "use_bb == 'manual'"
                },
                "max_y":
                {
                    "label": "Maximum Y Coordinate",
                    "description": "Y position where the last period ends. Everything beyond remains flat.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 30.0,
                    "enabled": "use_bb == 'manual'"
                },
                "adaptive_flow_perc":
                {
                    "label": "Adapt flow rate",
                    "description": "0%: do not adapt flow rate; 100%: compensate flow for thicker and thinner layers",
                    "unit": "%",
                    "type": "float",
                    "default_value": 100.0,
                    "minimum_value": 0.0,
                    "maximum_value_warning": 200
                },
                "max_segment_len":
                {
                    "label": "Maximum Segment Length",
                    "description", "Subdivide straight edges. Needed for non-linear pattern shapes (i.e. all except Triangles).",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 2.0,
                    "minimum_value": 0.5
                }

            }
        }"""


    def normalize_periodic_range(self, v, v_min, v_max):
        """Values v less or equal to v_min are mapped to 0.01 * start_phase_perc.
           The distance between min_v and v_max corresponds to exactly periods repetitions
           of a [0..1[ ramp. So that if periods is 0.5, max_v maps to 0.5 + 0.01 * start_phase_perc.
        """
        d = v_max - v_min
        v -= v_min
        if v < 0.0: v = 0.0
        elif v > d: v = d
        return ((0.01 * self.opt['start_phase_perc'] + v/d * self.opt['periods']) % 1.0)


    def interpolate_layer_mul(self, m):
        """ assuming m is in the range [0..1], we map m=0 to min_layer_mul and m=1 to max_layer_mul
            Between these extrema, we do linear interpolation.
        """
        d = self.opt['max_layer_mul'] - self.opt['min_layer_mul']
        return self.opt['min_layer_mul'] + m * d


    def interpolate_layer_mul_exp(self, m):
        """ assuming m is in the range [0..1], we map m=0 to min_layer_mul and m=1 to max_layer_mul
            Between these extrema, we do exponential interpolation,
            so that m=0.5 min_layer_mul=0.25 max_layer_mul=4 results in 1.0
        """
        return math.exp(self.ln_min_layer_mul + m * (self.ln_max_layer_mul - self.ln_min_layer_mul))


    def periodic_shape_triangular(self, v):
        """fold v into the range [0..1[, then apply a
           linear ramp from (0.0) min_layer_mul to (0.5) max_layer_mul and back to (1.0) min_layer_mul.
        """
        v = v % 1.0
        if v < 0.5:
            m = 2.0 * v
        else:
            m = 2.0 * (1.0 - v)
        # print("v=%g, m=%g" % (v,m))
        return self.interpolate_layer_mul(m)


    def periodic_shape_sinuid(self, v):
        v = v % 1.0
        m = 0.5 - 0.5 * math.cos(2.0 * math.pi * v)
        # print("v=%g, m=%g" % (v,m))
        return self.interpolate_layer_mul(m)


    def periodic_shape_concave(self, v):
        v = v % 1.0
        if v < 0.5:
            m = 4.0 * v * v
        else:
            m = 4.0 * (1.0 - v) * (1.0 - v)
        # print("v=%g, m=%g" % (v,m))
        return self.interpolate_layer_mul(m)


    def periodic_shape_convex(self, v):
        v = v % 1.0
        m = 1.0 - 4.0*(v-0.5)*(v-0.5)
        # print("v=%g, m=%g" % (v,m))
        return self.interpolate_layer_mul(m)


    def layer_multiplier_x_axis(self, x, y):
        """Run a number of periodic height changes along the x-axis.
           Starting at min_x with the value of start_phase_perc and ending at
           max_x with the value corresponding to start_phase_perc + periods.
           The multiplier is determined by the shape method called with a normalized range [0..1[
        """
        m = self.normalize_periodic_range(x, self.opt['min_x'], self.opt['max_x'])
        return self.shape(m)


    def layer_multiplier_y_axis(self, x, y):
        m = self.normalize_periodic_range(y, self.opt['min_y'], self.opt['max_y'])
        return self.shape(m)


    def layer_multiplier_circular(self, x, y):
        """polar coordinates used here.
           Assuming period = 1, and start_phase_perc = 0:
           All positions with x = cx and y < cy are our logical minimum of phase 0 deg,
           all positions with x = cy and >= cy a our logical maximum of phase 180 deg,
           rotated further by start_phase_perc.
           CAUTION: The area around the center needs special dampening to stay within max_grade_perc
           CAUTION: periods is rounded up(!) to an integer value.
        """
        cx = 0.5 * (self.opt['min_x'] + self.opt['max_x'])
        cy = 0.5 * (self.opt['min_y'] + self.opt['max_y'])
        periods = -round(-self.opt['periods'], 0)

        raise ValueError('not implemented.')


    def layer_multiplier_radial(self, x, y):
        """Assuming period = 1, and start_phase_perc = 0:
           The center cx,cy is our logical minimum of phase 0 deg,
           the ellipsis touching the bounding box from the inside is at phase 360 deg.
           This means, that a star extending into the corners of the bounding box will have flat portions
           on its arms, where they reach beyond the ellipsis.
        """
        cx = 0.5 * (self.opt['min_x'] + self.opt['max_x'])
        cy = 0.5 * (self.opt['min_y'] + self.opt['max_y'])
        r = self.opt['max_x'] - cx
        ry = self.opt['max_y'] - cy
        yscale = r/ry
        y = yscale * y
        cy = yscale * cy
        raise ValueError('only half implemented.')


    def layer_multiplier_identity(self, x, y):
        """We switch to this layer_multiplier, once we hit the max_grade_perc limit.
           This causes all higher layers to repeat the same pattern in parallel lines.
        """
        return 1.0


    def execute(self, data):
        x = 0.
        y = 0.
        prev_e = 0.
        current_z = 0.
        for option in (
                "max_grade_perc",
                "mode",
                "periods",
                "start_phase_perc",
                "max_layer_mul",
                "min_layer_mul",
                "use_bb",
                "min_x",
                "max_x",
                "min_y",
                "max_y",
                "max_segment_len",
                "adaptive_flow_perc",
                "shape" ):
            self.opt[option] = self.getSettingValueByKey(option)

        if   self.opt['mode'] == 'x': self.lmult = self.layer_multiplier_x_axis
        elif self.opt['mode'] == 'y': self.lmult = self.layer_multiplier_y_axis
        elif self.opt['mode'] == 'c': self.lmult = self.layer_multiplier_circular
        elif self.opt['mode'] == 'r': self.lmult = self.layer_multiplier_radial
        else: raise ValueError('mode = "'+self.opt['mode']+'" unknown.')

        if   self.opt['shape'] == 'triangular': self.shape = self.periodic_shape_triangular
        elif self.opt['shape'] == 'sinuid':     self.shape = self.periodic_shape_sinuid
        elif self.opt['shape'] == 'convex':     self.shape = self.periodic_shape_convex
        elif self.opt['shape'] == 'concave':    self.shape = self.periodic_shape_concave
        else: raise ValueError('shape = "'+self.opt['shape']+'" unknown.')

        self.ln_min_layer_mul = math.log(self.opt['min_layer_mul'])
        self.ln_max_layer_mul = math.log(self.opt['max_layer_mul'])

        print("; opt = " + str(self.opt))
        print("; lmult = " + str(self.lmult))
        print("; shape = " + str(self.shape))

        for x in range(-40, 40):
            print("x: %g, H:%g" % (x, self.lmult(x,0)) )

        sys.exit(1)

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

                    ## Primitive layer height calculation ahead:
                    # Compare the first z-value from this layer
                    # with the first Z-value from the previous layer. This works well for normal prints,
                    # but CAUTION: may fail miserably for spiralized prints, when the rotation
                    # direction changes.
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

