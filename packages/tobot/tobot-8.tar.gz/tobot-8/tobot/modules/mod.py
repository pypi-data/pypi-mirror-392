# This file is placed in the Public Domain.


from tob.package import modules


def mod(event):
    event.reply(",".join(modules()))
