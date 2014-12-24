# coding: utf-8

# Copyright 2014 Jiří Janoušek <janousek.jiri@gmail.com>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from gi.repository import Gtk


class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Coinamon")
        self.grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL, row_spacing=10)
        self.stack = Gtk.Stack(vexpand=True, hexpand=True)
        self.switcher = Gtk.StackSwitcher(
            stack=self.stack, vexpand=False, hexpand=True, halign=Gtk.Align.CENTER)
        self.grid.add(self.switcher)
        self.grid.add(self.stack)
        self.add(self.grid)
        self.button = Gtk.Button(label="Click Here", vexpand=True, hexpand=True)
        self.button.connect("clicked", self.on_button_clicked)
        self.stack.add_titled(self.button, "button", "Button")
        self.grid.show_all()

    def on_button_clicked(self, widget):
        print("Hello World")
        Gtk.main_quit()
