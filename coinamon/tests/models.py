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

import unittest
from sqlalchemy.exc import IntegrityError
from ..db import db_session
from .. import models as m
from . import DatabaseMixin


class DatabaseTestCase(DatabaseMixin, unittest.TestCase):
    def create(self, **kwd):
        obj = self.get_valid()
        for key, val in kwd.items():
            setattr(obj, key, val)
        return obj


class AccountModelTest(DatabaseTestCase):
    def get_valid(self):
        return m.Account(name="name", type=m.Account.TYPE_RANDOM)

    def test_valid_ok(self):
        with db_session() as db:
            db.add(self.create())

    def test_blank_fails(self):
        with self.assertRaises(IntegrityError), db_session() as db:
            db.add(m.Account())

    def test_validate_name(self):
        with self.assertRaises(AssertionError), db_session() as db:
            db.add(self.create(name=" "))

        with self.assertRaises(AssertionError), db_session() as db:
            db.add(self.create(name=""))

        with self.assertRaises(AssertionError), db_session() as db:
            db.add(self.create(name=None))

    def test_validate_n_tx(self):
        with self.assertRaises(AssertionError), db_session() as db:
            db.add(self.create(n_tx=-1))

        with self.assertRaises(TypeError), db_session() as db:
            db.add(self.create(n_tx="foo"))

    def test_validate_type(self):
        with self.assertRaises(AssertionError), db_session() as db:
            db.add(self.create(type="foo"))

        with self.assertRaises(AssertionError), db_session() as db:
            db.add(self.create(type=""))

        with self.assertRaises(AssertionError), db_session() as db:
            db.add(self.create(type=None))


class TagModelTest(DatabaseTestCase):
    def get_valid(self):
        return m.Tag(name="name")

    def test_valid_ok(self):
        with db_session() as db:
            db.add(self.create())

    def test_blank_fails(self):
        with self.assertRaises(IntegrityError), db_session() as db:
            db.add(m.Tag())

    def test_validate_name(self):
        with self.assertRaises(AssertionError), db_session() as db:
            db.add(self.create(name=" "))

        with self.assertRaises(AssertionError), db_session() as db:
            db.add(self.create(name=""))

        with self.assertRaises(AssertionError), db_session() as db:
            db.add(self.create(name=None))


class GroupModelTest(DatabaseTestCase):
    def get_valid(self):
        return m.Group(name="name")

    def test_valid_ok(self):
        with db_session() as db:
            db.add(self.create())

    def test_blank_fails(self):
        with self.assertRaises(IntegrityError), db_session() as db:
            db.add(m.Group())

    def test_validate_name(self):
        with self.assertRaises(AssertionError), db_session() as db:
            db.add(self.create(name=" "))

        with self.assertRaises(AssertionError), db_session() as db:
            db.add(self.create(name=""))

        with self.assertRaises(AssertionError), db_session() as db:
            db.add(self.create(name=None))

    def test_validate_n_tx(self):
        with self.assertRaises(AssertionError), db_session() as db:
            db.add(self.create(n_tx=-1))

        with self.assertRaises(TypeError), db_session() as db:
            db.add(self.create(n_tx="foo"))


class AddressModelTest(DatabaseTestCase):
    def setUp(self):
        super().setUp()
        with db_session() as db:
            self.group = m.Group(name="group")
            self.account = m.Account(name="Account")
            db.commit()
            self.group_id = self.group.id
            self.account_id = self.account.id

    def get_valid(self):
        return m.Address(id="addrid", type=m.Address.TYPE_CONTACT, group_id=self.group_id)

    def test_valid_ok(self):
        with db_session() as db:
            db.add(self.create())

    def test_blank_fails(self):
        with self.assertRaises(IntegrityError), db_session() as db:
            db.add(m.Address())

    def test_validate_type(self):
        with self.assertRaises(AssertionError), db_session() as db:
            db.add(self.create(type="foo"))

        with self.assertRaises(AssertionError), db_session() as db:
            db.add(self.create(type=""))

        with self.assertRaises(AssertionError), db_session() as db:
            db.add(self.create(type=None))

    def test_validate_n_tx(self):
        with self.assertRaises(AssertionError), db_session() as db:
            db.add(self.create(n_tx=-1))

        with self.assertRaises(TypeError), db_session() as db:
            db.add(self.create(n_tx="foo"))
