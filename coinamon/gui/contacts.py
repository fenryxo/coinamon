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
from .view import View
from ..models import Group, Address


class ContactsModel(Gtk.TreeStore):
    GROUP_ID, KEY, KEY_EDITABLE, LABEL, LABEL_EDITABLE, BALANCE, N_TX = range(7)
    NEW_GROUP_ID = -1

    def __init__(self, db_session):
        Gtk.TreeStore.__init__(self, int, str, bool, str, bool, str, int)
        self.db_session = db_session

    def load_data(self):
        self.clear()
        with self.db_session() as dbs:
            def add(parent_id=None, parent_iter=None):
                for group in dbs.query(Group).filter_by(parent_id=parent_id).order_by(Group.name):
                    row_iter = self.append(parent_iter, row=(
                        group.id, group.name, False, None, False, str(group.balance), group.n_tx))
                    add(group.id, row_iter)
                    addresses = dbs.query(Address).filter_by(group_id=group.id) \
                        .order_by(Address.id, Address.label)
                    for addr in addresses:
                        self.append(row_iter, row=(
                            0, addr.id, False, addr.label, False, str(addr.balance), addr.n_tx))

            add()

    def is_group(self, path):
        return path is not None and self[path][self.GROUP_ID] != 0

    def is_new_group(self, path):
        return path is not None and self[path][self.GROUP_ID] == self.NEW_GROUP_ID

    def is_address(self, path):
        return path is not None and self[path][self.GROUP_ID] == 0

    def can_add_group(self, path):
        return True

    def can_add_subgroup(self, path):
        return self.is_group(path)

    def add_group(self, tree_iter, name="New group"):
        assert self.can_add_group(tree_iter)
        return self.insert_after(None, tree_iter, (
            self.NEW_GROUP_ID, name, True, None, False, "", 0))

    def add_subgroup(self, tree_iter, name="New group"):
        assert self.can_add_subgroup(tree_iter)
        return self.insert_after(tree_iter, None, (
            self.NEW_GROUP_ID, name, True, None, False, "", 0))

    def set_group_name(self, path, name):
        assert self.is_group(path)
        if not name:
            raise ValueError("Empty group name not permitted")

        if self[path][self.KEY] != name:
            with self.db_session() as dbs:
                if self.is_new_group(path):
                    cursor = path.split(":")
                    cursor.pop()
                    if cursor:
                        parent_id = self[":".join(cursor)][self.GROUP_ID]
                    else:
                        parent_id = None

                    group = Group(name=name, parent_id=parent_id)
                    dbs.add(group)
                    dbs.commit()
                    self[path][self.GROUP_ID] = group.id
                else:
                    dbs.query(Group).filter_by(id=self[path][self.GROUP_ID]).update({
                        Group.name: name
                        })
            self[path][self.KEY] = name

    def set_addr_label(self, path, label):
        assert self.is_address(path)
        if self[path][self.LABEL] != label:
            with self.db_session() as dbs:
                dbs.query(Address).filter_by(id=self[path][self.KEY]).update({
                    Address.label: label
                    })
            self[path][self.LABEL] = label


class BaseContactsTree(Gtk.TreeView):
    def __init__(self, model):
        super().__init__(model=model)
        self.define_columns()

    def define_columns(self):
        raise NotImplementedError(
            "{}.define_columns not implemented".format(self.__class__.__name__))


class ContactsTree(BaseContactsTree):
    KEY, LABEL, BALANCE, N_TX = range(4)

    def define_columns(self):
        # Group name/address id column
        renderer = Gtk.CellRendererText()
        renderer.connect("edited", self.on_key_edited)
        column = Gtk.TreeViewColumn("Group/Address", renderer, text=ContactsModel.KEY)
        column.add_attribute(renderer, "editable", ContactsModel.KEY_EDITABLE)
        self.append_column(column)

        # Label column
        renderer = Gtk.CellRendererText()
        renderer.connect("edited", self.on_label_edited)
        column = Gtk.TreeViewColumn("Label", renderer, text=ContactsModel.LABEL)
        column.add_attribute(renderer, "editable", ContactsModel.LABEL_EDITABLE)
        self.append_column(column)

        # Balance column
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Balance", renderer, text=ContactsModel.BALANCE)
        self.append_column(column)

        # N tx column
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Tx", renderer, text=ContactsModel.N_TX)
        self.append_column(column)

        self.connect("row-activated", self.on_row_activated)

    def edit_row(self, path):
        model = self.get_model()
        if model.is_group(path):
            self.expand_to_path(path)
            model[path][model.KEY_EDITABLE] = True
            self.set_cursor(path, self.get_column(self.KEY), True)
        elif model.is_address(path):
            self.expand_to_path(path)
            model[path][model.LABEL_EDITABLE] = True
            self.set_cursor(path, self.get_column(self.LABEL), True)

    def on_row_activated(self, tree, path, column):
        self.edit_row(path)

    def on_key_edited(self, cell, path, text):
        model = self.get_model()
        try:
            model.set_group_name(path, text.strip())
        except ValueError:
            if model.is_new_group(path):
                del model[path]
                return

        model[path][model.KEY_EDITABLE] = False

    def on_label_edited(self, cell, path, text):
        model = self.get_model()
        model.set_addr_label(path, text.strip())
        model[path][model.LABEL_EDITABLE] = False


class ContactsView(View):
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

        buttons = Gtk.ButtonBox(
            homogeneous=True, layout_style=Gtk.ButtonBoxStyle.CENTER, vexpand=False, hexpand=True)
        grid.add(buttons)
        self.add_group_button = button = Gtk.Button(label="Add group")
        self.add_group_button.connect("clicked", self.on_add_group)
        buttons.pack_start(button, True, False, 0)
        self.add_subgroup_button = button = Gtk.Button(label="Add subgroup")
        self.add_subgroup_button.connect("clicked", self.on_add_subgroup)
        buttons.pack_start(button, True, False, 0)

        grid.show_all()
        self.selection.connect("changed", self.on_selection_changed)
        self.on_selection_changed(self.selection)

    def on_selection_changed(self, selection):
        model, tree_iter = selection.get_selected()
        self.add_group_button.set_sensitive(model.can_add_group(tree_iter))
        self.add_subgroup_button.set_sensitive(model.can_add_subgroup(tree_iter))

    def on_add_group(self, button):
        model, tree_iter = self.selection.get_selected()
        new_iter = self.model.add_group(tree_iter)
        self.tree.edit_row(model.get_path(new_iter))

    def on_add_subgroup(self, button):
        model, tree_iter = self.selection.get_selected()
        new_iter = self.model.add_subgroup(tree_iter)
        self.tree.edit_row(model.get_path(new_iter))
