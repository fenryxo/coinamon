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

from coinamon.contacts.gui import ContactsModel   # noqa


class BaseContactsTree(Gtk.TreeView):
    def __init__(self, model):
        super().__init__(model=model)
        self.define_columns()
        self.set_enable_tree_lines(True)
        self.set_grid_lines(Gtk.TreeViewGridLines.HORIZONTAL)

    def define_columns(self):
        raise NotImplementedError(
            "{}.define_columns not implemented".format(self.__class__.__name__))


class ContactsTree(BaseContactsTree):
    KEY, LABEL, BALANCE, N_TX = range(4)

    def define_columns(self):
        # Icon and group name/address id columns
        column = Gtk.TreeViewColumn("Group/Address")
        column.set_spacing(5)
        renderer = Gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, "icon-name", ContactsModel.ICON)
        renderer = Gtk.CellRendererText()
        renderer.connect("edited", self.on_key_edited)
        column.pack_start(renderer, True)
        column.add_attribute(renderer, "text", ContactsModel.KEY)
        column.add_attribute(renderer, "editable", ContactsModel.KEY_EDITABLE)
        column.set_sort_column_id(ContactsModel.KEY_SORT)
        self.append_column(column)

        # Label column
        renderer = Gtk.CellRendererText()
        renderer.connect("edited", self.on_label_edited)
        column = Gtk.TreeViewColumn("Label", renderer, text=ContactsModel.LABEL)
        column.add_attribute(renderer, "editable", ContactsModel.LABEL_EDITABLE)
        column.set_sort_column_id(ContactsModel.LABEL)
        self.append_column(column)

        # Balance column
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Balance", renderer, text=ContactsModel.BALANCE)
        column.set_sort_column_id(ContactsModel.BALANCE)
        self.append_column(column)

        # N tx column
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Tx", renderer, text=ContactsModel.N_TX)
        column.set_sort_column_id(ContactsModel.N_TX)
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
