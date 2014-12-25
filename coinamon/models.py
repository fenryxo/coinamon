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

from sqlalchemy import Table, Column, String, Integer, BigInteger, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship, validates
from .db import Model


ACCOUNT_TYPE_IMPORTED = "import"
ACCOUNT_TYPE_RANDOM = "random"
ACCOUNT_TYPES = frozenset((ACCOUNT_TYPE_IMPORTED, ACCOUNT_TYPE_RANDOM))


class Account(Model):
    name = Column(String(50), nullable=False, unique=True)
    type = Column(Enum(*ACCOUNT_TYPES), nullable=False)
    n_tx = Column(Integer, nullable=False, default=0)
    balance = Column(BigInteger, nullable=False, default=0)

    @validates('name')
    def validate_name(self, key, name):
        assert name is not None and name.strip() != ""
        return name

    @validates('n_tx')
    def validate_n_tx(self, key, n_tx):
        assert n_tx >= 0
        return n_tx

    @validates('type')
    def validate_type(self, key, type):
        assert type in ACCOUNT_TYPES
        return type


class Tag(Model):
    name = Column(String(50), nullable=False, unique=True)

    @validates('name')
    def validate_name(self, key, name):
        assert name is not None and name.strip() != ""
        return name


class Category(Model):
    name = Column(String(50), nullable=False)
    parent_id = Column(Integer, ForeignKey('category.id'))
    parent = relationship("Category", remote_side="Category.id", backref="categories")
    n_tx = Column(Integer, nullable=False, default=0)
    balance = Column(BigInteger, nullable=False, default=0)

    @validates('name')
    def validate_name(self, key, name):
        assert name is not None and name.strip() != ""
        return name

    @validates('n_tx')
    def validate_n_tx(self, key, n_tx):
        assert n_tx >= 0
        return n_tx

ADDRESS_TYPE_RECEIVE = "receive"
ADDRESS_TYPE_CHANGE = "change"
ADDRESS_TYPE_IMPORT = "import"
ADDRESS_TYPE_CONTACT = "contact"
ADDRESS_TYPES = frozenset((
    ADDRESS_TYPE_RECEIVE,
    ADDRESS_TYPE_CHANGE,
    ADDRESS_TYPE_IMPORT,
    ADDRESS_TYPE_CONTACT,
    ))


class Address(Model):
    id = Column(String(255), primary_key=True)
    account_id = Column(Integer, ForeignKey('account.id'))
    account = relationship("Account", backref="addresses")
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category", backref="addresses")
    label = Column(String(50))
    n_tx = Column(Integer, nullable=False, default=0)
    balance = Column(BigInteger, nullable=False, default=0)
    pinned = Column(Boolean, nullable=False, default=False)
    type = Column(Enum(*ADDRESS_TYPES), nullable=False)
    tags = relationship('Tag', backref='addresses', secondary=Table(
        'address_tag_assoc',
        Model.metadata,
        Column('address_id', String(255), ForeignKey('address.id')),
        Column('tag_id', Integer, ForeignKey('tag.id'))))

    @validates('n_tx')
    def validate_n_tx(self, key, n_tx):
        assert n_tx >= 0
        return n_tx

    @validates('type')
    def validate_type(self, key, type):
        assert type in ADDRESS_TYPES
        return type
