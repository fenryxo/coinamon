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
import struct
import unittest

from coinalib import bitcoin

BLOCK_HEADERS = [
    {
        'utxo_root': '16b333076eba85325e29cdf10ce59ae4d8eeaba181eb4b38cff7e73f4f695f60',
        'block_height': 356380, 'nonce': 2719374106, 'bits': 404165597,
        'merkle_root': '2e4ad3f750a78197c93dd5d8d8ffc3b1921e24720a0788689677d9a448592a83',
        'prev_block_hash': '000000000000000010386f315e907e42399c545cef76f4be008ee4af900d8bd2',
        'timestamp': 1431600866, 'version': 3
    },
    {
        'utxo_root': 'ddd82ddb3bceb53f2a07ad34514a6f91cf30b1ade5f5a00942585e7acebe9dd0',
        'block_height': 356381, 'nonce': 338974263, 'bits': 404165597,
        'merkle_root': '1e76ef4e18f7883720ef6e41783ace60701270764834726862dc981d23fa74b2',
        'prev_block_hash': '00000000000000000e2cd26b6438236a63fb001e3d0c8b2d2079122299f831a5',
        'timestamp': 1431601752, 'version': 2
    },
    {
        'utxo_root': '71bbe10d0c5f45d6bb00e29dc97f116f8b25f4a7edb8b27f47be50fac2282b64',
        'block_height': 356382, 'nonce': 3347960697, 'bits': 404165597,
        'merkle_root': '00c503a4017bac7945c1713e68cf15e526a9299c6c5b2914c9a5671dbe34614b',
        'prev_block_hash': '000000000000000015ff2cc2db0d8535bb13b7f43d794994012955b2e0693a18',
        'timestamp': 1431601497, 'version': 2
    },
    {
        'utxo_root': '263757ab25b69a7f6bfd9b45ad986393455354e4c959a36225f5ed72bc33d642',
        'block_height': 356383, 'nonce': 696476939, 'bits': 404165597,
        'merkle_root': '9de614c7d3edb2216e42765e935096692de42394fe70776c3ca4ecd4eb2513a7',
        'prev_block_hash': '00000000000000000399dd1524fbf0d7ed1defb89b4d400bb8ed980c40099da9',
        'timestamp': 1431601659, 'version': 3
    },
    {
        'utxo_root': '0b661b2683e27831a30ff3bfcc946942642bb5dbe603651f1f5dff1763147d9a',
        'block_height': 356384, 'nonce': 1293983283, 'bits': 404165597,
        'merkle_root': '2fd6a95ee0d49ca197848c5d473dd161e20d933718d415d41591d7a281d83167',
        'prev_block_hash': '000000000000000010e166aa5b12924853e1814b71e605512766d37b491eb676',
        'timestamp': 1431602755, 'version': 2
    },
    {
        'utxo_root': '9e6bc00e420a4faff37153377fce2bfe4e110906d2d88ce26a10951020d77c11',
        'block_height': 356385, 'nonce': 1109837152, 'bits': 404165597,
        'merkle_root': '03c68f540bd68e43a26711029d2f8a4953173494fed54f60b0f579cff54d00d6',
        'prev_block_hash': '00000000000000000354d68fafd8938957e14c0ea93b493b932b8fcf71a73f5c',
        'timestamp': 1431603446, 'version': 3
    },
    {
        'utxo_root': 'eba986b67b86ef7adc677580789161759eb91dba824437e742fc2763fab3c26d',
        'block_height': 356386, 'nonce': 3871460100, 'bits': 404165597,
        'merkle_root': '500b06d263e2cf21adc0258f8db57efdec9c26b1fcd7bf0fefb3dd10479d5174',
        'prev_block_hash': '00000000000000000fcfc02315c8e881cf880fa58e6d3e05cef9f37d593efb47',
        'timestamp': 1431603772, 'version': 2
    },
    {
        'utxo_root': '633d99ceaa7605411aebb8dbbfa65cd793f8c1c6d2a4c0a13e6e4e69124624cb',
        'block_height': 356387, 'nonce': 194149977, 'bits': 404165597,
        'merkle_root': '78bc21a562dd9f0635bc25908b282ef3b0bf985a094b470d30641d01e4c79d48',
        'prev_block_hash': '00000000000000000abc41009f33652162f3f1ad0aeda561149321ece341a815',
        'timestamp': 1431603840, 'version': 2
    },
    {
        'utxo_root': '42629e5c161146f24dfd412dc30767d0a33f705a41f53dbb3aa20eb44e97b59d',
        'block_height': 356388, 'nonce': 3826817334, 'bits': 404165597,
        'merkle_root': '9501ae4945b0f4de96d181c9757375b89437ab72eee5e3e3cf625451408a6069',
        'prev_block_hash': '0000000000000000121d66d0752955261ae209b0fa4a88f92ba1bda2e775f0a3',
        'timestamp': 1431605120, 'version': 2
    },
    {
        'utxo_root': 'd91a56cba7ecde85f975ab4242f344b62a4ba2de4213f7fec76a86c26adb469c',
        'block_height': 356389, 'nonce': 2492392301, 'bits': 404165597,
        'merkle_root': 'ecbf86ccfe16e5e3ef3218701d51817cccc141b1599a71cb5267db3dcfeae415',
        'prev_block_hash': '000000000000000004f33f2683111f47e0093f2eebd97c927ca70c6f5b75c005',
        'timestamp': 1431605858, 'version': 2
    },
    {
        'utxo_root': 'fbd8b177477a9ed32ca1c4b83eab88e80d2a06798455e155f198c761bb94529c',
        'block_height': 356390, 'nonce': 1424411088, 'bits': 404165597,
        'merkle_root': '13388ab59ed301edadd363c9a1137576539a6b3164aac7f274eed2f42a693c75',
        'prev_block_hash': '00000000000000000f8a5799d9a62d1673c08c91c85013948cb8ec1cff1e48e1',
        'timestamp': 1431606525, 'version': 2
    },
    {
        'utxo_root': '5ff775c16de1c2cfe26b1618e23bf92ed47199dd6a73f52d00a1c2d3173573e7',
        'block_height': 356391, 'nonce': 367796563, 'bits': 404165597,
        'merkle_root': '7fdf2883ddd857ad951cee68378280590b34b840f0588a0d7075fccd502d4c75',
        'prev_block_hash': '00000000000000000cf94cc03ee6b0f4b1dca4bec85337b86f38f0994a5ad1f1',
        'timestamp': 1431607136, 'version': 2
    },
    {
        'utxo_root': '1a6685e34376be0c053ff621515c22e983b0c8650d2506b654af35355404f53d',
        'block_height': 356392, 'nonce': 1973042377, 'bits': 404165597,
        'merkle_root': 'e0a3b508f3dcd1fae58e5c5812f8c04e5f7014237aa69cf62f63793d29bb3237',
        'prev_block_hash': '000000000000000010acd4b339c736eaf04b6a12a72100d149cfdd92fda35480',
        'timestamp': 1431607451, 'version': 3
    },
    {
        'utxo_root': '61134342253ed5f87a221c8f2b4f44574f86b16731a0a6bca29bc29f7d67dae6',
        'block_height': 356393, 'nonce': 380641592, 'bits': 404165597,
        'merkle_root': '56d972c143f2b1b463bd881c0504d9e963143b22da7638d38fb1cdef1621b7e3',
        'prev_block_hash': '0000000000000000144e917141da9a4e66cbb69145df3a539adcf39c56ca4894',
        'timestamp': 1431607687, 'version': 2
    }
]


def alternative_block_header_raw(block_header):
    buf = bytearray(80)
    offset = 0
    size = 4
    struct.pack_into("<I", buf, offset, block_header.version)
    offset += size
    size = 32
    buf[offset:offset + size] = \
        binascii.a2b_hex(block_header.prev_block_hash.encode("ascii"))[::-1]
    offset += size
    size = 32
    buf[offset:offset + size] = \
        binascii.a2b_hex(block_header.merkle_root.encode("ascii"))[::-1]
    offset += size
    size = 4
    struct.pack_into("<I", buf, offset, block_header.timestamp)
    offset += size
    size = 4
    struct.pack_into("<I", buf, offset, block_header.bits)
    offset += size
    size = 4
    struct.pack_into("<I", buf, offset, block_header.nonce)
    return buf


class BlockHeaderTest(unittest.TestCase):
    def test_raw_bin(self):
        for i, block_header in enumerate(BLOCK_HEADERS):
            with self.subTest(i=i):
                block_header = bitcoin.BlockHeader(**block_header)
                raw_bin = block_header.raw_bin
                alt_raw_bin = alternative_block_header_raw(block_header)
                self.assertEqual(alt_raw_bin, raw_bin)

    def test_hash_hex(self):
        for i in range(len(BLOCK_HEADERS) - 1):
            with self.subTest(i=i):
                block_header = bitcoin.BlockHeader(**BLOCK_HEADERS[i])
                expected_hash_hex = BLOCK_HEADERS[i + 1]["prev_block_hash"]
                hash_hex = block_header.hash_hex
                self.assertEqual(expected_hash_hex, hash_hex)
