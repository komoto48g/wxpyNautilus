#! python3
"""siteinit file
"""


def init_mainframe(self):
    ## Specify an editor to edit plugins.
    self.EDITOR = "C:/usr/home/bin/xyzzy/xyzzy.exe"

    ## Image/CCD unit length per pixel [mm/pix]
    self.graph.unit = self.output.unit = 0.05

    ## Cutoff tolerance of the score percentile
    self.graph.score_percentile = 0.05
    self.output.score_percentile = 0.05

    ## matplotlib/wxagg backend
    ## Restrict imshow sizes max <= 24e6 (bytes typ.)
    self.graph.nbytes_threshold = 8e6
    self.output.nbytes_threshold = 8e6

    ## window layout
    self.histogram.modeline.Show()

    ## --------------------------------
    ## Plugins
    ## --------------------------------

    from mwx.plugins import frame_listview, line_profile, fft_view
    self.load_plug(frame_listview)
    self.load_plug(line_profile)
    self.load_plug(fft_view)

    ## --------------------------------
    ## Global keymap of the main Frame 
    ## --------------------------------

    self.define_key('C-x o', self.load_session)
    self.define_key('C-x s', self.save_session)
    self.define_key('C-x S-s', self.save_session_as)

    ## @self.define_key('M-right', dir=1, doc="focus to next window")
    ## @self.define_key('M-left', dir=-1, doc="focus to prev window")
    ## def other_window(v, dir):
    ##     ls = [w for w in self.graphic_windows if w.IsShownOnScreen()]
    ##     for j, w in enumerate(ls):
    ##         if w.canvas.HasFocus():
    ##             next = ls[(j+dir) % len(ls)]
    ##             return next.SetFocus()
    ##     else:
    ##         self.graph.SetFocus()
