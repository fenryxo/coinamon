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
        return path is not None and self[path][ContactsModel.GROUP_ID] != 0

    def is_address(self, path):
        return path is not None and self[path][ContactsModel.GROUP_ID] == 0

    def set_group_name(self, path, name):
        assert self.is_group(path)
        if name and self[path][self.KEY] != name:
            with self.db_session() as dbs:
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

    def on_row_activated(self, tree, path, column):
        model = self.get_model()
        if model.is_group(path):
            model[path][ContactsModel.KEY_EDITABLE] = True
            self.set_cursor(path, self.get_column(ContactsTree.KEY), True)
        elif model.is_address(path):
            model[path][ContactsModel.LABEL_EDITABLE] = True
            self.set_cursor(path, self.get_column(ContactsTree.LABEL), True)

    def on_key_edited(self, cell, path, text):
        model = self.get_model()
        model.set_group_name(path, text.strip())
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
        grid.show_all()
        self.selection = tree.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)
