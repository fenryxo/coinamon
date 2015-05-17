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

from collections import OrderedDict

from gi.repository import Gio
from gi.repository import Gtk


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self):
        Gtk.ApplicationWindow.__init__(self, title="Coinamon")
        self.set_default_size(800, 600)
        self.header_bar = Gtk.HeaderBar(visible=True, show_close_button=True)
        self.set_titlebar(self.header_bar)
        self.grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL, row_spacing=10)
        self.stack = Gtk.Stack(
            transition_type=Gtk.StackTransitionType.SLIDE_LEFT_RIGHT, vexpand=True, hexpand=True)
        self.switcher = Gtk.StackSwitcher(
            stack=self.stack, vexpand=False, hexpand=True, halign=Gtk.Align.CENTER, visible=True)
        self.header_bar.set_custom_title(self.switcher)
        self.grid.add(self.stack)
        self.add(self.grid)
        self.grid.show_all()
        self.views = OrderedDict()
        self.visible_child = None
        self.stack.connect("notify::visible-child-name", self.on_stack_child_changed)

        self.menu_button = Gtk.MenuButton()
        self.menu_button.set_image(Gtk.Image.new_from_icon_name(
            "emblem-system-symbolic", Gtk.IconSize.SMALL_TOOLBAR))
        self.menu_button.set_menu_model(Gio.Menu())
        self.header_bar.pack_end(self.menu_button)

    def add_menu_item(self, path, detailed_action):
        path = list(s.strip() for s in path.split("/") if s.strip())
        label = path.pop()
        item = Gio.MenuItem.new(label, detailed_action)

        gear_menu = menu = self.menu_button.get_menu_model()
        for label in path:
            gmenu_label = "'{}'".format(label)
            parent, menu = menu, None
            for i in range(parent.get_n_items()):
                parent_label = str(parent.get_item_attribute_value(i, "label"))
                print(parent_label, label)
                if parent_label == gmenu_label:
                    menu = parent.get_item_link(i, "submenu")
                    break

            if menu is None:
                menu = Gio.Menu()
                parent.append_submenu(label, menu)

        menu.append_item(item)
        if gear_menu.get_n_items():
            self.menu_button.show()

    def add_view(self, view, show=False):
        try:
            actions = view.__class__.Actions
            for action in actions.__dict__.values():
                if isinstance(action, Gio.Action):
                    self.add_action(action)
        except AttributeError:
            pass

        self.views[view.name] = view
        view.widget.show()
        self.stack.add_titled(view.widget, view.name, view.label)
        if show:
            self.stack.set_visible_child(view.widget)

    def on_stack_child_changed(self, stack, *args):
        if self.visible_child:
            self.disable_actions(self.views[self.visible_child])
        for child in self.header_bar.get_children():
            if child is not self.menu_button:
                self.header_bar.remove(child)

        self.visible_child = name = stack.get_visible_child_name()
        if name:
            view = self.views[name]
            view.add_buttons(self.header_bar)
            view.update_actions()

    def disable_actions(self, view):
        try:
            actions = view.__class__.Actions
            for action in actions.__dict__.values():
                if isinstance(action, Gio.Action):
                    action.set_enabled(False)
        except AttributeError:
            pass
