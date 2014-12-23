#!/usr/bin/python3
# coding: utf-8

from coinamon.db import bind_engine, db_session
from coinamon.models import User
from coinamon.gui import MainWindow, Gtk

win = MainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()

bind_engine('sqlite:///:memory:', echo=True)
with db_session() as db:
    user = User(name='ed', fullname='Ed Jones', password='edspassword')
    db.add(user)

Gtk.main()
