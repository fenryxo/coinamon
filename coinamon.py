#!/usr/bin/python3
# coding: utf-8

from coinamon.db import bind_engine
from coinamon.gui import MainWindow, Gtk

win = MainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()

bind_engine('sqlite:///:memory:', echo=True)

Gtk.main()
