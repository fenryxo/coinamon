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

from datetime import datetime
from sqlalchemy import sql
from .db import db_session
from .models import Group, Address


class ImportFailedError(Exception):
    def __init__(self, errors, unique=None, duplicate=None, *args, **kwargs):
        super().__init__("Import failed.", *args, **kwargs)
        self.errors = errors
        self.unique = unique
        self.duplicate = duplicate


class PartialImportError(ImportFailedError):
    pass


class CompleteImportError(ImportFailedError):
    pass


class ContactsImporter:
    name = None
    label = None

    def import_contacts(self, data):
        raise NotImplementedError(
            "{}.import_contacts not implemented.".format(self.__class__.__name__))

    def save_contacts(self, contacts):
        duplicate = []
        unique = []
        with db_session() as dbs:

            for item in contacts:
                if dbs.query(sql.exists().where(Address.id == item[1])).scalar():
                    duplicate.append(item)
                else:
                    unique.append(item)

            if unique:
                group = Group(name="Imported contacts ({0:%c})".format(datetime.today()))
                for label, address_id in unique:
                    dbs.add(Address(
                        id=address_id, label=label, group=group, type=Address.TYPE_CONTACT))
        return unique, duplicate

    def check_result(self, unique, duplicate, errors):
        if errors or duplicate:
            if unique:
                raise PartialImportError(errors, unique, duplicate)
            else:
                raise CompleteImportError(errors, unique, duplicate)
        return unique
