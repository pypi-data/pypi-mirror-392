#!/usr/bin/env python

import sys, traceback, os, time, warnings

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

import pgutils, pggui, pgtextview

def wrap(cont):
    fr = Gtk.Frame()
    sc = Gtk.ScrolledWindow()
    sc.set_hexpand(True)
    sc.set_vexpand(True)
    sc.add(cont)
    fr.add(sc)
    return fr, cont

class Entryx(Gtk.Entry):

    def __init__(self, noemit = False):
        super(Entryx).__init__()
        Gtk.Entry.__init__(self)
        self.noemit = noemit    # do not emit move next on enter
        self.connect("key-press-event", self.key_press_event)

    def set_noemit(self, flag):
        self.noemit = flag

    def set_gray(self, flag):
        if flag:
            self.set_editable(False);
            style = self.get_style_context()
            color = style.get_background_color(Gtk.StateFlags.NORMAL)
            color2 = Gdk.RGBA(color.red-.1, color.green-.1, color.blue-.1)
            self.override_background_color(Gtk.StateFlags.NORMAL, color2)
        else:
            self.set_editable(True);
            style = self.get_style_context()
            color = style.get_background_color(Gtk.StateFlags.NORMAL)
            self.override_background_color(Gtk.StateFlags.NORMAL, color)

    def  key_press_event(self, arg1, event):
        #print("keypress", event.keyval)
        if event.keyval == Gdk.KEY_Tab or event.keyval == Gdk.KEY_ISO_Left_Tab:
            #print("tab keypress ", event.keyval, event.state)
            if event.state & Gdk.ModifierType.SHIFT_MASK:
                self.emit("move-focus",  Gtk.DirectionType.TAB_BACKWARD)
            else:
                self.emit("move-focus",  Gtk.DirectionType.TAB_FORWARD)
            return True

        if event.keyval == Gdk.KEY_Return:
            if not self.noemit:
                self.emit("move-focus",  Gtk.DirectionType.TAB_FORWARD)
                return True

# Expects two tuples of stuff
# labtext, labname, tip, defval = None:

def entryquad(arr, vbox, entry1, entry2):

    hbox2 = Gtk.HBox(False, 2)

    lab1a = Gtk.Label(label="      ")
    hbox2.pack_start(lab1a, False, 0, 0)
    lab1 = Gtk.Label.new_with_mnemonic(entry1[0]) ; lab1.set_alignment(1, 0)
    lab1.set_tooltip_text(entry1[2])
    hbox2.pack_start(lab1, False, 0, 0)
    lab1a = Gtk.Label(label="      ")
    hbox2.pack_start(lab1a, False, 0, 0)
    headx = Entryx();  headx.set_width_chars(33)
    lab1.set_mnemonic_widget(headx)

    if entry1[3] != None:
        headx.set_text(entry1[3][entry1[1]])
    hbox2.pack_start(headx, True, 0, 0)
    lab3 = Gtk.Label(label="        ")
    hbox2.pack_start(lab3, False, 0, 0)
    arr.append((entry1[1], headx))

    lab1b = Gtk.Label(label="      ")
    hbox2.pack_start(lab1b, False, 0, 0)
    lab2 = Gtk.Label.new_with_mnemonic(entry2[0])  ; lab2.set_alignment(1, 0)
    lab2.set_tooltip_text(entry2[2])
    hbox2.pack_start(lab2, False, 0, 0)
    lab1b = Gtk.Label(label="      ")
    hbox2.pack_start(lab1b, False, 0, 0)
    headx2 = Entryx();  headx2.set_width_chars(33)
    lab2.set_mnemonic_widget(headx2)
    if entry2[3] != None:
        headx2.set_text(entry2[3][entry2[1]])
    hbox2.pack_start(headx2, True, 0, 0)
    lab3b = Gtk.Label(label="        ")
    hbox2.pack_start(lab3b, False, 0, 0)
    arr.append((entry2[1], headx2))

    #self.ySpacer(vbox)
    vbox.pack_start(hbox2, True, True, 0)
    return lab1, lab2

# Create a label entry pair
def entrypair(vbox, labtext, labname, tip, defval = None):

    hbox2 = Gtk.HBox()
    lab1b = Gtk.Label(label="      ")
    hbox2.pack_start(lab1b, False, 0, 0)

    lab1 = Gtk.Label.new_with_mnemonic(labtext) ; lab1.set_alignment(1, 0)
    hbox2.pack_start(lab1, False, 0, 0)

    lab1a = Gtk.Label(label="      ")
    hbox2.pack_start(lab1a, False, 0, 0)

    headx = Gtk.Entry();
    if defval != None:
        headx.set_text(defval[labname])
    lab1.set_mnemonic_widget(headx)

    hbox2.pack_start(headx, True, 0, 0)
    lab3 = Gtk.Label(label="        ")
    hbox2.pack_start(lab3, False, 0, 0)
    arr.append((labname, headx))

    pggui.ySpacer(vbox)
    vbox.pack_start(hbox2, False, 0, 0)
    lab1.set_tooltip_text(tip)

    return lab1

def textviewpair(arr, vbox, labtext, labname, tip, defval=None, expand=False):

    hbox2 = Gtk.HBox();
    pggui.xSpacer(hbox2)

    lab2a = Gtk.Label(label="     ")
    hbox2.pack_start(lab2a, False , 0, 0)

    lab2 = Gtk.Label.new_with_mnemonic(labtext); lab2.set_alignment(1, 0)
    lab2.set_tooltip_text(tip)
    hbox2.pack_start(lab2, False , 0, 0)
    if defval:
        sw = scrolledtext(arr, labname, defval[labname])
    else:
        sw = scrolledtext(arr, labname, defval)

    lab2.set_mnemonic_widget(sw.textx)

    pggui.xSpacer(hbox2)
    hbox2.pack_start(sw, True, True, 0)
    pggui.xSpacer(hbox2)
    pggui.ySpacer(vbox)

    lab2b = Gtk.Label(label="     ")
    hbox2.pack_start(lab2b, False , 0, 0)
    vbox.pack_start(hbox2, True, True, 0)
    return lab2

def gridhexa(gridxx, left, top, entry1, entry2, butt = None, butt2 = None):

    lab1 = Gtk.Label.new_with_mnemonic(entry1[0] + "  ")
    lab1.set_alignment(1, 0)
    lab1.set_tooltip_text(entry1[2])
    gridxx.attach(lab1, left, top, 1, 1)

    headx = Entryx();
    lab1.set_mnemonic_widget(headx)
    headx.set_width_chars(20)
    if entry1[3] != None:
        headx.set_text(entry1[3])
    gridxx.attach(headx, left+1, top, 1, 1)

    if butt:
        gridxx.attach(butt, left+2, top, 1, 1)

    lab2 = Gtk.Label.new_with_mnemonic("  " + entry2[0] + "  ")
    lab2.set_alignment(1, 0)
    lab2.set_tooltip_text(entry2[2])
    gridxx.attach(lab2, left+3, top, 1, 1)

    headx2 = Entryx();
    lab2.set_mnemonic_widget(headx2)

    headx2.set_width_chars(20)
    if entry2[3] != None:
        headx2.set_text(entry2[3])
    gridxx.attach(headx2, left+4, top, 1, 1)
    if butt2:
        gridxx.attach(butt2, left+5, top, 1, 1)
    return headx, headx2

def gridquad(gridx, left, top, entry1, entry2, butt = None):
    lab1 = Gtk.Label.new_with_mnemonic(entry1[0] + "  ")
    warnings.simplefilter("ignore")
    lab1.set_alignment(1, 0)
    warnings.simplefilter("default")
    lab1.set_tooltip_text(entry1[2])
    gridx.attach(lab1, left, top, 1, 1)

    headx = Entryx();
    lab1.set_mnemonic_widget(headx)
    headx.set_width_chars(20)
    if entry1[3] != None:
        headx.set_text(entry1[3])
    gridx.attach(headx, left+1, top, 1, 1)

    lab2 = Gtk.Label.new_with_mnemonic("  " + entry2[0] + "  ")
    lab2.set_alignment(1, 0)
    lab2.set_tooltip_text(entry2[2])
    gridx.attach(lab2, left+2, top, 1, 1)

    headx2 = Entryx();
    lab2.set_mnemonic_widget(headx2)

    headx2.set_width_chars(20)
    if entry2[3] != None:
        headx2.set_text(entry2[3])
    gridx.attach(headx2, left+3, top, 1, 1)
    if butt:
        gridx.attach(butt, left+4, top, 1, 1)
    return headx, headx2

def griddouble(gridx, left, top, entry1, buttx = None):
    lab1 = Gtk.Label.new_with_mnemonic(entry1[0] + "   ")
    lab1.set_alignment(1, 0)
    lab1.set_tooltip_text(entry1[2])
    gridx.attach(lab1, left, top, 1, 1)

    headx = Entryx();
    lab1.set_mnemonic_widget(headx)
    headx.set_width_chars(40)
    if entry1[3] != None:
        headx.set_text(entry1[3])
    gridx.attach(headx, left+1, top, 2, 1)
    if buttx:
        gridx.attach(buttx, left+3, top, 1, 1)
    return headx

class   TextViewx(Gtk.TextView):

    ''' Override textview for simple deployment '''

    def __init__(self):
        super(TextViewx).__init__()
        GObject.GObject.__init__(self)
        self.buffer = Gtk.TextBuffer()
        self.set_buffer(self.buffer)
        self.single_line = False
        self.connect("key-press-event", self.key_press_event)

    def  key_press_event(self, arg1, event):

        ''' Override tabs '''

        if event.keyval == Gdk.KEY_Tab or event.keyval == Gdk.KEY_ISO_Left_Tab:
            #print("tab keypress ", event.keyval, event.state)
            if event.state & Gdk.ModifierType.SHIFT_MASK:
                self.emit("move-focus",  Gtk.DirectionType.TAB_BACKWARD)
            else:
                self.emit("move-focus",  Gtk.DirectionType.TAB_FORWARD)
            return True

        # If reached last line, TAB it
        if event.keyval == Gdk.KEY_Down:
            pos = self.buffer.get_property("cursor-position")
            #print("Down", pos)
            #print(self.buffer.list_properties())
            sss = self.buffer.get_start_iter()
            eee = self.buffer.get_end_iter()
            textx = self.buffer.get_text(sss, eee, True)
            if pos == len(textx):
                self.emit("move-focus",  Gtk.DirectionType.TAB_FORWARD)
                return True

        # If reached first line, TAB it
        if event.keyval == Gdk.KEY_Up:
            # Are we at the beginning:
            pos = self.buffer.get_property("cursor-position")
            #print("Up", pos)
            if pos == 0:
                self.emit("move-focus",  Gtk.DirectionType.TAB_BACKWARD)
                return True

        if event.keyval == Gdk.KEY_Return:
            if event.state & Gdk.ModifierType.SHIFT_MASK:
                #print("keypress shift ", event)
                self.emit("move-focus",  Gtk.DirectionType.TAB_FORWARD)
                return True

    def get_text(self):
        startt = self.buffer.get_start_iter()
        endd = self.buffer.get_end_iter()
        return self.buffer.get_text(startt, endd, False)

    def set_text(self, txt, eventx = False):
        if eventx:
            self.check_saved()
        startt = self.buffer.get_start_iter()
        endd = self.buffer.get_end_iter()
        self.buffer.delete(startt, endd)
        self.buffer.insert(startt, txt)
        self.buffer.set_modified(True)

def gridsingle(gridx, left, top, entry1):
    lab1 = Gtk.Label.new_with_mnemonic(entry1[0] + "   ")
    lab1.set_alignment(1, 0)
    lab1.set_tooltip_text(entry1[2])
    gridx.attach(lab1, left, top, 1, 1)

    headx, cont = wrap(TextViewx())
    lab1.set_mnemonic_widget(cont)

    if entry1[3] != None:
         headx.set_text(entry1[3])
    gridx.attach(headx, left+1, top, 3, 1)

    return cont

def scrolledtext(arr, name, body = None):
    textx = Gtk.TextView();
    textx.set_border_width(4)
    arr.append((name, textx))
    if body != None:
        #textx.grab_focus()
        buff = Gtk.TextBuffer(); buff.set_text(body)
        textx.set_buffer(buff)

    sw = Gtk.ScrolledWindow()
    sw.textx = textx
    sw.add(textx)
    sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
    sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    return sw

def imgbutt(imgfile, txt, func, win):
    hbb = Gtk.HBox(); vbb = Gtk.VBox();  ic = Gtk.Image();
    ic.set_from_file(imgfile)
    pb = ic.get_pixbuf();
    #pb2 = pb.scale_simple(150, 150, GdkPixbuf.InterpType.BILINEAR)
    pb2 = pb.scale_simple(150, 150, 0)
    ic2 = Gtk.Image.new_from_pixbuf(pb2)
    butt1d = Gtk.Button.new_with_mnemonic(txt)
    butt1d.connect("clicked", func, win)

    vbb.pack_start(Gtk.Label(label=" "), True, True, 0)
    vbb.pack_start(ic2, False, 0, 0)
    vbb.pack_start(Gtk.Label(label=" "), True, True, 0)
    vbb.pack_start(butt1d, False, 0, 0)
    vbb.pack_start(Gtk.Label(label=" "), True, True, 0)

    hbb.pack_start(Gtk.Label(label="  "), True, True, 0)
    hbb.pack_start(vbb, True, True, 0)
    hbb.pack_start(Gtk.Label(label="  "), True, True, 0)

    return hbb

# eof
