# coding: utf-8

import unittest
from sqlalchemy.exc import IntegrityError
from ..db import bind_engine, db_session
from .. import models as m


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        bind_engine('sqlite:///:memory:', echo=False)

    def create(self, **kwd):
        obj = self.get_valid()
        for key, val in kwd.items():
            setattr(obj, key, val)
        return obj


class AccountModelTest(DatabaseTestCase):
    def get_valid(self):
        return m.Account(name="name", type=m.ACCOUNT_TYPE_RANDOM)

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


class CategoryModelTest(DatabaseTestCase):
    def get_valid(self):
        return m.Category(name="name")

    def test_valid_ok(self):
        with db_session() as db:
            db.add(self.create())

    def test_blank_fails(self):
        with self.assertRaises(IntegrityError), db_session() as db:
            db.add(m.Category())

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
            self.category = m.Category(name="category")
            self.account = m.Account(name="Account")
            db.commit()
            self.category_id = self.category.id
            self.account_id = self.account.id

    def get_valid(self):
        return m.Address(id="addrid", type=m.ADDRESS_TYPE_CONTACT, category_id=self.category_id)

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
