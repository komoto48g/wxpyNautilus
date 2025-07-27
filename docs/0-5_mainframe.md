# Mainframe

Move to wxpyNautilus directory and run "wxNautilus.py"::

    $ py -3 wxpyNautilus.py

![image](_images/0-5a_mainframe.png)


## Basic operation

You can load plugins, image, and media files with DnD.
This shows the demonstration of plugin `"demo/template.py" <https://github.com/komoto48g/mwxlib/blob/main/demo/template.py>`_

<video controls width=786 src="./_static/0-5a_wxn.mp4">
</video>

The graphic window is made with matplotlib and some keys associated with the matplotlib interface are defined as follows:

Global bindings::

    [C-Ldrag] Pan move.
    [C-Rdrag] Pan zoom.
    [C-+/-] Zoom up/down (center-orientred).
    [C-wheelup/wheeldown] Zoom up/down (mouse-orientred).
    [M-a] fit-to-canvas.
    [C-a] update-axis to home position.
    [home] ditto

X/Y-axis bindings::

    [Ldrag] Drag the axis.
    [C-Ldrag] Zoom the axis.
    [C-S-Ldrag] Zoom-edge.

Selector mode bindings::

    Pressing [Lbutton] sets selection to a point.
    Pressing [S-Lbutton] sets selection to plural points (draw a polygon).
    
    [Ldrag] Draw a line or moves the edge or the lines.
    [S-Ldrag] Draw a line at an angle of 0, 45, or 90 degrees.
    [delete] Delete the selection.
    [escape] ditto.

Loupe mode bindings::

    Pressing [z] transits to zoom-mode.
    
    [Ldrag] Zoom in.
    [Rdrag] Zoom out.

Marker mode bindings::

    Pressing [c] converts selector to markers.
    
    [n] move-to-next-marker.
    [p] move-to-previoius-marker.
    [Ldrag] Move the selected marker.
    [delete] Delete the selected marker.
    [escape] Exit marker-mode.

Region mode bindings::

    Pressing [r] converts selector to a region.
    
    [Ldrag] Move the selected region.
    [M-Ldrag] Draw square region.
    [r-Ldrag] Draw rectangle region.
    [S-Ldrag] Draw rectangle region at an angle of 0, 45, or 90 degrees.
    [delete] Delete the region.
    [escape] Exit region-mode.

!!! Tip

    The startup configuration is described in "siteinit.py"
    where plugins and key bindings are defined in ``init_mainframe(self)`` function.
    Please change ``self.Editor`` that is called when editing the plugin.


## Basic access to plugins

Right-click on the plugin's panel and select the menu ``Dive into ...`` to open the plugin's shell.

![image](_images/0-5b_graph.png)

From the shell, you can access objects:

```python
>>> self
# A plugins object.
>>> self.parent
# A parent (mainframe) object.
>>> self.graph
# A reference of parent graph view (left view pane).
>>> self.output
# A reference of parent output view (right view pane).
>>> self.graph.frame
# Currently selected graph frame proxy of <matplotlib.image.AxesImage>.
>>> self.graph.buffer
# Currently selected graph frame.buffer array.
```


<!--
## Usage of the shell

You can use the shell to test image processing on loaded images.

<video controls width=786 src="./_static/demo-denoising.mp4">
</video>

Isn't she lovely? (I meant the little one. ^^)
-->
