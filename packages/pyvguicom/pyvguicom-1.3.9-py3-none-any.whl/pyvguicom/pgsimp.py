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

import pgutils

# ------------------------------------------------------------------------

class   SimpleTree(Gtk.TreeView):

    ''' Simplified Tree control '''

    def __init__(self, head = [], editx = [], skipedit = 0, xalign = 0.5):

        Gtk.TreeView.__init__(self)

        self.callb = None
        self.chcallb = None
        self.actcallb = None

        # repair missing column
        if len(head) == 0:
            head.append("")

        if len(editx) == 0:
            editx.append("")

        self.types = []
        for aa in head:
            self.types.append(str)

        self.treestore = Gtk.TreeStore()
        self.treestore.set_column_types(self.types)

        cnt = 0
        for aa in head:
            # Create a CellRendererText to render the data
            cell = Gtk.CellRendererText()
            cell.set_property("alignment", Pango.Alignment.LEFT)
            cell.set_property("align-set", True)
            cell.set_property("xalign", xalign)

            if cnt > skipedit:
                cell.set_property("editable", True)
                cell.connect("edited", self.text_edited, cnt)

            tvcolumn = Gtk.TreeViewColumn(aa)
            tvcolumn.pack_start(cell, True)
            tvcolumn.add_attribute(cell, 'text', cnt)
            self.append_column(tvcolumn)
            cnt += 1

        self.set_model(self.treestore)
        self.connect("cursor-changed", self.selection)
        self.connect("row-activated", self.activate)

    def activate(self, xtree, arg2, arg3):
        #print("Activated", row, arg2, arg3)
        sel = xtree.get_selection()
        xmodel, xiter = sel.get_selected()
        if xiter:
            xstr = xmodel.get_value(xiter, 0)
            #print("Activated str", xstr)
            if self.actcallb:
                self.actcallb(xstr)

    def text_edited(self, widget, path, text, idx):
        #print ("edited", widget, path, text, idx)
        self.treestore[path][idx] = text
        args = []
        for aa in self.treestore[path]:
            args.append(aa)
        if self.chcallb:
            self.chcallb(args)

    def selection(self, xtree):
        #print("simple tree sel", xtree)
        sel = xtree.get_selection()
        xmodel, xiter = sel.get_selected()
        if xiter:
            self.args = []
            for aa in range(len(self.types)):
                xstr = xmodel.get_value(xiter, aa)
                self.args.append(xstr)
            #print("selection", self.args)
            if self.callb:
                self.callb(self.args)

    def setcallb(self, callb):
        self.callb = callb

    def setCHcallb(self, callb):
        self.chcallb = callb

    def setActcallb(self, callb):
        self.actcallb = callb

    def append(self, args, parent = None):
        #print("append", args)
        piter = self.treestore.append(parent, args)
        return piter

    # TreeStore
    def insert(self, parent, pos, args):
        print("insert", parent, pos, args)
        piter = self.treestore.insert(parent, pos, args)
        return piter

    def sel_first(self):
        #print("sel first ...")
        sel = self.get_selection()
        xmodel, xiter = sel.get_selected()
        iterx = self.treestore.get_iter_first()
        sel.select_iter(iterx)
        ppp = self.treestore.get_path(iterx)
        self.set_cursor(ppp, self.get_column(0), False)
        pgutils.usleep(5)
        self.scroll_to_cell(ppp, None, 0, 0, 0 )

    def sel_last(self):
        #print("sel last ...")
        sel = self.get_selection()
        xmodel, xiter = sel.get_selected()
        iterx = self.treestore.get_iter_first()
        if not iterx:
            return
        while True:
            iter2 = self.treestore.iter_next(iterx)
            if not iter2:
                break
            iterx = iter2.copy()
        sel.select_iter(iterx)
        ppp = self.treestore.get_path(iterx)
        self.set_cursor(ppp, self.get_column(0), False)
        pgutils.usleep(5)
        self.scroll_to_cell(ppp, None, True, 0., 0. )
        #sel.select_path(self.treestore.get_path(iterx))

    def find_item(self, item):

        ''' find if we already have an item like that '''

        #print("find", item)
        found = 0
        iterx = self.treestore.get_iter_first()
        if not iterx:
            return found
        while True:
            value = self.treestore.get_value(iterx, 0)
            #print("item:", value)
            if item == value:
                found = True
                break
            iter2 = self.treestore.iter_next(iterx)
            if not iter2:
                break
            iterx = iter2.copy()
        return found

    def clear(self):
        self.treestore.clear()

# ------------------------------------------------------------------------

class   SimpleEdit(Gtk.TextView):

    ''' Simplified Edit controol '''

    def __init__(self, head = []):

        Gtk.TextView.__init__(self)
        self.buffer = Gtk.TextBuffer()
        self.set_buffer(self.buffer)
        self.set_editable(True)
        self.connect("unmap", self.unmapx)
        #self.connect("focus-out-event", self.focus_out)
        self.connect("key-press-event", self.area_key)
        self.modified = False
        self.text = ""
        self.savecb = None
        self.single_line = False

    def focus_out(self, win, arg):
        #print("SimpleEdit focus_out")
        self.check_saved()
        #self.mefocus = False

    def check_saved(self):
        if not self.buffer.get_modified():
            return
        #print("Saving")
        startt = self.buffer.get_start_iter()
        endd = self.buffer.get_end_iter()
        self.text = self.buffer.get_text(startt, endd, False)
        if self.savecb:
            self.savecb(self.text)

    def focus_in(self, win, arg):
        pass
        #self.buffer.set_modified(False)
        #self.mefocus = True
        #print("SimpleEdit focus_in")

    def unmapx(self, widget):
        #print("SimpleEdit unmap", widget)
        pass

    def area_key(self, widget, event):
        #print("SimpleEdit keypress", event.string)
        #self.buffer.set_modified(True)

        if self.single_line:
            if event.string == "\r":
                #print("newline")
                if self.savecb:
                    try:
                        self.savecb(self.get_text())
                    except:
                        print("Error simpledit callback")
                return True

    def append(self, strx):
        self.check_saved()
        iterx = self.buffer.get_end_iter()
        self.buffer.insert(iterx, strx)
        self.buffer.set_modified(False)

    def clear(self):
        self.check_saved()
        startt = self.buffer.get_start_iter()
        endd = self.buffer.get_end_iter()
        self.buffer.delete(startt, endd)
        self.buffer.set_modified(False)

    def setsavecb(self, callb):
        self.savecb = callb

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


# EOF
