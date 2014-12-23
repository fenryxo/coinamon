#!/usr/bin/python3
# coding: utf-8

from coinamon.gui import MainWindow, Gtk

win = MainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()

Gtk.main()
