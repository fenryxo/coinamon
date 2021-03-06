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

import collections
import traceback

from coinalib.stratum import session as m_session
from coinalib.stratum import transports
from coinalib.stratum import utils


class AsyncRequestCallback:
    def __init__(self, callback, args, kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def __call__(self, response, error):
        return self.callback(response, error, *self.args, **self.kwargs)


class SyncRequestCallback:
    def __init__(self, loop):
        self.loop = loop
        self.response = None
        self.error = None

    def __call__(self, response, error):
        self.response = response
        self.error = error
        self.loop.stop()


class StratumClient:
    def __init__(self, transport_pool, loop, session=None):
        self.init_transport = utils.Event()
        self.connection_established = utils.Event()
        self.connection_lost = utils.Event()
        self.connection_reconnect = utils.Event()

        if session is None:
            session = m_session.Session()

        self.tranport_pool = transport_pool
        self.loop = loop
        self.session = session
        self._event_loop_listener = m_session.EventLoopListener(loop, self)
        self.session.add_listener(self._event_loop_listener)
        self.transport = None
        self.notifications = collections.defaultdict(utils.Event)
        self.reconnect_attempts = 0

    @property
    def is_connection_established(self):
        return self.transport and self.transport.is_functional

    def start(self):
        self.start_new_transport()

    def stop(self):
        if self.transport:
            self.transport.stop()
            self.transport.join()

    def send_request_async(self, method, params, callback, *args, **kwargs):
        callback = AsyncRequestCallback(callback, args, kwargs)
        return self.session.enqueue_request(method, params, callback)

    def send_request_sync(self, method, params):
        child_loop = self.loop.create_child()
        callback = SyncRequestCallback(child_loop)
        self.session.enqueue_request(method, params, callback)
        child_loop.run()
        if callback.error:
            raise callback.error
        return callback.response

    def start_new_transport(self):
        if self.transport and self.transport.running:
            self.transport.stop()
        self.session.restart_unprocessed()
        try:
            self.transport = self.tranport_pool.get_transport()

        except ValueError:
            self.transport = None
            self.reconnect()
        else:
            self.transport.start(self.session)
            self.init_transport.emit(self, self.transport)

    def reconnect(self):
        self.reconnect_attempts += 1
        delay = min(5 * self.reconnect_attempts, 5 * 60)
        self.connection_reconnect.emit(self, self.reconnect_attempts, delay)
        self.tranport_pool.enable_all()
        self.loop.call_later(delay, self.start_new_transport)

    def on_transport_aborted(self, session, transport, exception):
        transport.peer.disable()
        if transport.is_functional:
            self.connection_lost.emit(self, transport)
        self.start_new_transport()

    def on_transport_functional(self, session, transport):
        self.reconnect_attempts = 0
        self.connection_established.emit(self, transport)

    def on_notification_received(self, session, notification):
        self.notifications[notification.method].emit(notification)

    def on_respose_received(self, session, request, response, error):
        try:
            request.callback(response, error)
        except Exception:
            traceback.print_exc()


if __name__ == "__main__":
    from coinalib.stratum import peers

    loop = utils.SimpleLoop()
    peer_list = peers.PeerList(peers.PeerList.parse(peers.DEFAULT_PEERS))
    transport_pool = transports.TransportPool(peer_list)
    client = StratumClient(transport_pool, loop)
    client.start()

    method = "server.version"
    params = ["1.9.5", "0.9"]

    def done(response, error, *args, **kwargs):
        print(response, error, args, kwargs)
        print(client.send_request_sync(method, params))
        print(client.send_request_sync(method, params))
        loop.stop()
        print(client.send_request_sync(method, params))
        print(client.send_request_sync(method, params))

    client.send_request_async(method, params, done, "hey", name="hou")

    loop.run()

    method = "blockchain.headers.subscribe"
    params = []
    print(client.send_request_sync(method, params))
    loop.run()
    client.quit()
