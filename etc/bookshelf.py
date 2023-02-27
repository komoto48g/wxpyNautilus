import contextlib
import os
import wx
import mwx
from mwx.controls import Icon, TreeListCtrl
from wxpyNautilus import Layer, Frame


class ItemData:
    def __init__(self, root, buffer):
        self.root = root
        self.buffer = buffer
        self._itemId = None #: reference <TreeItemId>


class EditorTreeCtrl(TreeListCtrl):
    def __init__(self, parent, *args, **kwargs):
        TreeListCtrl.__init__(self, parent, *args, **kwargs)
        
        self.parent = parent
        self.target = None
        
        self.context = {
            None : {
                   'buffer_new' : [ None, self.on_buffer_new ],
                  'buffer_caps' : [ None, self.set_caption ],
                 'buffer_saved' : [ None, ],
                'buffer_loaded' : [ None, ],
               'buffer_removed' : [ None, self.on_buffer_removed ],
              'buffer_selected' : [ None, self.on_buffer_selected ],
             'buffer_activated' : [ None, self.on_buffer_selected ],
           'buffer_inactivated' : [ None, ],
            },
        }
        
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDclick)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy)
        
        @self.handler.bind('enter pressed')
        def enter(v):
            data = self.GetItemData(self.Selection)
            if data:
                buf = data.buffer
                editor = buf.parent
                editor.swap_buffer(buf)
                editor.parent.popup_window(editor, focus=1)
            v.Skip()
        
        @self.handler.bind('*button* pressed')
        @self.handler.bind('*button* released')
        def dispatch(v):
            """Fork mouse events to the parent."""
            self.parent.handler(self.handler.event, v)
            v.Skip()
    
    def OnDestroy(self, evt):
        if evt.EventObject is self:
            self.unwatch()
        evt.Skip()
    
    def SetItemData(self, item, data, *rest):
        """Sets the item client data. (override)"""
        try:
            data._itemId = item
            TreeListCtrl.SetItemData(self, item, data)
        except AttributeError:
            pass
    
    ## --------------------------------
    ## Actions for bookshelf interfaces
    ## --------------------------------
    
    def watch(self, target):
        self.target = target
        if self.target:
            for editor in self.target.all_pages():
                editor.handler.append(self.context)
                self[editor.Name] = [(buf.name, ItemData(self, buf))
                                        for buf in editor.all_buffers()]
            self.reset()
    
    def unwatch(self):
        if self.target:
            for editor in self.target.all_pages():
                editor.handler.remove(self.context)
            self.clear()
        self.target = None
    
    def on_buffer_new(self, buf):
        self[f"{buf.parent.Name}/{buf.name}"] = ItemData(self, buf)
        self.reset(clear=False)
    
    def on_buffer_removed(self, buf):
        del self[f"{buf.parent.Name}/{buf.name}"]
        self.reset()
        buf.parent.SetFocus() # restore focus
    
    def on_buffer_selected(self, buf):
        data = self[f"{buf.parent.Name}/{buf.name}"]
        if data:
            wx.CallAfter(self.SelectItem, data._itemId)
    
    def set_caption(self, buf, caption):
        data = self[f"{buf.parent.Name}/{buf.name}"]
        if data:
            self.SetItemText(data._itemId, caption)
    
    def OnLeftDclick(self, evt):
        item, flags = self.HitTest(evt.Position)
        if item:
            data = self.GetItemData(item)
            if data:
                buf = data.buffer
                editor = buf.parent
                editor.swap_buffer(buf)
                editor.parent.popup_window(editor, focus=0)
                return
        evt.Skip()


class Plugin(Layer):
    def Init(self):
        self.tree = EditorTreeCtrl(self,
            style=wx.TR_DEFAULT_STYLE
                ## | wx.TR_HIDE_ROOT
                ## | wx.TR_FULL_ROW_HIGHLIGHT
                ## | wx.TR_NO_LINES
        )
        self.tree.watch(self.parent.shellframe.ghost)
        
        self.layout(
            (self.tree,),
            expand=2, border=0, vspacing=0
        )
    
    def Destroy(self):
        try:
            self.tree.unwatch()
        finally:
            return Layer.Destroy(self)


if __name__ == "__main__":
    app = wx.App()
    frm = Frame(None)
    frm.load_plug(Plugin, show=1, dock=5)
    frm.Show()
    app.MainLoop()
