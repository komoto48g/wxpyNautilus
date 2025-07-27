# ShellFrame GUI

Nautilus consists of three notebook windows.

1.  **Console**, a multi-page shells based on ``wx.py.shell.Shell``

1.  **Ghost**, a helper window consists of multi-buffer editors, monitor, and inspector panes:

    * Eitors (Scratch, Log, Help, History, and Config)
    * Bookshelf

1.  **Watchdog**

    * Globals and locals watchers
    * Event monitor based on ``wx.lib.eventwatcher.EventWatcher``
    * Widget inspector based on ``wx.lib.inspection.InspectionTool``

![image](_images/1a_shellframe.png)


## Ghost in the shell

### Scratch

**Scratch** window is a scratch notebook of code snippets similar to emacs ``*scratch*`` buffer.
You can open, close, and save the script file in the buffer.


### Log

**Log** window is a logger of debugger and is used to view frames.
**Log** window is also used to display history of shells input.
The history shows the actual command text pushed to the interpreter.


### Help

**Help** window is a viewer of help string.
Nautilus doesn't display help text in the shell as normal interpreters, but piped them to the help buffer.


## Watchdog in the shell

### Wahtchers for globals and locals

Watchers for **globals** and **locals** show the list in debug mode.


### Monitor

**Monitor** window is used to display wx widgets events, based on ``wx.lib.eventwatcher.EventWatcher``.


### Inspector

**Inspector** window is used to display wx widgets tree, based on ``wx.lib.inspection.InspectionTool``.


