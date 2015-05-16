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

# flake8: noqa


def add_views(app, window):
    #~ window.add_view(ContactsView(app.db_session), True)
    from coinalib import bitcoin
    #~ from coinalib import blockexplorers
    #~ from coinalib.stratum import client
    #~ from coinalib.stratum import glibutils
    #~ from coinalib.stratum import peers
    #~ from coinalib.stratum import transports

    block_explorer = app.block_explorer

    client = app.electrum

    def done(response, error, *args, **kwargs):
        print(response, error, args, kwargs)
        block_header = bitcoin.BlockHeader(**response.response)
        block_explorer.block_info(block_header.hash_hex).open()

    def on_notification(notification, *args, **kwargs):
        print(notification, args, kwargs)
        block_header = bitcoin.BlockHeader(**notification.params[0])
        block_explorer.block_info(block_header.hash_hex).open()

    method = "blockchain.headers.subscribe"
    params = []
    print(client.subscribe(method, on_notification))
    print(client.send_request_async(method, params, done, "foo", bar="baz"))


def add_actions(app, window):
    pass
