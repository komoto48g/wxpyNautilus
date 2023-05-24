#! python3
# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE
import numpy as np
import os
import wx
import wx.media

from mwx.graphman import Layer, Frame
from mwx.controls import Icon, Button, TextCtrl


def read_info(path):
    command = ['ffprobe',
               '-i', path,
               '-loglevel', 'quiet',    # no verbose
               '-print_format', 'json', # -format json
               '-show_streams',         # -streams info
               ]
    with Popen(command, stdout=PIPE, stderr=PIPE) as fp:
        ret, err = fp.communicate()
        if not err:
            return eval(ret)


def capture_video(path, ss=0):
    command = ['ffmpeg',
               '-ss', '{}'.format(ss),  # Note: placing -ss before -i will be faster,
               '-i', path,              #       but maybe not accurate.
               '-frames:v', '1',        # -frame one shot
               '-f', 'rawvideo',        # -format raw
               '-pix_fmt', 'rgb24',     # -pixel rgb24, gray, etc.
               'pipe:'                  # -pipe:stdout '-'
               ]
    bufsize = 4096 # w * h * 3
    buf = b"" # bytearray()
    with Popen(command, stdout=PIPE) as fp:
        while 1:
            s = fp.stdout.read(bufsize)
            buf += s
            if len(s) < bufsize:
                break
    return np.frombuffer(buf, np.uint8)


def export_video(path, f, crop, ss, to):
    command = ['ffmpeg',
               '-i', path,
               '-vf', 'crop={}'.format(crop),
               '-ss', ss,
               '-to', to,
               '-y', f,
               ]
    print('>', ' '.join(command))
    with Popen(command) as fp:
        ret, err = fp.communicate()


class MyFileDropLoader(wx.FileDropTarget):
    def __init__(self, target):
        wx.FileDropTarget.__init__(self)
        self.target = target
    
    def OnDropFiles(self, x, y, filenames):
        path = filenames[-1] # Only the last one will be loaded.
        if len(filenames) > 1:
            print("- Drop only one file please."
                  "Loading {!r} ...".format(path))
        self.target.load_media(path)
        return True


class Plugin(Layer):
    """Media loader using FFMpeg (installation required).
    """
    menukey = "FFMpeg/"
    dockable = False
    
    def Init(self):
        self.mc = wx.media.MediaCtrl()
        self.mc.Create(self, size=(300,300),
                       style=wx.SIMPLE_BORDER,
                       szBackend=wx.media.MEDIABACKEND_WMP10
                       ## szBackend=wx.media.MEDIABACKEND_DIRECTSHOW
        )
        self.mc.ShowPlayerControls()
        self.mc.Bind(wx.media.EVT_MEDIA_LOADED, self.OnMediaLoaded)
        ## self.mc.Bind(wx.media.EVT_MEDIA_PLAY, self.OnMediaPlay)
        ## self.mc.Bind(wx.media.EVT_MEDIA_PAUSE, self.OnMediaPause)
        
        self.mc.SetDropTarget(MyFileDropLoader(self))
        
        self._path = None
        
        self.ss = TextCtrl(self, label="ss:", size=(80,-1),
                           handler=self.on_get_offset,
                           updater=self.on_set_offset,
                           )
        self.to = TextCtrl(self, label="to:", size=(80,-1),
                           handler=self.on_get_offset,
                           updater=self.on_set_offset,
                           )
        self.crop = TextCtrl(self, icon="cut", size=(130,-1),
                           updater=self.on_set_crop
                           )
        self.ex = Button(self, label="Export", icon='save')
        self.rw = Button(self, icon='|<-')
        self.fw = Button(self, icon='->|')
        
        self.ex.Bind(wx.EVT_BUTTON, lambda v: self.export())
        self.rw.Bind(wx.EVT_BUTTON, lambda v: self.seekdelta(-100))
        self.fw.Bind(wx.EVT_BUTTON, lambda v: self.seekdelta(+100))
        
        self.layout((self.mc,), expand=2)
        self.layout((self.ss, self.to, self.rw, self.fw, self.crop, self.ex),
                    expand=0, row=6)
        
        self.menu[0:5] = [
            (1, "&Load file", Icon('folder_open'),
                lambda v: self.load_media()),
                
            (2, "&Snapshot", Icon('cam'),
                lambda v: self.snapshot(),
                lambda v: v.Enable(self._path is not None)),
            (),
        ]
        
        self.parent.handler.bind("unknown_format", self.load_media)
    
    def Destroy(self):
        try:
            self.parent.handler.unbind("unknown_format", self.load_media)
            self.mc.Stop()
        finally:
            return Layer.Destroy(self)
    
    def load_session(self, session):
        Layer.load_session(self, session)
        f = session.get('path')
        if f:
            self.load_media(f)
    
    def save_session(self, session):
        Layer.save_session(self, session)
        session['path'] = self._path
    
    def OnMediaLoaded(self, evt):
        self.Show()
        evt.Skip()
    
    ## def OnMediaPause(self, evt):
    ##     self.on_set_offset(self.to)
    ##     evt.Skip()
    
    def load_media(self, path=None):
        if path is None:
            with wx.FileDialog(self, "Choose a media file",
                style=wx.FD_OPEN|wx.FD_CHANGE_DIR|wx.FD_FILE_MUST_EXIST) as dlg:
                if dlg.ShowModal() != wx.ID_OK:
                    return
                path = dlg.Path
        self.mc.Load(path) # -> True (always)
        self._path = path
        self.info = read_info(path)
        if self.info:
            v = next(x for x in self.info['streams'] if x['codec_type'] == 'video')
            ## self.video_fps = eval(v['r_frame_rate']) # Real base framerate
            self.video_fps = eval(v['avg_frame_rate'])  # Average framerate
            self.video_dur = eval(v['duration']) * 1e3  # duration [ms]
            self.video_size = v['width'], v['height']   # pixel size
            self.message("Loaded {!r} successfully.".format(path))
            return True
        else:
            ## wx.MessageBox("Failed to load the media file.\n\n{!r}".format(path),
            ##               style=wx.ICON_WARNING)
            self.message("Failed to load the media file {!r}.".format(path))
            self._path = None
            return False
    
    DELTA = 1000 # correction ▲理由は不明 (WMP10 backend only?)
    
    def on_get_offset(self, tc):
        if not self._path:
            return
        t = float(tc.Value)
        self.mc.Seek(self.DELTA + int(t * 1000))
    
    def on_set_offset(self, tc):
        if not self._path:
            return
        t = round(self.mc.Tell() /1000, 3)
        tc.Value = str(t)
    
    def on_set_crop(self, tc):
        if not self._path:
            return
        ## refer frame roi to get crop area (W:H:left:top).
        crop = None
        frame = self.graph.frame
        if frame:
            nx, ny = frame.xytopixel(frame.region)
            if nx.size:
                xo, yo = nx[0], ny[1]
                xp, yp = nx[1], ny[0]
                crop = "{}:{}:{}:{}".format(xp-xo, yp-yo, xo, yo)
        if not crop:
            crop = "{}:{}:0:0".format(*self.video_size)
        tc.Value = crop
    
    def seekdelta(self, offset):
        if not self._path:
            return
        self.mc.Seek(self.DELTA + offset, mode=wx.FromCurrent)
        wx.CallAfter(wx.CallLater, 50, self.on_set_offset, self.to)
    
    def snapshot(self):
        if not self._path:
            return
        t = self.mc.Tell()
        w, h = self.video_size
        buf = capture_video(self._path, ss=t/1000).reshape((h,w,3))
        name = "{}-ss{}".format(os.path.basename(self._path), int(t))
        self.graph.load(buf, name)
    
    def export(self):
        if not self._path:
            return
        fin = self._path
        fout = "{}_clip".format(os.path.splitext(fin)[0])
        with wx.FileDialog(self, "Save as",
                defaultFile=os.path.basename(fout),
                wildcard="Media file (*.mp4)|*.mp4|"
                         "Animiation (*.gif)|*.gif",
                style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            fout = dlg.Path
        export_video(fin, fout,
                     self.crop.Value or "{}:{}:0:0".format(*self.video_size),
                     self.ss.Value, self.to.Value)


if __name__ == "__main__":
    app = wx.App()
    frm = Frame(None)
    frm.load_plug(__file__, show=1, dock=0)
    frm.Show()
    app.MainLoop()
