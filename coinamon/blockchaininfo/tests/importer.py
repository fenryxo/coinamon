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

from coinamon.blockchaininfo.importer import BlockchaininfoImporter
from coinamon.blockchaininfo.tests import data
from coinamon.core.importer import BadDataError
from coinamon.core.tests import DatabaseMixin


class BlockchaininfoImporterTest(DatabaseMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.importer = BlockchaininfoImporter(self.db_session)

    def test_import_contacts(self):
        errors = []
        with self.assertRaises(BadDataError):
            list(self.importer.import_contacts(None, errors))

        with self.assertRaises(BadDataError):
            list(self.importer.import_contacts("", errors))

        with self.assertRaises(BadDataError):
            list(self.importer.import_contacts("    ", errors))

        with self.assertRaises(BadDataError):
            list(self.importer.import_contacts("  fsdf fdsgdatr fsdgdsg  ", errors))

        with self.assertRaises(BadDataError):
            list(self.importer.import_contacts('{"foo": "foo"}', errors))

        with self.assertRaises(BadDataError):
            list(self.importer.import_contacts('{"address_book": 1}', errors))

        result = list(self.importer.import_contacts(data.WALLET_JSON, errors))
        self.assertEqual(result, data.CONTACTS)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], BadDataError)
