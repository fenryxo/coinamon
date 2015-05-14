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


NotificationCallback = collections.namedtuple("NotificationCallback", "callback args kwargs")


class AsyncRequestCallback:
    def __init__(self, callback, *args, **kwargs):
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
        if session is None:
            session = m_session.Session()

        self.tranport_pool = transport_pool
        self.loop = loop
        self.session = session
        self._event_loop_listener = m_session.EventLoopListener(loop, self)
        self.session.add_listener(self._event_loop_listener)
        self._transport = None
        self.notification_callbacks = []

    def subscribe(self, callback, *args, **kwargs):
        cb = NotificationCallback(callback, args, kwargs)
        self.notification_callbacks.append(cb)
        return cb

    def unsubscribe(self, cb):
        self.notification_callbacks.remove(cb)

    def start(self):
        self._transport = self.tranport_pool.get_transport()
        self._transport.start(self.session)

    def stop(self):
        if self._transport:
            self._transport.stop()
            self._transport.join()

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

    def on_transport_aborted(self, session, transport, exception):
        transport.peer.disable()
        session.restart_unprocessed()
        self._transport = self.tranport_pool.get_transport()
        self._transport.start(session)

    def on_notification_received(self, session, notification):
        for cb in self.notification_callbacks:
            try:
                cb.callback(notification, *cb.args, **cb.kwargs)
            except Exception:
                traceback.print_exc()

    def on_respose_received(self, session, request, response, error):
        try:
            request.callback(response, error)
        except Exception:
            traceback.print_exc()


if __name__ == "__main__":
    from coinalib.stratum import peers
    from coinalib.stratum import utils

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
