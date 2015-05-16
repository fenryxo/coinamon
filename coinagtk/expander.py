# coding: utf-8

# Copyright 2015 Jiří Janoušek <janousek.jiri@gmail.com>
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

from gi.repository import GObject
from gi.repository import Gtk


class Expander(Gtk.Grid):
    label_widget = GObject.property(type=Gtk.Widget, default=None)

    @classmethod
    def new(cls):
        return cls()

    def __init__(self, **kwargs):
        Gtk.Grid.__init__(self, column_spacing=10, row_spacing=0, **kwargs)
        self._revealer = Gtk.Revealer(transition_type=Gtk.RevealerTransitionType.SLIDE_DOWN)
        self._arrow = Gtk.Image.new_from_icon_name("pan-end-symbolic", Gtk.IconSize.BUTTON)
        self._arrow.set_padding(0, 0)
        self._arrow.set_alignment(0.5, 0.5)
        self._arrow.set_hexpand(True)
        self._arrow.set_vexpand(True)
        self._button = Gtk.Button(
            vexpand=False, hexpand=False, valign=Gtk.Align.CENTER, halign=Gtk.Align.START,
            relief=Gtk.ReliefStyle.NONE)
        self._button.set_image(self._arrow)
        self.attach(self._button, 0, 0, 1, 1)
        self._button.show_all()
        self.attach(self._revealer, 1, 1, 1, 1)
        self._revealer.show()
        if self.label_widget:
            self.attach(self.label_widget, 1, 0, 1, 1)
        self._button.connect("clicked", self._on_button_clicked)

    def add(self, widget):
        self._revealer.add(widget)

    def remove(self, widget):
        self._revealer.remove(widget)

    def do_set_property(self, prop, value):
        if prop.name == 'label-widget':
            if self.label_widget is not None:
                super().remove(self.label_widget)
            self.label_widget = value
            if value:
                self.attach(value, 1, 0, 1, 1)
        else:
            Gtk.Grid.do_set_property(self, prop, value)

    def _on_button_clicked(self, button):
        revealed = not self._revealer.props.reveal_child
        self._revealer.props.reveal_child = revealed
        icon_name = "pan-end-symbolic" if not revealed else "pan-down-symbolic"
        self._arrow.set_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
