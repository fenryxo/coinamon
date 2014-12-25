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
from . import DatabaseMixin
from .. import importer


class ContactsImporterTest(DatabaseMixin, unittest.TestCase):
    def test_import_contacts(self):
        with self.assertRaises(NotImplementedError):
            importer.ContactsImporter().import_contacts(None)

    def test_save_contacts(self):
        contacts = [
            ('Pikachu', '1AhB4xTDhFt2hdDeUajP7gnt7soFwYiVL9'),
            ('Charmander', '15ADxNhKLSKMpzSoAKmVjXBKF62ErwynKU'),
            ('Charmeleon', '1Hugs3Zo3b1vZ36FCVRbwW5QfYTChwF9cZ'),
            ('Yes - No', '1MYR9ovdGPz88KwSM55Z2rnRStprh2moGk'),
            (None, '18Wwrz1p4cW9UnxoGDNUegY7doSnfC4ZhZ'),
            ]

        unique, duplicate = importer.ContactsImporter().save_contacts(contacts)
        self.assertEqual(unique, contacts)
        self.assertFalse(duplicate)

        unique, duplicate = importer.ContactsImporter().save_contacts(contacts)
        self.assertEqual(duplicate, contacts)
        self.assertFalse(unique)

        new_contacts = [
            ('Pikachu 2', '2AhB4xTDhFt2hdDeUajP7gnt7soFwYiVL9'),
            ('Charmander 2', '25ADxNhKLSKMpzSoAKmVjXBKF62ErwynKU')]

        unique, duplicate = importer.ContactsImporter().save_contacts(contacts + new_contacts)
        self.assertEqual(duplicate, contacts)
        self.assertEqual(unique, new_contacts)

    def test_check_result(self):
        self.assertEqual(
            importer.ContactsImporter().check_result(unique=0, duplicate=0, errors=0), 0)
        self.assertEqual(
            importer.ContactsImporter().check_result(unique=5, duplicate=0, errors=0), 5)

        with self.assertRaises(importer.CompleteImportError) as cm:
            importer.ContactsImporter().check_result(unique=0, duplicate=0, errors=3)
        self.assertEqual(cm.exception.unique, 0)
        self.assertEqual(cm.exception.duplicate, 0)
        self.assertEqual(cm.exception.errors, 3)

        with self.assertRaises(importer.PartialImportError) as cm:
            importer.ContactsImporter().check_result(unique=2, duplicate=0, errors=3)
        self.assertEqual(cm.exception.unique, 2)
        self.assertEqual(cm.exception.duplicate, 0)
        self.assertEqual(cm.exception.errors, 3)

        with self.assertRaises(importer.PartialImportError) as cm:
            importer.ContactsImporter().check_result(unique=2, duplicate=5, errors=3)
        self.assertEqual(cm.exception.unique, 2)
        self.assertEqual(cm.exception.duplicate, 5)
        self.assertEqual(cm.exception.errors, 3)

        with self.assertRaises(importer.PartialImportError) as cm:
            importer.ContactsImporter().check_result(unique=2, duplicate=5, errors=0)
        self.assertEqual(cm.exception.unique, 2)
        self.assertEqual(cm.exception.duplicate, 5)
        self.assertEqual(cm.exception.errors, 0)

        with self.assertRaises(importer.CompleteImportError) as cm:
            importer.ContactsImporter().check_result(unique=0, duplicate=5, errors=0)
        self.assertEqual(cm.exception.unique, 0)
        self.assertEqual(cm.exception.duplicate, 5)
        self.assertEqual(cm.exception.errors, 0)


class BlockchainWalletImporterTest(DatabaseMixin, unittest.TestCase):
    def test_import_contacts(self):
        ADDRESSES = """\
            Pikachu - 1AhB4xTDhFt2hdDeUajP7gnt7soFwYiVL9
            0.00 BTC
            Actions
            Charmander - 15ADxNhKLSKMpzSoAKmVjXBKF62ErwynKU
            0.00 BTC
            Actions
            Charmeleon - 1Hugs3Zo3b1vZ36FCVRbwW5QfYTChwF9cZ
            0.00 BTC
            Actions
            Yes - No - 1MYR9ovdGPz88KwSM55Z2rnRStprh2moGk
            0.00 BTC
            Actions
            18Wwrz1p4cW9UnxoGDNUegY7doSnfC4ZhZ"""
        contacts = [
            ('Pikachu', '1AhB4xTDhFt2hdDeUajP7gnt7soFwYiVL9'),
            ('Charmander', '15ADxNhKLSKMpzSoAKmVjXBKF62ErwynKU'),
            ('Charmeleon', '1Hugs3Zo3b1vZ36FCVRbwW5QfYTChwF9cZ'),
            ('Yes - No', '1MYR9ovdGPz88KwSM55Z2rnRStprh2moGk'),
            (None, '18Wwrz1p4cW9UnxoGDNUegY7doSnfC4ZhZ'),
            ]
        self.assertEqual(
            importer.BlockchainWalletImporter().import_contacts(ADDRESSES), contacts)

        with self.assertRaises(importer.CompleteImportError) as cm:
            importer.BlockchainWalletImporter().import_contacts(ADDRESSES)
        self.assertEqual(cm.exception.unique, [])
        self.assertEqual(cm.exception.duplicate, contacts)
        self.assertEqual(cm.exception.errors, [])
