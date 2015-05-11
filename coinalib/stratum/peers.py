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

import random

from coinalib import stratum


DEFAULT_PEERS = [
    ['192.198.93.86', 'EAST.electrum.jdubya.info', ['v0.9', 'p1000', 't', 'h', 's', 'g']],
    ['91.121.108.61', 'electrum.xiro.co', ['v0.9', 'p10000', 't', 's']],
    ['70.38.9.66', 'electrum.drollette.com', ['v0.9', 'p10000', 't', 's']],
    ['96.32.46.235', 'electrum0.electricnewyear.net', ['v0.9', 'p10000', 't', 's']],
    ['162.220.47.184', 'bitcoin.epicinet.net', ['v0.9', 'p10000', 't', 'h', 's', 'g']],
    ['98.206.63.41', 'jwu42.hopto.org', ['v0.9', 'p1000', 't', 's']],
    ['208.66.30.27', 'electrum.rajohns.com', ['v0.9', 'p10000', 't', 's']],
    ['93.211.67.167', 'electrum3.hachre.de', ['v0.9', 'p10000', 't', 'h', 's', 'g']],
    ['85.178.11.235', 'eco-electrum.ddns.net', ['v0.9', 'p100', 't', 's']],
    ['52.11.253.111', 'bitcoin-p2pool.com', ['v0.9', 'p10000', 't', 's']],
    ['192.99.46.170', 'electrum.dragonzone.net', ['v0.9', 'p10000', 't', 's']],
    ['83.162.196.192', 'electrum0.snel.it', ['v0.9', 'p10000', 't', 's']],
    ['144.76.99.209', 'ecdsa.net', ['v0.9', 'p100', 't', 's110']],
    ['107.150.28.160', 'electrum.fsck.space', ['v0.9', 'p10000', 't', 's']],
    ['50.67.156.43', 'electrum.mindspot.org', ['v0.9', 'p10000', 't', 'h', 's', 'g']],
    ['188.40.33.189', 'kirsche.emzy.de', ['v0.9', 'p10000', 't', 'h', 's', 'g']],
    ['149.210.187.10', 'electrum.bitfuzz.nl', ['v0.9', 'p10000', 't', 's']],
    ['88.198.241.196', 'electrum.be', ['v0.9', 'p10000', 't', 's']],
    ['76.174.26.91', 'electrum.hsmiths.com', ['v0.9', 'p10000', 't', 's']],
    ['167.160.169.212', 'bitcoin.trouth.net', ['v0.9', 'p10000', 't', 's']],
    ['130.211.184.129', 'bitcoin.krellis.org', ['v0.9', 'p1000', 't', 's']],
    ['191.233.88.232', 'green-gold.cloudapp.net', ['v0.9', 'p10000', 't', 's']],
    ['84.250.46.245', 'erbium1.sytes.net', ['v0.9', 'p10000', 't', 's']],
    ['151.80.190.130', 'electrum.sky-ip.org', ['v0.9', 'p10000', 't', 's']],
    ['94.102.50.70', 'electrum.badass.sx', ['v0.9', 'p10000', 't', 's']],
    ['162.210.198.184', 'us.electrum.be', ['v0.9', 'p10000', 't', 'h', 's', 'g']],
    ['78.55.125.38', 'electrum.no-ip.org', ['v0.9', 'p10000', 't', 's', 'g443']]
]


class Peer:
    def __init__(self, host, port, version, prunning, protocol, enabled=True):
        self.host = host
        self.port = port
        self.version = version
        self.prunning = prunning
        self.protocol = protocol
        self.enabled = enabled

    def disable(self):
        # Might emit signal in the future
        self.enabled = False

    def enable(self):
        # Might emit signal in the future
        self.enabled = True

    def __str__(self):
        return "{}:{} ({}) {} p{} ({})".format(
            self.host, self.port, self.protocol, self.version, self.prunning,
            "enabled" if self.enabled else "disabled")

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.__str__())


class PeerList:
    @staticmethod
    def parse(peers, errors=None):
        for peer in peers:
            try:
                addr, host, meta = peer
                version = meta[0]
                if meta[1][0] != "p":
                    raise ValueError("Unexpected prunning description '{}'".format(meta[1]))

                prunning = int(meta[1][1:])
                for protocol in meta[2:]:
                    try:
                        if len(protocol) > 1:
                            port = int(protocol[1:])
                            protocol = protocol[0:1]
                        else:
                            port = 0  # use default

                        protocol = stratum.Protocol(protocol)  # raises ValueError
                        yield Peer(host, port, version, prunning, protocol)
                    except ValueError as e:
                        if errors is not None:
                            errors.append((peer, e))
            except (ValueError, IndexError) as e:
                if errors is not None:
                    errors.append((peer, e))

    def __init__(self, peers=None):
        self.update(peers or tuple())

    def update(self, peers):
        self.peers = {p: [] for p in stratum.Protocol}
        for peer in peers:
            self.peers[peer.protocol].append(peer)

        key_func = lambda peer: peer.prunning
        for protocol in stratum.Protocol:
            self.peers[protocol].sort(key=key_func, reverse=True)

    def get_peer(self, protocol=None):
        if protocol is None:
            for protocol in stratum.Protocol.by_priority():
                try:
                    return self.get_peer(protocol)
                except ValueError:
                    pass

            for peers in self.peers.values():
                if peers:
                    raise ValueError("No enabled peers for any protocol.")
            raise ValueError("No peers for any protocol.")

        peers = self.peers[protocol]
        if not peers:
            raise ValueError("No peers for protocol '{}'.".format(protocol))

        prunning = 0
        choices = []
        for peer in peers:
            if prunning == 0:
                prunning = peer.prunning

            if peer.prunning != prunning:
                prunning = peer.prunning
                if choices:
                    break

            if peer.enabled:
                choices.append(peer)

        if not choices:
            raise ValueError("No enabled peers for protocol '{}'.".format(protocol))

        return random.choice(choices)

    # TODO medium: unittest
    def list_peers(self, protocol=None):
        if protocol is None:
            for peers in self.peers.values():
                for peer in peers:
                    yield peer
        else:
            for peer in self.peers[protocol]:
                yield peer
