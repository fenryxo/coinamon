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

from sqlalchemy import sql

from coinamon.models import Address
from coinamon.models import Group


class Importer:
    IMPORTS_CONTACTS = "contacts"

    name = None
    label = None
    capabilities = None

    def __init__(self, db_session):
        self.db_session = db_session

    def import_contacts(self, data):
        raise NotImplementedError(
            "{}.import_contacts not implemented.".format(self.__class__.__name__))

    def analyse_contacts(self, contacts):
        unique = []
        duplicate = []

        with self.db_session() as dbs:
            for item in contacts:
                addr = item["addr"]
                label = item["label"]
                item = label, addr
                if dbs.query(sql.exists().where(Address.id == addr)).scalar():
                    duplicate.append(item)
                else:
                    unique.append(item)

        return unique, duplicate

    def save_contacts(self, group, contacts):
        with self.db_session() as dbs:
            if isinstance(group, str):
                group = Group(name=group)
                dbs.add(group)
                dbs.flush()
                group_id = group.id
            elif isinstance(group, Group):
                group_id = group.id
            else:
                raise TypeError("Argument group must be a Group or a str, but got {}.".format(
                    type(group)))

            for label, address_id in contacts:
                dbs.add(Address(
                    id=address_id, label=label, group_id=group_id, type=Address.TYPE_CONTACT))


class BadDataError(ValueError):
    pass
