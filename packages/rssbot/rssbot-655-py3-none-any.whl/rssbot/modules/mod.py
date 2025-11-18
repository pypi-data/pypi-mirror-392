# This file is placed in the Public Domain.


from rssbot.package import modules


def mod(event):
    event.reply(",".join(modules()))
