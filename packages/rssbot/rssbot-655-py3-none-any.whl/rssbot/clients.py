# This file is placed in the Public Domain.


import queue
import threading


from .handler import Handler
from .threads import launch


class Config:

    name = "tob"
    opts = ""
    sets: dict[str,str] = {}
    version = 141


class Client(Handler):

    def __init__(self):
        Handler.__init__(self)
        self.olock = threading.RLock()
        self.oqueue = queue.Queue()
        self.silent = True
        Fleet.add(self)

    def announce(self, text):
        if not self.silent:
            self.raw(text)

    def display(self, event):
        with self.olock:
            for tme in sorted(event.result):
                self.dosay(
                           event.channel,
                           event.result[tme]
                          )

    def dosay(self, channel, text):
        self.say(channel, text)

    def raw(self, text):
        raise NotImplementedError("raw")

    def say(self, channel, text):
        self.raw(text)

    def wait(self):
        self.oqueue.join()    


class Output(Client):

    def output(self):
        while True:
            event = self.oqueue.get()
            if event is None:
                self.oqueue.task_done()
                break
            self.display(event)
            self.oqueue.task_done()

    def start(self):
        launch(self.output)
        super().start()

    def stop(self):
        self.oqueue.put(None)
        super().stop()


class Fleet:

    clients: dict[str, Client] = {}

    @staticmethod
    def add(client):
        Fleet.clients[repr(client)] = client

    @staticmethod
    def all():
        return Fleet.clients.values()

    @staticmethod
    def announce(text):
        for client in Fleet.all():
            client.announce(text)

    @staticmethod
    def display(event):
        client = Fleet.get(event.orig)
        if client:
            client.display(event)

    @staticmethod
    def get(origin):
        return Fleet.clients.get(origin, None)

    @staticmethod
    def like(origin):
        for orig in Fleet.clients:
            if origin.split()[0] in orig.split()[0]:
                yield orig

    @staticmethod
    def say(orig, channel, txt):
        client = Fleet.get(orig)
        if client:
            client.say(channel, txt)

    @staticmethod
    def shutdown():
        for client in Fleet.all():
            client.wait()
            client.stop()


def __dir__():
    return (
        'Client',
        'Config',
        'Fleet',
        'Output'
   )
