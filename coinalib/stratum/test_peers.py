# coding: utf-8

# Copyright 2015 Jiří Janoušek <janousek.jiri@gmail.com>
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

from coinalib import stratum
from coinalib.stratum.peers import Peer, PeerList, DEFAULT_PEERS  # noqa


class PeerTest(unittest.TestCase):
    def test_str(self):
        peer = Peer("myhost", 1234, "v01", 1024, "x")
        self.assertEqual("myhost:1234 (x) v01 p1024 (enabled)", str(peer))

    def test_disable_and_enable(self):
        peer = Peer("myhost", 1234, "v01", 1024, "x")
        self.assertTrue(peer.enabled)
        peer.disable()
        self.assertFalse(peer.enabled)
        peer.enable()
        self.assertTrue(peer.enabled)


class PeerListTest(unittest.TestCase):
    PEERS = [
        ['123.123.123.123', 'myelectrum.example.info', [
            'v0.9', 'p10000', 't', 'h', 's', 'g']],
        ['123.123.123.123', 'myelectrum.example.org', [
            'v0.99', 'p1000', 's789', 'g333', 't123', 'h456']],
        ['123.123.123.123', 'myelectrum2.example.org', [
            'v0.99', 's1000', 'x789', 'g333']],
    ]

    def test_parse(self):

        expected = (
            "myelectrum.example.info:0 (t) v0.9 p10000 (enabled)",
            "myelectrum.example.info:0 (h) v0.9 p10000 (enabled)",
            "myelectrum.example.info:0 (s) v0.9 p10000 (enabled)",
            "myelectrum.example.info:0 (g) v0.9 p10000 (enabled)",
            "myelectrum.example.org:789 (s) v0.99 p1000 (enabled)",
            "myelectrum.example.org:333 (g) v0.99 p1000 (enabled)",
            "myelectrum.example.org:123 (t) v0.99 p1000 (enabled)",
            "myelectrum.example.org:456 (h) v0.99 p1000 (enabled)",
        )
        errors = []
        peers = tuple(str(p) for p in PeerList.parse(self.PEERS, errors))
        self.assertEqual(len(errors), 1)
        self.assertEqual(expected, peers)

    def test_parse_default_peers(self):
        errors = []
        peers = tuple(PeerList.parse(DEFAULT_PEERS, errors))
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(peers), 6 * 4 + 1 * 3 + 20 * 2 + 0 * 1)

    def test_peers_empty(self):
        peers = PeerList()
        for protocol in stratum.Protocol:
            with self.subTest(protocol=protocol):
                msg = "No peers for protocol '{}'".format(protocol)
                with self.assertRaisesRegex(ValueError, msg):
                    peers.get_peer(protocol)

        protocol = None
        with self.subTest(protocol=protocol):
            with self.assertRaisesRegex(ValueError, "No peers for any protocol"):
                peers.get_peer(protocol)

    def test_get_peer(self):
        peers = PeerList(PeerList.parse(self.PEERS))
        for protocol in stratum.Protocol:
            with self.subTest(protocol=protocol):
                peer = peers.get_peer(protocol)
                self.assertEqual(
                    "myelectrum.example.info:0 ({}) v0.9 p10000 (enabled)".format(protocol),
                    str(peer))
        protocol = None
        with self.subTest(protocol=protocol):
            peer = peers.get_peer(protocol)
            expected = "myelectrum.example.info:0 ({}) v0.9 p10000 (enabled)".format(
                stratum.Protocol.ssl)
            self.assertEqual(expected, str(peer))

    def test_update(self):
        peers = PeerList()
        peers.update(PeerList.parse(self.PEERS))
        for protocol in stratum.Protocol:
            with self.subTest(protocol=protocol):
                peer = peers.get_peer(protocol)
                self.assertEqual(
                    "myelectrum.example.info:0 ({}) v0.9 p10000 (enabled)".format(protocol),
                    str(peer))

    def test_peer_disabled(self):
        peers = PeerList(PeerList.parse(self.PEERS))

        for protocol in stratum.Protocol:
            with self.subTest(protocol=protocol):
                peers.get_peer(protocol)

        protocol = None
        with self.subTest(protocol=protocol):
            peers.get_peer(protocol)

        all_peers = tuple(peers.list_peers())
        for peer in all_peers:
            peer.disable()

        for protocol in stratum.Protocol:
            with self.subTest(protocol=protocol):
                msg = "No enabled peers for protocol '{}'".format(protocol)
                with self.assertRaisesRegex(ValueError, msg):
                    peers.get_peer(protocol)

        protocol = None
        with self.subTest(protocol=protocol):
            with self.assertRaisesRegex(ValueError, "No enabled peers for any protocol"):
                peers.get_peer(protocol)
