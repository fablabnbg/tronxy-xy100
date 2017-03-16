Maximizing the Print Area
=========================

The movement in X and Y direction does not exactly bring the nozzle to the edges of the print plate.
The movement in Z direction is limited.

To address this, several parts were redesigned. Most part are 2D objects to be cut out of 5mm acrylic or to be 3D-printed. These parts are constructed with inkscape and are contained in parts/parts.svg -- exported *.scad and *.stl files from these parts are found in corresponding subdirectories.
Other parts (e.g. end-caps) are created as true 3D-objects with freeCAD. Their source are *.fcstd files located in subdirectories of the parts folder.

With the modfications described here, the print area can be extended from 120mm x 140mm to 155mm x 160mm

Optimizing build height
-----------------------
1. The build plate can be lowered to ca 7mm above the Y-table. Adjustable by 
tightening the 4 thumb screws under the table. The available Z-end stop 
adjustment can compensate for that.

2. Upper movement is blocked by the print head hitting the buttons of the display already at a height of 65mm. We re-mount the display, so that the buttons protrude only 1mm through the top plate, and the display itself is flush. parts/display-spacer.stl has a range of spacers, long and short in some variation.

3. The remaining obstacles are
* Two rounded acrylic pieces colliding 5mm before the brass nuts would hit the top cover.
* The mount of the print head wastes ca 20mm height. The nozzle height should not be much lower than the linear bearings.

Optimizing the front edge
-------------------------
In Y direction, the plate cannot move far enough inwards, so that the nozzle
reaches the front edge.

There are several obstacles, that prevent sufficient movement.

1. The Y endstop mount is not adjustable. It stops the movement early.
A redesigned y-endstop-mount.stl allows adjustment.

2. The long 20mm screws from the end-caps of the rods protrude ca 10mm beyond the nuts. This collides with the table.
Redsigned end-caps with only 2mm thickness under the screw head allow for use of 10mm screws that do not protrude at all.
  
3. The Y motor mount has an upper corner that collides with the table.
The corner needs to be cut away with saw and file. (I am too lazy to recreate that piece right now.)

4. The y motor connector is on the top according to the assembly guide. This collides with the print plate. Rotate the motor 180 deg, there is enough space on the bottom to accomodate connector and cable.

With these adjustments, the nozzle reaches the fromt of the build plate just
before the table hits the screws in the back wall. No further optimization
possible there. Please make sure all cables are zip tied away from the
collision area.

Optimizing the rear edge
------------------------

The programmed travel is longer than the physical travel. Pausing a print causes the table to move fully outward and hitting the physical limits. The y-position is lost, resuming the print is not possible.

1. When the table moves forward it collides with the large washers of the idler.
A redesigned parts/y-idler-mount lowers the idler by 1.5mm so that it fits 
under the table. A belt tensioning mechanism could also be added here. Easiest is an oblong hole for mounting the roller bearing.

The belt is attached to the table at a position reached by the idler. This prevents further movement. The rails have 8 mm more travel, but the nozzle is already 4 mm beyond the rear edge of the plate.

Optimizing left edge
--------------------

The x-limit switch protrudes from the print head. The switch should trigger just 1mm before the print head hits the block.

Optimizing the right edge
-------------------------

There is ca 20mm unused travel on the right hand side. We need smaller roller bearings for the x-idler, so that the belt moves more horizontal. It should have approximately the same diameter as the pulley. 
The programmed travel is shorter than the physical travel.

