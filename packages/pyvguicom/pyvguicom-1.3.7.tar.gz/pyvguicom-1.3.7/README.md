# pyvguicom  PyV GUI Common utilities

## Common GUI routines and classes

 These classes are for python PyGobject (Gtk) development. They are used in
several projects. They act as a simplification front end for the PyGtk / PyGobject
classes.

A sampler of what is in there (pasted from code, in no particular order):

    class CairoHelper():
    class TextTable(Gtk.Table):
    class TextRow(Gtk.HBox):
    class RadioGroup(Gtk.Frame):
    class Led(Gtk.DrawingArea):
    class SeparatorMenuItem(Gtk.SeparatorMenuItem):
    class Menu():
    class MenuButt(Gtk.DrawingArea):
    class Lights(Gtk.Frame):
    class WideButt(Gtk.Button):
    class ScrollListBox(Gtk.Frame):
    class FrameTextView(Gtk.TextView):
    class Label(Gtk.Label):
    class Logo(Gtk.VBox):
    class xSpacer(Gtk.HBox):
    class ListBox(Gtk.TreeView):

    ... and a lot more ...

## Also includes Some Python / Gtk primitives:

    def get_screen_wh():
    def get_screen_xy():
    def print_exception(xstr):
    def message(strx, parent = None, title = None, icon = Gtk.MessageType.INFO):
    def usleep(msec):
    def tmpname(indir, template):
    def mainloop():
    def time_n2s(ttt):
    def time_s2n(sss):
    def yes_no_cancel(title, message, cancel = True, parent = None):
    def yn_key(win, event, cancel):
    def opendialog(parent=None):
    def savedialog(resp):
    def leadspace(strx):

     ... and a lot more ...

## Example:

The Label Button (SmallButt) takes a constructor, and feeds
 the arguments with defaults as one would expect.

     def __init__(self, textm="", widget=None, tooltip=None, font=None):

The simplification effect allows one to create a Label Button with no arguments,
and still have a somewhat reasonable outcome. The label example is trivial,
the simplification takes a new dimension with classes like SimpleTree.

The defaults are set to a reasonable value, and the named argument(s) can be
set on one line. This makes the code look more compact and maintainable.

## Tests:

 The test utilities can  confirm correct operation; however being a visual
set of classes, the real test is seeing the generated UI.
The test utilities can also be found in the project install directory,
starting with the text* prefix.

 See descendent projects for more examples. (pyedpro; pycal; pyvserv; ...)

 ## History:

    Sat 08.Nov.2025     -- Simplified pyutils
    Tue 11.Nov.2025     -- No default frame for radio buttons

Peter Glen

// EOF
