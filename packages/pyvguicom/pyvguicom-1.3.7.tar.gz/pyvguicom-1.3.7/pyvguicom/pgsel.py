
#!/usr/bin/python

import  sys

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Pango

''' Simplified controls '''

gui_testmode = False

import pgutils, pggui

# ------------------------------------------------------------------------
# Letter selection control

class   LetterNumberSel(Gtk.VBox):

    ''' Letter Number selector '''

    def __init__(self, callb = None, font="Mono 13", pad = ""):

        Gtk.VBox.__init__(self)

        self.set_can_focus(True)
        self.set_focus_on_click(True)
        self.set_can_default(True)

        self.callb = callb

        self.frame = Gtk.Frame()

        hbox3a = Gtk.HBox()
        hbox3a.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        strx = "abcdefghijklmnopqrstuvwxyz"
        self.simsel =  internal_SimpleSel(strx, self.lettercb, font, pad)
        #self.override_background_color(Gtk.StateFlags.FOCUSED, Gdk.RGBA(.9,.9,.9))

        self.connect("key-press-event", self.simsel_key)
        self.connect("key-release-event", self.simsel_key_rel)

        hbox3a.pack_start(self.simsel, 0, 0, 0)
        hbox3a.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        strn2 = ""
        hbox3b = Gtk.HBox()
        hbox3b.pack_start(Gtk.Label(label="  "), 1, 1, 0)
        strn = "1234567890!@#$^*_-+"
        self.simsel2 = internal_SimpleSel(strn, self.lettercb, font, pad)
        hbox3b.pack_start(self.simsel2, 0, 0, 0)

        self.simall = internal_AllSel("All", self.lettercb, font, pad)
        hbox3b.pack_start(self.simall, 0, 0, 0)
        hbox3b.pack_start(Gtk.Label(label="  "), 1, 1, 0)

        self.simsel2.other = self.simsel
        self.simsel.other = self.simsel2

        self.simsel2.other2 = self.simall
        self.simsel.other2  = self.simall

        self.simall.other   = self.simsel
        self.simall.other2  = self.simsel2

        self.curr = self.simsel
        # Commit changes
        self.simsel.exec_index(True)

        self.hand_cursor = Gdk.Cursor(Gdk.CursorType.HAND2)
        self.simsel.connect("enter_notify_event", self.enter_label)
        self.simsel.connect("leave_notify_event", self.leave_label)
        self.simsel2.connect("enter_notify_event", self.enter_label)
        self.simsel2.connect("leave_notify_event", self.leave_label)

        self.connect("focus_in_event", self.focus_label)
        self.connect("focus_out_event", self.focus_out_label)

        vbox = Gtk.VBox()
        vbox.pack_start(hbox3a, 0, 0, False)
        #vbox.pack_start(pggui.ySpacer(), 0, 0, False)
        vbox.pack_start(hbox3b, 0, 0, False)

        self.frame = Gtk.Frame()
        self.frame.set_shadow_type(Gtk.ShadowType.NONE)

        self.frame.add(vbox)
        self.pack_start(self.frame, 0, 0, False)

    def focus_label(self, arg, arg2):
        #print("focus in")
        self.frame.set_shadow_type(Gtk.ShadowType.OUT)

    def focus_out_label(self, arg, arg2):
        #print("focus out")
        self.frame.set_shadow_type(Gtk.ShadowType.NONE)

    def simsel_key_rel(self, arg, event):
        if event.keyval == Gdk.KEY_Return or event.keyval == Gdk.KEY_space:
            return True

    def simsel_key(self, arg, event):

        #  print(event.keyval)

        if event.keyval == Gdk.KEY_Left:
            self.curr.idx -= 1
            if self.curr.idx < 0:
                #print("Skip left")
                if self.curr == self.simsel:
                    self.curr = self.simall
                    self.curr.idx = len(self.curr.textarr)-1
                elif self.curr == self.simall:
                    self.curr = self.simsel2
                    self.curr.idx = len(self.curr.textarr)-1
                else:
                    self.curr = self.simsel
                    self.curr.idx = len(self.curr.textarr)-1
            self.curr.exec_index(True)
            return True

        if event.keyval == Gdk.KEY_Right:
            self.curr.idx += 1
            if self.curr.idx >= len(self.curr.textarr):
                #print("Skip right")
                if self.curr == self.simsel:
                    self.curr = self.simsel2
                    self.curr.idx = 0
                elif self.curr == self.simsel2:
                    self.curr = self.simall
                    self.curr.idx = 0
                else:
                    self.curr = self.simsel
                    self.curr.idx = 0
            self.curr.exec_index(True)
            return True

        if event.keyval == Gdk.KEY_Down:
            if self.curr == self.simsel:
                self.curr = self.simsel2
                self.curr.exec_index(True)
            else:
                # Thu 02.May.2024 tab instead
                self.emit("move-focus",  Gtk.DirectionType.TAB_FORWARD)
            return True

        if event.keyval == Gdk.KEY_Up:
            if self.curr == self.simsel2:
                self.curr = self.simsel
                self.curr.exec_index(True)
            else:
                # Thu 02.May.2024 tab instead
                self.emit("move-focus",  Gtk.DirectionType.TAB_BACKWARD)
            return True

        if event.keyval == Gdk.KEY_Home:
            self.curr.idx = 0
            self.curr.exec_index(True)
            return True

        if event.keyval == Gdk.KEY_End:
            self.curr.idx = len(self.curr.textarr) - 1
            self.curr.exec_index(True)
            return True

        if event.keyval == Gdk.KEY_Return or event.keyval == Gdk.KEY_space:
            self.curr.exec_index(False)
            return True

        if event.keyval >= Gdk.KEY_a and event.keyval <= Gdk.KEY_z:
            self.curr.idx = event.keyval - Gdk.KEY_a
            self.curr.exec_index(True)
            return True

    def enter_label(self, arg, arg2):
        #print("Enter")
        self.get_window().set_cursor(self.hand_cursor)

    def leave_label(self, arg, arg2):
        #print("Leave")
        self.get_window().set_cursor()

    def  lettercb(self, letter):
        #print("LetterSel::letterx:", letter)
        if self.callb:
            self.callb(letter)

# Select character by index (do not call directly)

class   internal_AllSel(Gtk.Label):

    ''' Internal class for selectors '''

    def __init__(self, textx = " ", callb = None, font="Mono 13", pad = ""):

        Gtk.Label.__init__(self, "")

        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK )
        self.connect("button-press-event", self.area_button)
        self.modify_font(Pango.FontDescription(font))
        self.set_has_window(True)
        self.text = textx
        #self.textarr = [" " + textx + " ", "[" + textx + "]"]
        self.textarr = [textx]
        self.org = " "  + textx + " "
        self.callb = callb
        self.lastsel = ""
        self.lastidx = 0
        self.other = None
        self.other2 = None
        self.pad = pad
        self.newtext = pad
        self.idx = -1
        self.set_can_focus(True)
        self.set_focus_on_click(True)
        self.fill() #self.set_text(self.org)

    def fill(self):
        if self.idx == 0:
            self.text = "[" + self.org[1:-1] + "]"
        else:
            self.text = " " + self.org[1:-1] + " "
        self.set_text(self.text)

    def area_button(self, but, event):

        self.get_parent().get_parent().grab_focus()
        #print("allbutt")
        self.idx = 0
        self.fill()
        if 1: #not fromkey:
            if self.callb:
                self.callb(self.textarr[self.idx])

    def exec_index(self, fromkey):

        self.fill()

        # Fill others, if allocated
        if self.other:
           self.other.idx = -1
           self.other.fill()
        if self.other2:
           self.other2.idx = -1
           self.other2.fill()

        if not fromkey:
            if self.callb:
                self.callb(self.textarr[self.idx])

class   internal_SimpleSel(Gtk.Label):

    ''' Internal class for selectors '''

    def __init__(self, textx = " ", callb = None, font="Mono 13", pad = ""):

        Gtk.Label.__init__(self, "")

        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK )
        self.connect("button-press-event", self.area_button)
        self.modify_font(Pango.FontDescription(font))
        self.set_has_window(True)

        self.callb = callb

        self.lastsel = ""
        self.lastidx = 0
        self.other = None
        self.other2 = None
        self.pad = pad
        self.newtext = pad
        self.idx = 0
        self.set_can_focus(True)
        self.set_focus_on_click(True)

        self.textarr = []
        for aa in textx:
            self.textarr.append(aa)

        self.fill()

    def area_button(self, but, event):

        self.get_parent().get_parent().grab_focus()
        www = self.get_allocation().width
        pitch = float(www) / len(self.textarr)
        #print("pitch", pitch, "www", www, "len",
        #    len(self.textarr), "event.x", event.x)

        # Map point to position
        self.idx = int(event.x / pitch)
        #print("idxx:", idxx, self.idx)
        self.exec_index(False)

    def _fill2(self, xarr, xidx, padx):
        ''' Internal '''
        cnt = 0
        newtext = ""
        for aa in xarr:
            if cnt == xidx:
                newtext +=  self.pad + "<span weight='bold' " \
                            "underline='double'>" + aa.upper() + "</span>"
            else:
                newtext += self.pad + aa
            cnt += 1
        newtext += self.pad
        return newtext

    def fill(self):
        self.newtext = self._fill2(self.textarr, self.idx, self.pad)
        self.set_markup(self.newtext)

    def exec_index(self, fromkey):

        if self.idx < 0:
            self.idx = 0
        if self.idx > len(self.textarr) - 1:
            self.idx = len(self.textarr) - 1
        #print("index:", self.idx)
        self.fill()

        # Fill others, if allocated
        if self.other:
           self.other.idx = -1
           self.other.fill()
        if self.other2:
           self.other2.idx = -1
           self.other2.fill()

        if not fromkey:
            if self.callb:
                self.callb(self.textarr[self.idx])

class   NumberSel(Gtk.Label):

    ''' Number selector. Give a proportional answer from mouse position '''

    def __init__(self, text = " ", callb = None, font="Mono 13"):
        self.text = text
        self.callb = callb
        self.axx = self.text.find("[All]")
        Gtk.Label.__init__(self, text)
        self.set_has_window(True)
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK )
        self.connect("button-press-event", self.area_button)
        self.override_font(Pango.FontDescription(font))
        self.lastsel = 0

    def area_button(self, but, event):

        #print("sss =", self.get_allocation().width)
        #print("click", event.x, event.y)

        prop = event.x / float(self.get_allocation().width)
        idx = int(prop * len(self.text))

        # Navigate to IDX
        if self.text[idx] == " ":
            idx += 1
        else:
            if self.text[idx-1] != " ":
                idx -= 1
        if idx >= len(self.text):
            return
        if idx < 0:
            idx = 0
        try:
            # See of it is all
            if self.axx >= 0:
                if idx > self.axx:
                    #print("all", idx, self.text[idx-5:idx+7])
                    self.lastsel =  "All"
                    self.newtext = self.text[:self.axx] + self.text[self.axx:].upper()
                    self.set_text(self.newtext)
                else:
                    self.newtext = self.text[:self.axx] + self.text[self.axx:].lower()
                    self.set_text(self.newtext)

            else:
                self.lastsel =  self.text[idx:idx+2]
                #print("lastsel", self.lastsel)
                self.newtext = self.text[:idx] + self.text[idx].upper() + self.text[idx+1:]
                self.set_text(self.newtext)

            if self.callb:
                self.callb(self.lastsel)

        except:
            print(sys.exc_info())

class   HourSel(Gtk.VBox):

    ''' Hour selector '''

    def __init__(self, callb = None):

        Gtk.VBox.__init__(self)
        self.callb = callb

        strx = " 8 10 12 14 16 "
        hbox3a = Gtk.HBox()
        hbox3a.pack_start(Gtk.Label(label=" "), 1, 1, 0)
        self.simsel = NumberSel(strx, self.lettercb)
        hbox3a.pack_start(self.simsel, 0, 0, 0)
        hbox3a.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        self.pack_start(hbox3a, 0, 0, False)

    def  lettercb(self, letter):
        #print("LetterSel::letterx:", letter)
        if self.callb:
            self.callb(letter)

class   MinSel(Gtk.VBox):

    ''' Minute selector '''

    def __init__(self, callb = None):

        Gtk.VBox.__init__(self)
        self.callb = callb

        strx = " 0 10 20 30 40 50 "
        hbox3a = Gtk.HBox()
        hbox3a.pack_start(Gtk.Label(label=" "), 1, 1, 0)
        self.simsel = NumberSel(strx, self.lettercb)
        hbox3a.pack_start(self.simsel, 0, 0, 0)
        hbox3a.pack_start(Gtk.Label(label=" "), 1, 1, 0)

        self.pack_start(hbox3a, 0, 0, False)

    def  lettercb(self, letter):
        #print("LetterSel::letterx:", letter)
        if self.callb:
            self.callb(letter)

