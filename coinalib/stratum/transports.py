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
import threading
import time
import traceback

import requests

import coinalib
from coinalib import stratum
from coinalib.stratum import exceptions


Response = collections.namedtuple("Response", "id response")


def create_transport(peer):
    protocol = peer.protocol
    if protocol in (stratum.Protocol.http, stratum.Protocol.https):
        return HttpTransportThread(peer, protocol == stratum.Protocol.https)

    raise ValueError("Unsupported protocol '{}'.".format(protocol))


class TransportPool:
    def __init__(self, peer_list):
        self.peer_list = peer_list

    def get_transport(self, protocol=None):
        if protocol is None:
            for protocol in stratum.Protocol.by_priority():
                try:
                    return self.get_transport(protocol)
                except ValueError:
                    pass
            raise ValueError("No transport is available.")

        return create_transport(self.peer_list.get_peer(protocol))


class TransportThread(threading.Thread):
    def __init__(self, peer, use_ssl):
        super().__init__(name=self.__class__.__name__)
        self.session = None
        self.peer = peer
        self.use_ssl = use_ssl
        self.running = False

    def start(self, session):
        self.session = session
        super().start()

    def run(self):
        raise NotImplementedError

    def stop(self):
        if not self.running:
            raise RuntimeError("Transport is not runnning.")
        self.running = False


POLL_MSG_ID = 0


class HttpTransportThread(TransportThread):
    USER_AGENT = '{}/{} Stratum/HttpTransport'.format("Coinalib", coinalib.VERSION)

    def __init__(self, peer, use_ssl):
        super().__init__(peer, use_ssl)
        self.port = peer.port or (8082 if use_ssl else 8081)
        self.address = "{}://{}:{}/".format("https" if use_ssl else "http", peer.host, self.port)
        self.timeout = 5
        self.http = http = requests.Session()
        http.headers.update({
            'User-Agent': self.__class__.USER_AGENT,
            'Content-Type': 'application/stratum',
        })

    def run(self):
        if self.running:
            raise RuntimeError("Transport is already runnning.")

        self.running = True
        try:
            while self.running:
                try:
                    while self.running:
                        request = self.session.pop_request()
                        result = self._send_request(request.data, 5)
                        self._process_responses(result.content)
                except queue.Empty:
                    result = self._poll_for_responses()
                    self._process_responses(result.content)
                    time.sleep(0.1)
        except (exceptions.ConnectionTimeout, exceptions.ConnectionError) as e:
            self.session.transport_aborted(self, e)
        except Exception as e:
            traceback.print_exc()  # Unexpected exception - print traceback
            self.session.transport_aborted(self, e)
        self.running = False

    def _poll_for_responses(self):
        return self._send_request(json.dumps({
            "jsonrpc": "2.0",
            "id": POLL_MSG_ID,
            "method": "server.version",
            "params": ["1.9.5" "0.9"]
        }).encode("ascii"), 5)

    def _send_request(self, data, retry=0):
        while retry >= 0:
            try:
                return self.http.post(self.address, data=data, timeout=self.timeout, verify=False)
            except requests.Timeout as e:
                if retry > 0:
                    retry -= 1
                else:
                    raise exceptions.ConnectionTimeout(self.peer) from e
            except requests.ConnectionError as e:
                raise exceptions.ConnectionError(str(e), peer=self.peer) from e

    def _process_responses(self, data):
        if data:
            try:
                entries = json.loads(data.decode("ascii"))
            except Exception:
                raise exceptions.ValueError("Invalid response", data)

            if not isinstance(entries, list):
                entries = [entries]
            for entry in entries:
                message_id = entry.get("id", None)
                if message_id == POLL_MSG_ID:
                    continue  # poll request

                exception = None
                request = None
                if message_id is not None:
                    try:
                        request = self.session.get_request(message_id)
                    except KeyError:
                        traceback.print_exc()
                        continue

                error = entry.get("error")
                if error:
                    if isinstance(error, str):
                        exception = exceptions.MessageError(0, error)
                    else:
                        exception = exceptions.MessageError(
                            error[0],
                            error[1],
                            error[2] if len(error) > 2 else None)

                response = Response(message_id, entry.get("result"))
                self.session.deliver_response(request, response, exception)
