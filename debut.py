#! python3
# -*- coding: utf-8 -*-
"""deb utilus ver 1.0rc
"""
__version__ = "1.0rc"
__author__ = "Kazuya O'moto <komoto@jeol.co.jp>"

from functools import partial, reduce, wraps
from importlib import reload
import traceback
import builtins
import inspect
import dis
## import operator as op
import sys
import os
import re
import wx
from wx import stc
import mwx
from mwx.controls import Icon
from mwx.nutshell import EditorInterface
from mwx.nutshell import Editor, Nautilus

if 1:
    def do(f, *iterables, **kwargs):
        """
        Usage
        -----
        >>> 5 @range @(do, p, end=',')
        ==> partial(do, p, end=',')(range(5))
        ==> do.results = tuple(p(x, end=',') for x in range(5))
        0,1,2,3,4,
        >>> do.results
        (None, None, None, None, None)
        """
        if not iterables:
            return partial(do, f, **kwargs)
        do.results = tuple(map(partial(f, **kwargs), *iterables))
    
    builtins.do = do
    builtins.reduce = reduce
    builtins.partial = partial

## --------------------------------
## Shell/Editor patch and extension
## to be implemented in the future 
## --------------------------------
if 1:
    Editor.wildcards = [
        "PY files (*.py)|*.py",
        "ALL files (*.*)|*.*",
    ]

    def need_buffer_save_p(self, buf):
        if buf.mtdelta is None:
            return False
        if buf is self.buffer:
            return self.IsModified()
        else:
            ## self.push_current() # need to update current buffer.text
            return buf.text != buf.filetext
    Editor.need_buffer_save_p = need_buffer_save_p

    def confirm_load(self):
        """Confirm the load with the dialog."""
        if self.need_buffer_save_p(self.buffer):
            if wx.MessageBox(
                    "You are leaving unsaved content.\n\n"
                    "Changes to the content will be discarded.\n"
                    "Continue loading?",
                    ## "Load",
                    f"Load {self.buffer.filename}".replace(os.sep, '/'),
                    style=wx.YES_NO|wx.ICON_INFORMATION) != wx.YES:
                self.post_message("The load has been canceled.")
                return None
        return True
    Editor.confirm_load = confirm_load

    def confirm_save(self):
        """Confirm the save with the dialog."""
        if self.buffer.mtdelta:
            if wx.MessageBox(
                    "The file has been modified externally.\n\n"
                    "The contents of the file will be overwritten.\n"
                    "Continue saving?",
                    ## "Save",
                    f"Save {self.buffer.filename}".replace(os.sep, '/'),
                    style=wx.YES_NO|wx.ICON_INFORMATION) != wx.YES:
                self.post_message("The save has been canceled.")
                return None
        elif not self.IsModified():
            self.post_message("No need to save.")
            return False
        return True
    Editor.confirm_save = confirm_save

    def confirm_close(self):
        """Confirm the close with the dialog."""
        if self.need_buffer_save_p(self.buffer):
            if wx.MessageBox(
                    "You are closing unsaved content.\n\n"
                    "Changes to the content will be discarded.\n"
                    "Continue closing?",
                    ## "Close",
                    f"Close {self.buffer.filename}".replace(os.sep, '/'),
                    style=wx.YES_NO|wx.ICON_INFORMATION) != wx.YES:
                self.post_message("The close has been canceled.")
                return None
        return True
    Editor.confirm_close = confirm_close

    def _load(self):
        if not self.confirm_load():
            return None
        f = self.buffer.filename
        p = self.cpos
        if not f:
            self.post_message(f"No file to load.")
            return None
        if self.load_file(f, self.markline+1):
            self.goto_char(p) # restore position
            self.recenter()
            self.post_message(f"Loaded {f!r} successfully.")
            return True
        return False
    Editor.load = _load

    def _save(self):
        if not self.confirm_save():
            return None
        f = self.buffer.filename
        if not f:
            return self.saveas()
        if self.save_file(f):
            self.post_message(f"Saved {f!r} successfully.")
            return True
        return False
    Editor.save = _save

    def _saveas(self):
        name = re.sub("[\\/:*?\"<>|]", '',
                      os.path.basename(self.buffer.filename or ''))
        with wx.FileDialog(self, "Save buffer as",
                defaultFile=name,
                wildcard='|'.join(self.wildcards),
                style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            f = dlg.Path
        if self.save_file(f):
            self.post_message(f"Saved {f!r} successfully.")
            return True
        return False
    Editor.saveas = _saveas

    def _open(self):
        with wx.FileDialog(self, "Open buffer",
                wildcard='|'.join(self.wildcards),
                style=wx.FD_OPEN|wx.FD_MULTIPLE|wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            paths = dlg.Paths
        for f in paths:
            if self.load_file(f):
                self.post_message(f"Loaded {f!r} successfully.")
        return True
    Editor.open = _open

    def _kill_buffer(self):
        if not self.confirm_close():
            return
        self.pop_current()
    Editor.kill_buffer = _kill_buffer

    def _kill_all_buffers(self):
        for buf in filter(self.need_buffer_save_p, self.buffer_list):
            self.swap_buffer(buf)
            if not self.confirm_close():
                return
        self.clear_all()
    Editor.kill_all_buffers = _kill_all_buffers

    def _new_buffer(self):
        buf = self.default_buffer
        if buf.mtdelta is not None: # is saved?
            buf = buf.__class__(self.default_name)
            self.default_buffer = buf
        self.buffer = buf
        self._reset()
        self.push_current()
    Editor.new_buffer = _new_buffer

    def _next_buffer(self):
        j = self.buffer_index
        if j+1 < len(self.buffer_list):
            self.swap_buffer(self.buffer_list[j+1])
    Editor.next_buffer = _next_buffer

    def _prev_buffer(self):
        j = self.buffer_index
        if j > 0:
            self.swap_buffer(self.buffer_list[j-1])
    Editor.previous_buffer = _prev_buffer

if 1:
    def gen_atoms_forward(self, start=0, end=-1):
        if end == -1:
            end = self.TextLength
        q = start
        while q < end:
            p, q, st = self.get_following_atom(q)
            yield self.GetTextRange(p, q)
    EditorInterface.gen_atoms_forward = gen_atoms_forward

    def gen_atoms_backward(self, start=0, end=-1):
        if end == -1:
            end = self.TextLength
        p = end
        while p > start:
            p, q, st = self.get_preceding_atom(p)
            yield self.GetTextRange(p, q)
    EditorInterface.gen_atoms_backward = gen_atoms_backward

## --------------------------------
## Configuration of Shell/Editor
## --------------------------------

def init_editor_interface(self):
    """Customize the keymaps of Editor/Shell.
    
    Note:
        This method defines the *common* interface of Editor/Shell
    """
    self.define_key('C-space', self.set_marker) # set mark and markline
    self.define_key('C-S-space', self.set_line_marker) # set pointer to trace
    self.define_key('C-x @', self.goto_marker)
    self.define_key('C-x S-@', self.goto_line_marker)
    self.define_key('C-x C-x', self.exchange_point_and_mark)
    self.define_key('C-x [', self.beginning_of_buffer)
    self.define_key('C-x ]', self.end_of_buffer)

    self.define_key('C-;', self.comment_out_line)
    self.define_key('C-:', self.uncomment_line)
    self.define_key('C-S-;', self.comment_out_line)
    self.define_key('C-S-:', self.uncomment_line)

    @self.define_key('f9')
    def toggle_wrap_mode():
        mode = ['no-wrap', 'word-wrap', 'char-wrap', 'whitespace-wrap']
        self.WrapMode = (self.WrapMode + 1) % 4
        self.post_message("\b {!r}".format(mode[self.WrapMode]))

    @self.define_key('C-f9')
    def toggle_folder():
        self.show_folder(not self.is_folder_shown())

    @self.define_key('S-f9')
    def toggle_eol_view():
        self.ViewEOL = not self.ViewEOL
        self.ViewWhiteSpace = not self.ViewWhiteSpace


def init_editor(self):
    """Customize the keymaps of the Editor.
    """
    @self.define_key('enter')
    def newline_and_indent():
        n = self.py_electric_indent()
        self.AddText(os.linesep + ' ' * n)

    @self.define_key('C-enter')
    def newline_and_indent():
        n = self.py_electric_indent()
        self.goto_char(self.eol)
        self.AddText(os.linesep + ' ' * n)

    @self.define_key('S-enter')
    def open_line_and_indent_relative():
        n = self.py_current_indent()
        self.goto_char(self.bol)
        self.InsertText(self.bol, ' ' * n + os.linesep)
        self.goto_char(self.cpos + n) # relative indentation position

    ## @self.define_key('S-enter')
    ## def open_line_and_indent_relative():
    ##     self.goto_char(self.bol)
    ##     self.InsertText(self.bol, os.linesep) # open-line
    ##     self.py_indent_line() # indent (Note: Undo is recorded twice)

    @self.define_key('M-w')
    def copy_region():
        self.anchor = self.mark
        self.Copy()

    @self.define_key('C-w')
    def kill_region():
        self.anchor = self.mark
        self.Cut()

    self.define_key('M-up', self.previous_buffer)
    self.define_key('M-down', self.next_buffer)

    self.define_key('C-x k',   self.kill_all_buffers)
    self.define_key('C-x C-k', self.kill_buffer)
    self.define_key('C-x C-n', self.new_buffer)
    self.define_key('C-x C-l', self.load)
    self.define_key('C-x C-s', self.save)
    self.define_key('C-x S-s', self.saveas)
    self.define_key('C-x C-o', self.open)


def init_shell(self):
    """Customize the keymaps of the Shell.
    """
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
            self.post_message(f"No target")
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

    @self.define_key('f4', pattern=r"^\s+File \"(.+?)\", line ([0-9]+)")
    @self.define_key('f10', pattern=r">\s+([^<*?>]+?):([0-9]+)")
    def grep_forward(pattern):
        for err in self.grep_forward(pattern):
            target = ':'.join(err.groups())
            self.parent.load(target, focus=False)
            self.post_message(f"\b {target}")
            break

    @self.define_key('S-f4', pattern=r"^\s+File \"(.+?)\", line ([0-9]+)")
    @self.define_key('S-f10', pattern=r">\s+([^<*?>]+?):([0-9]+)")
    def grep_barckward(pattern):
        for err in self.grep_barckward(pattern):
            target = ':'.join(err.groups())
            self.parent.load(target, focus=False)
            self.post_message(f"\b {target}")
            break

    self.handler.unbind('stc_updated')
    @self.handler.bind('stc_updated') # handler.define
    def on_stc_updated(v):
        ## self.message(self.get_following_atom(self.cpos))
        ## self.message(self.get_preceding_atom(self.cpos))
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


def init_shellframe(self):
    """Customize the keymaps of the ShellFrame.
    """
    try:
        import debut as this
    except ImportError:
        from . import debut as this
    
    @self.define_key('f5')
    def reload_this():
        """Reload this module and initialized components"""
        try:
            self.Config.load()
            reload(this)
            this.stylus(self)
            del self.Config.red_arrow
            return
        except SyntaxError as e:
            filename = e.filename
            lineno = e.lineno
            self.post_message(f"reload failed: {e} at {filename}:{lineno}")
        except Exception as e:
            tb = e.__traceback__
            while tb:
                filename = tb.tb_frame.f_code.co_filename
                lineno = tb.tb_lineno
                tb = tb.tb_next
            self.post_message(f"reload failed: {e} at {filename}:{lineno}")
        if filename == self.Config.buffer.filename:
            self.Config.red_arrow = lineno-1
            self.Config.goto_line(lineno-1)
            self.Config.recenter()
    
    self.reload_this = reload_this

    if __name__ == "__main__":
        self.define_key('f12', self.rootshell.SetFocus) # overwrite close
    self.define_key('S-f12', self.clear_shell)
    self.define_key('C-f12', self.clone_shell)
    self.define_key('M-f12', self.close_shell)

    self.define_key('C-x M-s', self.save_session)

    self.define_key('C-x p', self.other_editor, p=-1) # cf. [Xbutton1]
    self.define_key('C-x n', self.other_editor, p=+1) # cf. [Xbutton2]

    @self.define_key('C-d', clear=0)
    @self.define_key('C-S-d', clear=1)
    def duplicate_line(clear=True):
        """Duplicate an expression at the caret-line"""
        ed = self.current_editor or self.current_shell
        text = ed.SelectedText or ed.expr_at_caret or ed.topic_at_caret
        if text:
            shell = self.current_shell
            ed.mark = ed.cpos
            if clear:
                shell.clearCommand() # move to the prompt end
            shell.write(text, -1) # write at the end of command-line of the shell
            shell.SetFocus()


def stylus(self):
    """Stylize Nautilus window.
    
    Note:
        This function is executed every time you reload.
    """
    init_shellframe(self)

    for page in self.all_pages(Editor):
        init_editor_interface(page)
        init_editor(page)

    for page in self.all_pages(Nautilus):
        init_editor_interface(page)
        init_shell(page)

    self.Config.set_style(py_text_mode.STYLE)
    self.Scratch.set_style(py_interactive_mode.STYLE)
    
    ## Don't clear Config buffer. => after stylus
    self.Config.undefine_key('C-x k')
    self.Config.undefine_key('C-x C-k')


## --------------------------------
## Main program
## --------------------------------

class MyFileDropLoader(wx.FileDropTarget):
    def __init__(self, target):
        wx.FileDropTarget.__init__(self)
        self.target = target
    
    def OnDropFiles(self, x, y, filenames):
        if not self.target.confirm_load():
            return False
        for f in filenames:
            if self.target.load_file(f):
                self.target.post_message(f"Loaded {f!r} successfully.")
        self.target.SetFocus()
        return True


def main(self):
    """Initialize Nautilus configuration.
    
    Note:
        This function is executed once at startup.
    """
    if not hasattr(self, "Config"):
        self.Config = Editor(self, name="Config")
        self.Config.load_file(__file__)
        self.ghost.InsertPage(4, self.Config, 'Config', bitmap=Icon('proc'))
        
        ## Set conf buffer traceable.
        self.set_traceable(self.Config)

    @self.Config.define_key('M-j')
    def eval_buffer():
        """Evaluate this <conf> code and call new stylus"""
        locals = {}
        self.Config.py_exec_region(locals, locals, filename="<conf>")
        if "stylus" in locals:
            locals["stylus"](self)

    stylus(self)

    ## Set scratch window to accept drop-file.
    self.ghost.SetDropTarget(MyFileDropLoader(self.Scratch))

    self.handler.bind('add_shell', init_shell)
    self.handler.bind('add_shell', init_editor_interface)
    self.post_message("Startup process has completed successfully.")


quote_unqoute = """
    Anything one man can imagine, other man can make real.
    --- Jules Verne (1828--1905)
    """

if __name__ == "__main__":
    import numpy as np
    np.set_printoptions(linewidth=256) # default 75
    
    app = wx.App()
    frm = mwx.deb(app=0, introText=__doc__ + quote_unqoute,)
    if 1:
        ## If you want debugger skip a specific module,
        ## add the module:str to debugger.skip:list here.
        frm.debugger.skip.remove(mwx.FSM.__module__) # for debug mwx.utilus
        pass
    frm.Show()
    if 1:
        dive(frm)
        dive(frm.Scratch)
        dive(frm.rootshell)
    main(frm)
    app.MainLoop()
