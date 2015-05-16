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


import binascii
import datetime
import hashlib
import struct


def double_sha256(data):
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


class BlockHeader(dict):
    def __init__(self, **params):
        super().__init__(**params)
        self._hash_hex = None

    @property
    def utxo_root(self):
        return self["utxo_root"]

    @property
    def block_height(self):
        return self["block_height"]

    @property
    def nonce(self):
        return self["nonce"]

    @property
    def bits(self):
        return self["bits"]

    @property
    def merkle_root(self):
        return self["merkle_root"]

    @property
    def prev_block_hash(self):
        return self["prev_block_hash"]

    @property
    def timestamp(self):
        return self["timestamp"]

    @property
    def datetime(self):
        return datetime.datetime.utcfromtimestamp(self.timestamp)

    @property
    def version(self):
        return self["version"]

    @property
    def raw_bin(self):
        # The hashes are in internal byte order; the other values are all in little-endian order.
        # https://bitcoin.org/en/developer-reference#block-headers
        return struct.pack(
            "<I32s32s3I",
            self.version,
            binascii.a2b_hex(self.prev_block_hash.encode("ascii"))[::-1],
            binascii.a2b_hex(self.merkle_root.encode("ascii"))[::-1],
            self.timestamp,
            self.bits,
            self.nonce)

    @property
    def raw_hex(self):
        return binascii.b2a_hex(self.raw_bin).decode("ascii")

    @property
    def hash_hex(self):
        if not self._hash_hex:
            self._hash_hex = binascii.b2a_hex(double_sha256(self.raw_bin)[::-1]).decode("ascii")
        return self._hash_hex

    @property
    def hash_bin(self):
        return binascii.a2b_hex(self.hash_hex.encode("ascii"))[::-1]
