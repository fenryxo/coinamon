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


class ContactsView(View):
    def __init__(self, db_session):
        widget = Gtk.ScrolledWindow()
        super().__init__("contacts", "Contacts", widget)
        self.db_session = db_session
        self.model = model = Gtk.TreeStore(int, str, str, str, int)
        with db_session() as dbs:
            def add(parent_id=None, parent_iter=None):
                for group in dbs.query(Group).filter_by(parent_id=parent_id).order_by(Group.name):
                    print(group)
                    row_iter = model.append(parent_iter, row=(
                        group.id, group.name, None, str(group.balance), group.n_tx))
                    if group.parent_id is not None:
                        add(self, group.parent_id, row_iter)

                    addresses = dbs.query(Address).filter_by(group_id=group.id) \
                        .order_by(Address.id, Address.label)
                    for addr in addresses:
                        print(addr)
                        model.append(row_iter, row=(
                            0, addr.id, addr.label, str(addr.balance), addr.n_tx))

            add()

        self.tree = tree = Gtk.TreeView(model)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Group/Address", renderer, text=1)
        tree.append_column(column)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Label", renderer, text=2)
        tree.append_column(column)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Balance", renderer, text=3)
        tree.append_column(column)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Tx", renderer, text=4)
        tree.append_column(column)

        self.widget.add(tree)
        self.tree.show()
