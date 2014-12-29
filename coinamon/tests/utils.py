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

from coinamon import utils


class FnctionsTestCase(unittest.TestCase):
    def test_parse_blockchain_contacts_list(self):
        CONTACTS = """\
        Dash - Test
        1FudEVgHetFdDeWtS6uq7k2cjiEUNw129N

        Happy Daisy
        1Pvt1GNb92W35gXshzwUCG5kpPsBg4ACtA

        Bill Gates
        19hz4WsAEKdP1fcumazpyBYrt8RMNNJium

        Bitcoin Master
        1KopQ3e9pFKEwTmriSvia1TyJc1VJ5KXLF

        Master Yoda
        1ABnFxaVGQ1ccefekKTXUVPNBiTLy9ytD6

        Coinbase Test
        13kqo1oaQskAHBb6krsczYBTtkeMpEEVsK

        Prince of Persia
        1G25qfo8aH1SHRfy5VuVYitH9vevyfvse7
        """

        EXPECTED = \
            [
                ('Dash - Test', '1FudEVgHetFdDeWtS6uq7k2cjiEUNw129N'),
                ('Happy Daisy', '1Pvt1GNb92W35gXshzwUCG5kpPsBg4ACtA'),
                ('Bill Gates', '19hz4WsAEKdP1fcumazpyBYrt8RMNNJium'),
                ('Bitcoin Master', '1KopQ3e9pFKEwTmriSvia1TyJc1VJ5KXLF'),
                ('Master Yoda', '1ABnFxaVGQ1ccefekKTXUVPNBiTLy9ytD6'),
                ('Coinbase Test', '13kqo1oaQskAHBb6krsczYBTtkeMpEEVsK'),
                ('Prince of Persia', '1G25qfo8aH1SHRfy5VuVYitH9vevyfvse7'),
            ]

        errors = []
        self.assertEqual(
            EXPECTED,
            list(utils.parse_blockchain_contacts_list(CONTACTS, errors=errors)))
        self.assertFalse(errors)

        self.assertEqual(
            EXPECTED,
            list(utils.parse_blockchain_contacts_list("  \n  \n" + CONTACTS + "  \n  \n")))

    def test_parse_blockchain_address_list(self):
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

        EXPECTED = \
            [
                ('Pikachu', '1AhB4xTDhFt2hdDeUajP7gnt7soFwYiVL9'),
                ('Charmander', '15ADxNhKLSKMpzSoAKmVjXBKF62ErwynKU'),
                ('Charmeleon', '1Hugs3Zo3b1vZ36FCVRbwW5QfYTChwF9cZ'),
                ('Yes - No', '1MYR9ovdGPz88KwSM55Z2rnRStprh2moGk'),
                (None, '18Wwrz1p4cW9UnxoGDNUegY7doSnfC4ZhZ'),
            ]

        errors = []
        self.assertEqual(
            EXPECTED,
            list(utils.parse_blockchain_address_list(ADDRESSES, errors=errors)))
        self.assertFalse(errors)

        self.assertEqual(
            EXPECTED,
            list(utils.parse_blockchain_address_list("  \n  \n" + ADDRESSES + "  \n  \n")))

        self.assertEqual(
            EXPECTED,
            list(utils.parse_blockchain_address_list(ADDRESSES, step=2, errors=errors)))
        self.assertFalse(errors)

        errors = []
        self.assertNotEqual(
            EXPECTED,
            list(utils.parse_blockchain_address_list(ADDRESSES, step=3, errors=errors)))
        self.assertTrue(errors)

        errors = []
        self.assertNotEqual(
            EXPECTED,
            list(utils.parse_blockchain_address_list(ADDRESSES, skip_lines=3, errors=errors)))
        self.assertFalse(errors)
