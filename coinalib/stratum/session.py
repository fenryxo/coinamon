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
import json
import queue


Request = collections.namedtuple("Request", "id data callback")


class Session:
    def __init__(self):
        self.listeners = []
        self.requests = queue.Queue()
        self.in_progress = {}
        self.message_id = 0

    def add_listener(self, listener):
        self.listeners.append(listener)

    def enqueue_request(self, method, params, callback):
        self.message_id += 1
        data = json.dumps({
            "id": self.message_id,
            "method": method, "params": params or [],
            "jsonrpc": "2.0"
        })
        data = data.encode("ascii") + b"\n"
        self.requests.put(Request(self.message_id, data, callback))
        return self.message_id

    def get_request(self, request_id):
        return self.in_progress[request_id]

    def pop_request(self):
        request = self.requests.get_nowait()
        self.in_progress[request.id] = request
        self.requests.task_done()
        return request

    def deliver_response(self, request, response, error):
        del self.in_progress[request.id]
        for listener in self.listeners:
            listener.on_respose_received(self, request, response, error)

    def deliver_notification(self, notification):
        for listener in self.listeners:
            listener.on_notification_received(self, notification)

    def transport_aborted(self, transport, exception):
        for listener in self.listeners:
            listener.on_transport_aborted(self, transport, exception)

    def restart_unprocessed(self):
        unprocessed = self.in_progress
        self.in_progress = {}
        for request in unprocessed.values():
            self.requests.put(request)


class SessionListener:
    def on_notification_received(self, session, notification):
        raise NotImplementedError

    def on_transport_aborted(self, session, transport, exception):
        raise NotImplementedError

    def on_respose_received(self, transport, request, response):
        raise NotImplementedError


class EventLoopListener(SessionListener):
    def __init__(self, loop, listener):
        super().__init__()
        self.loop = loop
        self.listener = listener

    def on_notification_received(self, session, notification):
        self.loop.call_soon_threadsafe(
            self.listener.on_notification_received, session, notification)

    def on_respose_received(self, session, request, response, error):
        self.loop.call_soon_threadsafe(
            self.listener.on_respose_received, session, request, response, error)

    def on_transport_aborted(self, session, transport, exception):
        self.loop.call_soon_threadsafe(
            self.listener.on_transport_aborted, session, transport, exception)
