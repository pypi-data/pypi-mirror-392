# This file is placed in the Public Domain.


from tob.command import Fleet


def sil(event):
    bot = Fleet.get(event.orig)
    bot.silent = True
    event.reply("ok")


def lou(event):
    bot = Fleet.get(event.orig)
    bot.silent = False
    event.reply("ok")
