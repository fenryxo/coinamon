# coding: utf-8

import signal
from gi.repository import Gtk  # noqa
from .mainwindow import MainWindow  # noqa

signal.signal(signal.SIGINT, signal.SIG_DFL)
