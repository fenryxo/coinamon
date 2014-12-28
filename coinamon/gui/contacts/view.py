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

from gi.repository import Gio, Gtk
from ..view import View
from . import ContactsModel, DuplicateAddressError, ContactsTree, AddContactDialog


class ContactsView(View):
    class Actions:
        ADD_CONTACT = Gio.SimpleAction.new("add_contact", None)
        ADD_GROUP = Gio.SimpleAction.new("add_group", None)
        ADD_SUBGROUP = Gio.SimpleAction.new("add_subgroup", None)
        REMOVE_GROUP = Gio.SimpleAction.new("remove_group", None)

    def __init__(self, db_session):
        widget = grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL, row_spacing=10, margin=10)
        super().__init__("contacts", "Contacts", widget)
        self.model = model = ContactsModel(db_session)
        model.load_data()
        self.tree = tree = ContactsTree(model)
        scroll = Gtk.ScrolledWindow(vexpand=True, hexpand=True)
        scroll.add(tree)
        grid.add(scroll)

        self.selection = tree.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)

        self.Actions.ADD_CONTACT.connect("activate", self.on_add_contact)
        self.Actions.ADD_GROUP.connect("activate", self.on_add_group)
        self.Actions.ADD_SUBGROUP.connect("activate", self.on_add_subgroup)
        self.Actions.REMOVE_GROUP.connect("activate", self.on_remove_group)
        self.buttons = []

        # Add actions
        button = Gtk.MenuButton()
        button.set_image(Gtk.Image.new_from_icon_name(
            "list-add-symbolic", Gtk.IconSize.SMALL_TOOLBAR))
        menu = Gio.Menu()
        menu.append("Add contact", "win." + self.Actions.ADD_CONTACT.get_name())
        menu.append("Add group", "win." + self.Actions.ADD_GROUP.get_name())
        menu.append("Add subgroup", "win." + self.Actions.ADD_SUBGROUP.get_name())
        button.set_menu_model(menu)
        button.show_all()
        self.buttons.append(button)

        # Remove actions
        button = Gtk.MenuButton()
        button.set_image(Gtk.Image.new_from_icon_name(
            "list-remove-symbolic", Gtk.IconSize.SMALL_TOOLBAR))
        menu = Gio.Menu()
        menu.append("Remove group", "win." + self.Actions.REMOVE_GROUP.get_name())
        button.set_menu_model(menu)
        button.show_all()
        self.buttons.append(button)

        grid.show_all()
        self.selection.connect("changed", self.on_selection_changed)
        self.update_actions()
        tree.set_reorderable(True)

    def add_buttons(self, header_bar):
        super().add_buttons(header_bar)
        for button in self.buttons:
            header_bar.pack_start(button)

    def update_actions(self):
        self.on_selection_changed(self.selection)

    def on_selection_changed(self, selection):
        model, tree_iter = selection.get_selected()
        self.Actions.ADD_CONTACT.set_enabled(model.can_add_contact(tree_iter))
        self.Actions.ADD_GROUP.set_enabled(model.can_add_group(tree_iter))
        self.Actions.ADD_SUBGROUP.set_enabled(model.can_add_subgroup(tree_iter))
        self.Actions.REMOVE_GROUP.set_enabled(model.can_remove_group(tree_iter))

    def on_add_contact(self, *args):
        model, tree_iter = self.selection.get_selected()
        dialog = AddContactDialog(self.widget.get_toplevel())
        try:
            while True:
                result = dialog.run()
                if result == Gtk.ResponseType.OK:
                    address = dialog.address_entry.get_text().strip()
                    label = dialog.label_entry.get_text().strip()
                    if not address:
                        dialog.show_error("Address must not be empty.")
                    else:
                        try:
                            addr_iter = self.model.add_contact(tree_iter, address, label)
                            addr_path = self.model.get_path(addr_iter)
                            self.tree.expand_to_path(addr_path)
                            self.tree.set_cursor(addr_path, None, False)
                            break
                        except DuplicateAddressError as e:
                            t = "The address '{}' is already in the database with a label '{}'." \
                                if e.old_label else "The address '{}' is already in the database."
                            dialog.show_error(t.format(e.address, e.old_label))
                else:
                    break
        finally:
            dialog.destroy()

    def on_add_group(self, *args):
        model, tree_iter = self.selection.get_selected()
        new_iter = self.model.add_group(tree_iter)
        self.tree.edit_row(model.get_path(new_iter))

    def on_add_subgroup(self, *args):
        model, tree_iter = self.selection.get_selected()
        new_iter = self.model.add_subgroup(tree_iter)
        self.tree.edit_row(model.get_path(new_iter))

    def on_remove_group(self, *args):
        model, tree_iter = self.selection.get_selected()
        model.remove_group(tree_iter)
