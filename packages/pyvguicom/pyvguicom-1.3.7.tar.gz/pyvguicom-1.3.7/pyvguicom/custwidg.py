#!/usr/bin/env python

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Pango

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

class SimpleWidget(Gtk.Widget):
    __gtype_name__ = 'ManualWidget'

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.set_size_request(40, 40)
        self.set_can_focus(True)
        self.set_focus_on_click(True)
        self.set_can_default(True)
        self.cnt = 0

        #cr = self.get_window().cairo_create()
        #self.layout = PangoCairo.create_layout(cr)

        self.fd = Pango.FontDescription()
        fam = "Monospace"
        size = 24
        self.fd.set_family(fam)
        self.fd.set_absolute_size(size * Pango.SCALE)
        #self.pangolayout = self.create_pango_layout("a")
        #self.pangolayout.set_font_description(self.fd)

    def do_draw(self, cr):

        allocation = self.get_allocation()

        if self.cnt == 0:
            self.layout = PangoCairo.create_layout(cr)
            self.fd.set_absolute_size(allocation.height / 3 * Pango.SCALE)
            self.layout.set_font_description(self.fd)
        self.cnt += 1
        context = self.get_style_context()
        #print("con", context)

        # paint background
        bg_color = self.get_style_context().get_background_color(Gtk.StateFlags.NORMAL)
        print(bg_color)
        bg_color = Gdk.RGBA(.9, .9, .9, )
        print(bg_color)

        cr.set_source_rgba(*list(bg_color))
        cr.paint()
        Gtk.render_background(context, cr, 0, 0, 100,100)

        # draw a diagonal line
        #fg_color = self.get_style_context().get_color(Gtk.StateFlags.NORMAL)
        fg_color = Gdk.RGBA(.7, .7, .7)
        cr.set_source_rgba(*list(fg_color));
        cr.set_line_width(2)
        cr.move_to(0, 0)   # top left of the widget
        cr.line_to(allocation.width, allocation.height)
        cr.stroke()

        cr.move_to(0, allocation.height)
        cr.line_to(allocation.width, 0)
        cr.stroke()

        fg_color = Gdk.RGBA(.2, .2, .2)
        cr.set_source_rgba(*list(fg_color));

        self.layout.set_text("Hello %d" % self.cnt)
        sss = self.layout.get_size()
        #print("sss", sss[0] / Pango.SCALE, sss[1] / Pango.SCALE )
        xxx = allocation.width  / 2 - (sss[0] / 2) / Pango.SCALE
        yyy = allocation.height / 2 - (sss[1] / 2) / Pango.SCALE

        cr.move_to(xxx, yyy)
        PangoCairo.show_layout(cr, self.layout)
        #Gtk.render_layout(context, cr, xxx, yyy, self.layout)

        #Gtk.render_frame(context, cr, 0, 0, 100,100)
        if self.is_focus():
            Gtk.render_focus(context, cr, 0, 0, allocation.width, allocation.height)
        #Gtk.render_arrow(context, cr, 0, 0, 100,100)

    def do_realize(self):
        allocation = self.get_allocation()
        attr = Gdk.WindowAttr()
        attr.window_type = Gdk.WindowType.CHILD
        attr.x = allocation.x
        attr.y = allocation.y
        attr.width = allocation.width
        attr.height = allocation.height
        attr.visual = self.get_visual()
        attr.event_mask = self.get_events() | Gdk.EventMask.EXPOSURE_MASK
        WAT = Gdk.WindowAttributesType
        mask = WAT.X | WAT.Y | WAT.VISUAL
        window = Gdk.Window(self.get_parent_window(), attr, mask);
        self.set_window(window)
        self.register_window(window)
        self.set_realized(True)
        #window.set_background_pattern(None)


