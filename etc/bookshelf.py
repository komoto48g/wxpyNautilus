import wx
from mwx.utilus import TreeList
from mwx.framework import CtrlInterface
from mwx.nutshell import EditorBook
from mwx.graphman import Layer


class ItemData:
    """Item data for TreeListCtrl
    """
    def __init__(self, root, buffer):
        self.root = root
        self.buffer = buffer
        self._itemId = None #: reference <TreeItemId>


class EditorTreeCtrl(wx.TreeCtrl, CtrlInterface, TreeList):
    """TreeList control
    
    Construct treectrl in the order of tree:list.
    """
    def __init__(self, parent, *args, **kwargs):
        wx.TreeCtrl.__init__(self, parent, *args, **kwargs)
        CtrlInterface.__init__(self)
        TreeList.__init__(self)
        
        self.Font = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        
        self.parent = parent
        self.target = None
        
        self.context = {
            None : {
                   'buffer_new' : [ None, self.on_buffer_new ],
                  'buffer_caps' : [ None, self.on_buffer_caption ],
                 'buffer_saved' : [ None, ],
                'buffer_loaded' : [ None, ],
               'buffer_removed' : [ None, self.on_buffer_removed ],
              'buffer_selected' : [ None, self.on_buffer_selected ],
             'buffer_activated' : [ None, self.on_buffer_selected ],
           'buffer_inactivated' : [ None, ],
          'buffer_filename_set' : [ None, self.on_buffer_file_renamed ],
            },
        }
        
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy)
        
        @self.handler.bind('tab pressed')
        @self.handler.bind('enter pressed')
        def enter(v):
            data = self.GetItemData(self.Selection)
            if data:
                data.buffer.SetFocus()
        
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
    
    ## --------------------------------
    ## TreeList/Ctrl wrapper interface 
    ## --------------------------------
    
    def reset(self, clear=True):
        """Build tree control.
        All items will be rebuilt after clear if specified.
        """
        try:
            self.Freeze()
            if clear:
                self.DeleteAllItems()
                self.AddRoot(self.Name)
            for branch in self:
                self._set_item(self.RootItem, *branch)
        finally:
            self.Thaw()
    
    def _get_item(self, root, key):
        """Returns the first item [root/key] found.
        Note: Items with the same name are not supported.
        """
        item, cookie = self.GetFirstChild(root)
        while item:
            if key == self.GetItemText(item):
                return item
            item, cookie = self.GetNextChild(root, cookie)
    
    def _set_item(self, root, key, *values):
        """Set the item [root/key] with values recursively.
        """
        item = self._get_item(root, key) or self.AppendItem(root, key)
        branches = next((x for x in values if isinstance(x, (tuple, list))), [])
        rest = [x for x in values if x not in branches]
        if rest:
            ## Take the first element assuming it's client data.
            ## Set the item client data. (override as needed)
            self.SetItemData(item, *rest)
        for branch in branches:
            self._set_item(item, *branch)
    
    def SetItemData(self, item, data, *rest):
        """Sets the item client data. (override)"""
        try:
            data._itemId = item
            wx.TreeCtrl.SetItemData(self, item, data)
        except AttributeError:
            pass
    
    ## --------------------------------
    ## Actions for bookshelf interfaces
    ## --------------------------------
    
    def watch(self, target):
        self.unwatch()
        self.target = target
        if self.target:
            for editor in self.target.get_pages(EditorBook):
                editor.handler.append(self.context)
                self[editor.Name] = [[buf.name, ItemData(self, buf)]
                                        for buf in editor.all_buffers]
            self.reset()
    
    def unwatch(self):
        if self.target:
            for editor in self.target.get_pages(EditorBook):
                editor.handler.remove(self.context)
            self.clear()
            self.reset()
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
            self.SelectItem(data._itemId)
    
    def on_buffer_caption(self, buf, caption):
        data = self[f"{buf.parent.Name}/{buf.name}"]
        if data:
            self.SetItemText(data._itemId, caption)
    
    def on_buffer_file_renamed(self, buf, *args):
        for key, data in self.items(): # <-- old key
            if data.buffer is buf:
                self.SetItemText(data._itemId, buf.name)
                for item in self[buf.parent.Name]:
                    if item[1] is data:
                        item[0] = buf.name # --> new key
                        break
                break
    
    def OnSelChanged(self, evt):
        if self and self.HasFocus():
            data = self.GetItemData(evt.Item)
            if data:
                data.buffer.SetFocus()
            self.SetFocus()
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
    from wxpyNautilus import Frame

    app = wx.App()
    frm = Frame(None)
    frm.load_plug(Plugin, show=1, dock=5)
    frm.Show()
    app.MainLoop()
