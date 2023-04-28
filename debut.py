#! python3
# -*- coding: utf-8 -*-
"""deb utilus ver 1.0rc
"""
__version__ = "1.0rc"
__author__ = "Kazuya O'moto <komoto@jeol.co.jp>"

import builtins
import getopt
import sys
import os
import re
import wx
from wx import aui
from wx import stc

import mwx
from mwx.utilus import FSM
from mwx.controls import Icon
from mwx.nutshell import Nautilus, EditorBook
from mwx.py.filling import FillingTree

try:
    from etc import bookshelf
except ImportError:
    from .etc import bookshelf


def subclasses(cls):
    try:
        return cls.__subclasses__()
    except AttributeError:
        pass
builtins.subclasses = subclasses


class monkey_patch:
    ## mwx.__version__ < '0.77.7'
    def atomic(self, obj, key):
        if key == 'DropTarget': # Windows bug fix.
            return False
        try:
            v = getattr(obj, key)
            return not hasattr(v, '__name__') and not key.startswith('__')
        except Exception:
            pass
    FillingTree.filter = atomic


## --------------------------------
## Configuration of Shell / Editor 
## --------------------------------

def init_stc_interface(self):
    """Customize the common keymaps.
    """
    @self.define_key('f9')
    def toggle_wrap_mode():
        mode = ['no-wrap',
                'word-wrap',
                'char-wrap',
                'whitespace-wrap'
                ]
        self.WrapMode = (self.WrapMode + 1) % 4
        self.post_message("\b {!r}".format(mode[self.WrapMode]))

    @self.define_key('C-f9')
    def toggle_folder():
        self.show_folder(not self.is_folder_shown())

    @self.define_key('S-f9')
    def toggle_eol_view():
        self.ViewEOL = not self.ViewEOL
        self.ViewWhiteSpace = not self.ViewWhiteSpace

    self.define_key('C-x [', self.beginning_of_buffer)
    self.define_key('C-x ]', self.end_of_buffer)
    self.define_key('C-x @', self.goto_mark)
    self.define_key('C-c C-c', self.goto_matched_paren)
    self.define_key('C-x C-x', self.exchange_point_and_mark)


def init_buffer(self):
    """Customize the keymaps of the Buffer.
    """
    ## Buffer text control
    init_stc_interface(self)
    
    @self.define_key('enter')
    def newline_and_indent():
        n = self.py_electric_indent()
        self.AddText(os.linesep + ' ' * n)

    @self.define_key('C-enter')
    def newline_and_indent_eol():
        n = self.py_electric_indent()
        self.goto_char(self.eol)
        self.AddText(os.linesep + ' ' * n)

    @self.define_key('C-S-enter')
    @self.define_key('S-enter')
    def open_line_and_indent():
        n = self.py_current_indent()
        self.goto_char(self.bol)
        self.InsertText(self.bol, ' ' * n + os.linesep)
        self.goto_char(self.cpos + n) # relative indentation position

    @self.define_key('M-w')
    def copy_region():
        self.anchor = self.mark
        self.Copy()

    @self.define_key('C-w')
    def kill_region():
        self.anchor = self.mark
        self.Cut()


def init_editor(self):
    """Customize the keymaps of the Editor.
    """
    self.define_key('C-x k',   self.kill_all_buffers)
    self.define_key('C-x C-k', self.kill_buffer)
    self.define_key('C-x C-n', self.new_buffer)
    self.define_key('C-x C-l', self.load_buffer)
    self.define_key('C-x s',   self.save_all_buffers)
    self.define_key('C-x C-s', self.save_buffer)
    self.define_key('C-x S-s', self.save_as_buffer)
    self.define_key('C-x C-f', self.open_buffer) # cf. find-file

    self.define_key('f5', self.load_buffer)

    @self.define_key('C-x up', dir=wx.UP)
    @self.define_key('C-x down', dir=wx.DOWN)
    @self.define_key('C-x left', dir=wx.LEFT)
    @self.define_key('C-x right', dir=wx.RIGHT)
    def split(dir):
        j = self.all_buffers.index(self.CurrentPage)
        self.Split(j, dir)

    @self.define_key('C-x 0')
    def unsplit(v):
        self.move_tab(self.CurrentPage, self.all_tabs[0])


def init_shell(self):
    """Customize the keymaps of the Shell.
    """
    init_stc_interface(self)
    
    @self.define_key('S-enter') # cf. [C-RET] Shell.insertLineBreak
    def open_line():
        self.back_to_indentation()
        p = self.cpos
        self.insertLineBreak()
        self.cpos = self.anchor = p

    @self.define_key('f1')
    def help(v):
        text = self.SelectedText or self.expr_at_caret
        try:
            obj = self.eval(text)
            self.help(obj)
        except Exception:
            v.Skip()

    @self.define_key('f2')
    def load_target():
        text = self.SelectedText or self.expr_at_caret
        if not text:
            self.post_message("No target")
            return
        try:
            obj = self.eval(text)
        except Exception as e:
            self.post_message(f"\b failed: {e!r}")
        else:
            if self.parent.load(obj):
                self.post_message(f"\b {obj!r}")
            else:
                self.post_message(f"\b {text!r} was nowhere to be found.")

    error = r"(?i)^\s+File \"(.+?)\", line ([0-9]+)"
    frame = r"(?i)^\s+file \'(.+?)\', line ([0-9]+)"
    where = r".*>\s+([^*?\"|\r\n]+?):([0-9]+)"
    bp    = r"at \s+([^*?\"|\r\n]+?):([0-9]+)"
    grep = '|'.join((frame, where, bp))

    @self.define_key('f4', pattern=error)
    @self.define_key('f10', pattern=grep)
    def grep_forward(pattern):
        for err in self.grep_forward(pattern):
            target = ':'.join(filter(None, err.groups()))
            if self.parent.load(target, focus=False):
                self.post_message(f"\b {target}")
            break

    @self.define_key('S-f4', pattern=error)
    @self.define_key('S-f10', pattern=grep)
    def grep_barckward(pattern):
        for err in self.grep_barckward(pattern):
            target = ':'.join(filter(None, err.groups()))
            if self.parent.load(target, focus=False):
                self.post_message(f"\b {target}")
            break

    @self.define_key('S-f12')
    def clear_shell():
        self.clear()

    @self.define_key('C-f12')
    def clone_shell():
        self.parent.clone_shell(self.target)

    @self.define_key('M-f12')
    def close_shell():
        self.parent.delete_shell(self)

    @self.define_key('C-f4')
    def HL():
        obj = self.cmdline
        try:
            highlight(self.eval(obj))
        except Exception:
            pass

## --------------------------------
## Setup the console of Nautilus
## --------------------------------

class py_text_mode:
    STYLE = {
        stc.STC_STYLE_DEFAULT     : "fore:#7f7f7f,back:#fffff8,size:9,face:MS Gothic",
        stc.STC_STYLE_LINENUMBER  : "fore:#000000,back:#fffff8,size:9",
        stc.STC_STYLE_BRACELIGHT  : "fore:#000000,back:#cccccc,bold",
        stc.STC_STYLE_BRACEBAD    : "fore:#000000,back:#ff0000,bold",
        stc.STC_STYLE_CONTROLCHAR : "size:6",
        stc.STC_STYLE_CARETLINE   : "fore:#000000,back:#f0f0ff,size:2", # optional
        stc.STC_STYLE_ANNOTATION  : "fore:#7f0000,back:#ff7f7f", # optional
        stc.STC_P_DEFAULT         : "fore:#000000",
        stc.STC_P_OPERATOR        : "fore:#000000",
        stc.STC_P_IDENTIFIER      : "fore:#000000",
        stc.STC_P_COMMENTLINE     : "fore:#007f00,back:#f0fff0",
        stc.STC_P_COMMENTBLOCK    : "fore:#007f00,back:#f0fff0,eol",
        stc.STC_P_NUMBER          : "fore:#e02000",
        stc.STC_P_STRINGEOL       : "fore:#7f7f7f,back:#ffc0c0,eol",
        stc.STC_P_CHARACTER       : "fore:#7f7f7f",
        stc.STC_P_STRING          : "fore:#7f7f7f",
        stc.STC_P_TRIPLE          : "fore:#7f7f7f",
        stc.STC_P_TRIPLEDOUBLE    : "fore:#7f7f7f",
        stc.STC_P_CLASSNAME       : "fore:#7f00ff,bold",
        stc.STC_P_DEFNAME         : "fore:#0000ff,bold",
        stc.STC_P_WORD            : "fore:#0000ff",
        stc.STC_P_WORD2           : "fore:#7f007f",
        stc.STC_P_WORD3           : "fore:#ff0000,back:#ffff00", # optional for search word
        stc.STC_P_DECORATOR       : "fore:#c04040,bold",
    }


class py_interactive_mode:
    STYLE = {
        stc.STC_STYLE_DEFAULT     : "fore:#7f7f7f,back:#202020,size:9,face:MS Gothic",
        stc.STC_STYLE_LINENUMBER  : "fore:#000000,back:#f0f0f0,size:9",
        stc.STC_STYLE_BRACELIGHT  : "fore:#ffffff,back:#202020,bold",
        stc.STC_STYLE_BRACEBAD    : "fore:#ffffff,back:#ff0000,bold",
        stc.STC_STYLE_CONTROLCHAR : "size:6",
        stc.STC_STYLE_CARETLINE   : "fore:#ffffff,back:#123460,size:2", # optional
        stc.STC_STYLE_ANNOTATION  : "fore:#7f0000,back:#ff7f7f", # optional
        stc.STC_P_DEFAULT         : "fore:#cccccc",
        stc.STC_P_OPERATOR        : "fore:#cccccc",
        stc.STC_P_IDENTIFIER      : "fore:#cccccc",
        stc.STC_P_COMMENTLINE     : "fore:#42c18c,back:#004040",
        stc.STC_P_COMMENTBLOCK    : "fore:#42c18c,back:#004040,eol",
        stc.STC_P_NUMBER          : "fore:#ffc080",
        stc.STC_P_STRINGEOL       : "fore:#cccccc,back:#004040,eol",
        stc.STC_P_CHARACTER       : "fore:#a0a0a0",
        stc.STC_P_STRING          : "fore:#a0a0a0",
        stc.STC_P_TRIPLE          : "fore:#a0a0a0,back:#004040",
        stc.STC_P_TRIPLEDOUBLE    : "fore:#a0a0a0,back:#004040",
        stc.STC_P_CLASSNAME       : "fore:#61d6d6,bold",
        stc.STC_P_DEFNAME         : "fore:#3a96ff,bold",
        stc.STC_P_WORD            : "fore:#80c0ff",
        stc.STC_P_WORD2           : "fore:#ff80ff",
        stc.STC_P_WORD3           : "fore:#ff0000,back:#ffff00", # optional for search word
        stc.STC_P_DECORATOR       : "fore:#ff8040",
    }


def stylus(self):
    """Stylize Nautilus window.
    
    Note:
        This function is executed every time you reload.
    """
    ## Customize the keymaps of the ShellFrame.
    self.define_key('C-x C-S-o', self.load_session)
    self.define_key('C-x C-S-s', self.save_session_as)

    @self.define_key('Xbutton1', p=-1)
    @self.define_key('Xbutton2', p=+1)
    @self.define_key('C-x p', p=-1)
    @self.define_key('C-x n', p=+1)
    def other_editor(p=1):
        """Move focus to other topmost notebook page."""
        nb = wx.Window.FindFocus()
        while isinstance(nb.Parent, aui.AuiNotebook):
            nb = nb.Parent
        try:
            if nb.PageCount > 1:
                nb.Selection = (nb.Selection + p) % nb.PageCount
        except AttributeError:
            pass

    @self.define_key('C-d', clear=0)
    @self.define_key('C-S-d', clear=1)
    def duplicate_line(clear=True):
        """Duplicate an expression at the caret-line."""
        buf = wx.Window.FindFocus()
        if not isinstance(buf, stc.StyledTextCtrl):
            return
        text = buf.SelectedText or buf.expr_at_caret or buf.topic_at_caret
        if text:
            shell = self.current_shell
            buf.mark = buf.cpos
            if clear:
                shell.clearCommand() # move to the prompt end
            shell.write(text, -1) # write at the end of command-line
            shell.SetFocus()

    for page in self.get_pages(EditorBook):
        init_editor(page)
        for buffer in page.all_buffers:
            init_buffer(buffer)

    for page in self.get_pages(Nautilus):
        init_shell(page)

    self.Config.set_attributes(Style=py_text_mode.STYLE)
    self.Scratch.set_attributes(Style=py_interactive_mode.STYLE)
    
    ## Don't clear buffer.
    self.Config.undefine_key('C-x k')
    self.Config.undefine_key('C-x C-k')


## --------------------------------
## Main program
## --------------------------------

class MyDataLoader(wx.DropTarget):
    """DnD target loader.
    
    Supports URL text and file data formats.
    """
    def __init__(self, target: EditorBook):
        wx.DropTarget.__init__(self)
        
        self.target = target
        self.textdo = wx.TextDataObject()
        self.filedo = wx.FileDataObject()
        self.DataObject = wx.DataObjectComposite()
        self.DataObject.Add(self.textdo)
        self.DataObject.Add(self.filedo, True)
    
    def OnData(self, x, y, result):
        self.GetData()
        if self.textdo.TextLength > 1:
            text = self.textdo.Text
            if re.match(r"https?://[\w/:%#\$&\?()~.=+-]+", text):
                res = self.target.load_url(text)
                if res:
                    self.target.buffer.SetFocus()
                    result = wx.DragCopy
                elif res is None:
                    self.target.post_message("Load canceled.")
                    result = wx.DragCancel
                else:
                    self.target.post_message("URL not found.")
                    result = wx.DragNone
            else:
                self.target.post_message("Dropped text is not a URL.")
                result = wx.DragNone
            self.textdo.Text = ''
        else:
            for f in self.filedo.Filenames:
                if self.target.load_file(f):
                    self.target.buffer.SetFocus()
                    self.target.post_message(f"Loaded {f!r} successfully.")
            self.filedo.SetData(wx.DF_FILENAME, None)
        return result


def main(self):
    """Initialize Nautilus configuration.
    
    Note:
        This function is executed once at startup.
    """
    ## Config loader extension
    if not hasattr(self, "Config"):
        self.Config = EditorBook(self, name="Config")
        self.Config.load_file(__file__)
        buffer = self.Config.default_buffer
        try:
            buffer._load_file(self.SESSION_FILE)
        except FileNotFoundError:
            buffer._save_file(self.SESSION_FILE)
        self.ghost.AddPage(self.Config, 'Config', bitmap=Icon('proc'))

    self.set_traceable(self.Config) # Bind pointer to enable trace.

    @self.Config.define_key('M-j')
    def eval_buffer():
        """Evaluate this <conf> code and call new stylus"""
        locals = {'self': self}
        self.Config.buffer.py_exec_region(
            locals, locals, self.Config.buffer.filename
        )
        if "main" in locals:
            locals["main"](self)

    ## Stylize all windows
    stylus(self)

    ## Define *new* event handlers.
    for editor in self.get_pages(EditorBook):
        editor.SetDropTarget(MyDataLoader(editor))
        editor.handler.define('buffer_new', init_buffer)
    self.handler.define('shell_new', init_shell)

    ## Bookshelf treeview extension
    if not hasattr(self, "Bookshelf"):
        self.Bookshelf = bookshelf.EditorTreeCtrl(self,
                            style=wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT,
                            name = "Bookshelf")
        self.ghost.AddPage(self.Bookshelf, "Bookshelf", bitmap=Icon('book'))
    
    ## Note: Bookshelf context must be coded in the editor/shell
    ##       after the *new* event handlers is defined above,
    ##       and also after this module is reloaded.
    self.Bookshelf.watch(self.ghost)
    self.Bookshelf.SetDropTarget(MyDataLoader(self.Scratch))

    ## self.post_message("Startup process has completed successfully.")


quote_unqoute = """
    Anything one man can imagine, other man can make real.
    --- Jules Verne (1828--1905)
    """


if __name__ == "__main__":
    session = None
    opts, args = getopt.gnu_getopt(sys.argv[1:], "s:")
    for k, v in opts:
        if k == "-s":
            if not v.endswith(".debrc"):
                v += ".debrc"
            session = v
    if session:
        print(f"Starting session {session!r}")

    app = wx.App()
    frame = mwx.deb(loop=0, debrc=session,
                    introText=__doc__ + quote_unqoute)
    main(frame)
    frame.define_key('f12', frame.rootshell.SetFocus) # Don't close.
    if 1:
        ## If you want debugger skip a specific module,
        ## add the module:str to debugger.skip:set.
        frame.debugger.skip -= {
            mwx.FSM.__module__, # for debugging FSM
        }
        ## Dive into some objects to inspect.
        dive(frame)
    app.MainLoop()
