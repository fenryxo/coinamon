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

from sqlalchemy.exc import IntegrityError
from gi.repository import Gtk
from ...models import Group, Address


class DuplicateAddressError(ValueError):
    def __init__(self, address, old_label, new_label):
        super().__init__(address, old_label, new_label)
        self.address = address
        self.old_label = old_label
        self.new_label = new_label


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

    def can_add_contact(self, tree_iter):
        return tree_iter is not None

    def can_add_group(self, tree_iter):
        return True

    def can_add_subgroup(self, tree_iter):
        return self.is_group(tree_iter)

    def can_remove_group(self, tree_iter):
        # TODO: recursive remove for self.iter_depth(tree_iter) > 0
        return self.is_group(tree_iter) and self.iter_n_children(tree_iter) == 0

    def add_contact(self, tree_iter, address, label):
        assert self.can_add_group(tree_iter)
        if not self.is_group(tree_iter):
            path = self.get_path(tree_iter)
            path.up()
            tree_iter = self.get_iter(path)
        assert self.is_group(tree_iter)

        try:
            with self.db_session() as dbs:
                group_id = self[tree_iter][self.GROUP_ID]
                dbs.add(Address(
                    id=address, label=label, group_id=group_id, type=Address.TYPE_CONTACT))
        except IntegrityError:
            with self.db_session() as dbs:
                addr = dbs.query(Address).filter_by(id=address).one()
                raise DuplicateAddressError(address, addr.label, label)

        return self.insert_before(tree_iter, None, (
            0, address, False, label, False, "", 0))

    def add_group(self, tree_iter, name="New group"):
        assert self.can_add_group(tree_iter)
        return self.insert_after(None, tree_iter, (
            self.NEW_GROUP_ID, name, True, None, False, "", 0))

    def add_subgroup(self, tree_iter, name="New group"):
        assert self.can_add_subgroup(tree_iter)
        return self.insert_after(tree_iter, None, (
            self.NEW_GROUP_ID, name, True, None, False, "", 0))

    def remove_group(self, tree_iter):
        assert self.can_remove_group(tree_iter)
        assert self.iter_n_children(tree_iter) == 0  # TODO: recursive delete
        group_id = self[tree_iter][self.GROUP_ID]
        with self.db_session() as dbs:
            dbs.query(Group).filter_by(id=group_id).delete()
        del self[tree_iter]

    def set_group_name(self, path, name):
        assert self.is_group(path)
        if not name:
            raise ValueError("Empty group name not permitted")

        is_new = self.is_new_group(path)
        if is_new or self[path][self.KEY] != name:
            with self.db_session() as dbs:
                if is_new:
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

    def can_move(self, source_path, dest_path):
        try:
            self.get_iter(source_path)  # validate path
        except ValueError as e:
            print(type(e), e)
            return False

        if source_path.is_ancestor(dest_path):
            return False

        try:
            self.get_iter(dest_path)  # validate path
            return dest_path.get_depth() > 1 or self[source_path][self.GROUP_ID] > 0
        except ValueError:
            path = dest_path.copy()
            path.up()
            return self[path][self.GROUP_ID] != 0

    def copy_children(self, source_iter, dest_iter):
        child_iter = self.iter_children(source_iter)
        while child_iter is not None:
            child_dest_iter = self.append(dest_iter, self[child_iter][:])
            self.copy_children(child_iter, child_dest_iter)
            child_iter = self.iter_next(child_iter)

    def update_parent(self, tree_iter):
        parent = self.get_path(tree_iter)
        if not parent.up():
            raise ValueError(parent)
        if parent is None:
            assert self.is_group(tree_iter)
            parent_id = None
        else:
            assert self.is_group(parent)
            parent_id = self[parent][self.GROUP_ID]

        with self.db_session() as dbs:
            if self.is_group(tree_iter):
                dbs.query(Group).filter_by(id=self[tree_iter][self.GROUP_ID]).update({
                    Group.parent_id: parent_id
                    })
            elif self.is_address(tree_iter):
                dbs.query(Address).filter_by(id=self[tree_iter][self.KEY]).update({
                    Address.group_id: parent_id
                    })
            else:
                raise NotImplementedError

    def _get_path_from_selection_data(self, selection_data):
        #  this crashes: result, model, path = Gtk.tree_get_row_drag_data(selection_data)
        data = selection_data.get_data()
        try:
            return Gtk.TreePath.new_from_string(data.rsplit(b"\x00", 2)[-2].decode("ascii"))
        except Exception as e:
            raise ValueError("Error for data '{}': {}".format(data, e))

    def do_row_drop_possible(self, dest_path, selection_data):
        try:
            source_path = self._get_path_from_selection_data(selection_data)
        except ValueError as e:
            print(e)
            return False

        return self.can_move(source_path, dest_path)

    def do_drag_data_received(self, dest_path, selection_data):
        try:
            source_path = self._get_path_from_selection_data(selection_data)
        except ValueError as e:
            print(e)
            return False

        if not self.can_move(source_path, dest_path):
            return False

        source_iter = self.get_iter(source_path)
        try:
            dest_iter = self.get_iter(dest_path)  # validate path
            insert_as_child = False
        except ValueError:
            dest_path.up()
            try:
                dest_iter = self.get_iter(dest_path)
            except ValueError as e:
                print(e)
                return False
            insert_as_child = True

        row_data = self[source_path][:]
        if insert_as_child:
            tree_iter = self.insert_before(dest_iter, None, row_data)
        else:
            tree_iter = self.insert_before(None, dest_iter, row_data)

        self.update_parent(tree_iter)
        self.copy_children(source_iter, tree_iter)
        return True
