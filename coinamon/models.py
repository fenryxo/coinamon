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


class Account(Model):
    TYPE_IMPORTED = "import"
    TYPE_RANDOM = "random"
    TYPES = frozenset((TYPE_IMPORTED, TYPE_RANDOM))
    name = Column(String(50), nullable=False, unique=True)
    type = Column(Enum(*TYPES), nullable=False)
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
        assert type in self.TYPES
        return type


class Tag(Model):
    name = Column(String(50), nullable=False, unique=True)

    @validates('name')
    def validate_name(self, key, name):
        assert name is not None and name.strip() != ""
        return name


class Group(Model):
    name = Column(String(50), nullable=False)
    parent_id = Column(Integer, ForeignKey('group.id'))
    parent = relationship("Group", remote_side="Group.id", backref="groups")
    n_tx = Column(Integer, nullable=False, default=0)
    balance = Column(BigInteger, nullable=False, default=0)

    def __repr__(self):
        return "<{} name='{}', parent='{}'>".format(
            self.__class__.__name__, self.name,
            self.parent.name if self.parent else self.parent_id)

    @validates('name')
    def validate_name(self, key, name):
        assert name is not None and name.strip() != ""
        return name

    @validates('n_tx')
    def validate_n_tx(self, key, n_tx):
        assert n_tx >= 0
        return n_tx

    @classmethod
    def walk_tree(cls, session, start_id=None, level=0, *, addresses=False):
        for group in session.query(cls).filter_by(parent_id=start_id).order_by(cls.name):
            if addresses:
                yield level, group, None
            else:
                yield level, group
            yield from cls.walk_tree(session, group.id, level + 1, addresses=addresses)
            if addresses:
                result = session.query(Address).filter_by(group_id=group.id) \
                    .order_by(Address.id, Address.label)
                for addr in result:
                    yield level + 1, None, addr


class Address(Model):
    TYPE_RECEIVE = "receive"
    TYPE_CHANGE = "change"
    TYPE_IMPORT = "import"
    TYPE_CONTACT = "contact"
    TYPES = frozenset((TYPE_RECEIVE, TYPE_CHANGE, TYPE_IMPORT, TYPE_CONTACT))
    id = Column(String(255), primary_key=True)
    account_id = Column(Integer, ForeignKey('account.id'))
    account = relationship("Account", backref="addresses")
    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship("Group", backref="addresses")
    label = Column(String(50))
    n_tx = Column(Integer, nullable=False, default=0)
    balance = Column(BigInteger, nullable=False, default=0)
    pinned = Column(Boolean, nullable=False, default=False)
    type = Column(Enum(*TYPES), nullable=False)
    tags = relationship('Tag', backref='addresses', secondary=Table(
        'address_tag_assoc',
        Model.metadata,
        Column('address_id', String(255), ForeignKey('address.id')),
        Column('tag_id', Integer, ForeignKey('tag.id'))))

    def __repr__(self):
        return "<{} id='{}', label='{}', type='{}', group='{}', account='{}'>".format(
            self.__class__.__name__,
            self.id,
            self.label,
            self.type,
            self.group.name if self.group else self.group_id,
            self.account.name if self.account else self.account_id)

    @validates('n_tx')
    def validate_n_tx(self, key, n_tx):
        assert n_tx >= 0
        return n_tx

    @validates('type')
    def validate_type(self, key, type):
        assert type in self.TYPES
        return type
