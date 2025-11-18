# This file is placed in the Public Domain.


import datetime
import json
import os
import pathlib
import threading
import time


from .marshal import dump, load
from .objects import Object, items, update


lock = threading.RLock()


class Cache:

    objs = Object()

    @staticmethod
    def add(path, obj):
        setattr(Cache.objs, path, obj)

    @staticmethod
    def get(path):
        return getattr(Cache.objs, path, None)

    @staticmethod
    def update(path, obj):
        setattr(Cache.objs, path, obj)


def deleted(obj):
    return "__deleted__" in dir(obj) and obj.__deleted__


def find(type=None, selector=None, removed=False, matching=False):
    if selector is None:
        selector = {}
    for pth in fns(type):
        obj = Cache.get(pth)
        if not obj:
            obj = Object()
            read(obj, pth)
            Cache.add(pth, obj)
        if not removed and deleted(obj):
            continue
        if selector and not search(obj, selector, matching):
            continue
        yield pth, obj


def fns(type=None):
    if type is not None:
        type = type.lower()
    path = store()
    for rootdir, dirs, _files in os.walk(path, topdown=True):
        for dname in dirs:
            if dname.count("-") != 2:
                continue
            ddd = os.path.join(rootdir, dname)
            if type and type not in ddd.lower():
                continue
            for fll in os.listdir(ddd):
                yield os.path.join(ddd, fll)


def fntime(daystr):
    datestr = " ".join(daystr.split(os.sep)[-2:])
    datestr = datestr.replace("_", " ")
    if "." in datestr:
        datestr, rest = datestr.rsplit(".", 1)
    else:
        rest = ""
    timed = time.mktime(time.strptime(datestr, "%Y-%m-%d %H:%M:%S"))
    if rest:
        timed += float("." + rest)
    return float(timed)


def last(obj, selector=None):
    if selector is None:
        selector = {}
    result = sorted(
                    find(fqn(obj), selector),
                    key=lambda x: fntime(x[0])
                   )
    res = ""
    if result:
        inp = result[-1]
        update(obj, inp[-1])
        res = inp[0]
    return res


def read(obj, path):
    with lock:
        with open(path, "r", encoding="utf-8") as fpt:
            try:
                update(obj, load(fpt))
            except json.decoder.JSONDecodeError as ex:
                ex.add_note(path)
                raise ex


def search(obj, selector, matching=False):
    res = False
    for key, value in items(selector):
        val = getattr(obj, key, None)
        if not val:
            continue
        if matching and value == val:
            res = True
        elif str(value).lower() in str(val).lower():
            res = True
        else:
            res = False
            break
    return res


def write(obj, path=None):
    with lock:
        if path is None:
            path = getpath(obj)
        cdir(path)
        with open(path, "w", encoding="utf-8") as fpt:
            dump(obj, fpt, indent=4)
        Cache.update(path, obj)
        return path


class Workdir:

    wdr = ""


    @staticmethod
    def init(name):
        Workdir.wdr = os.path.expanduser(f"~/.{name}")


def cdir(path):
    pth = pathlib.Path(path)
    pth.parent.mkdir(parents=True, exist_ok=True)


def fqn(obj):
    kin = str(type(obj)).split()[-1][1:-2]
    if kin == "type":
        kin = f"{obj.__module__}.{obj.__name__}"
    return kin


def getpath(obj):
    return store(ident(obj))


def ident(obj):
    return os.path.join(fqn(obj), *str(datetime.datetime.now()).split())


def moddir(modname=None):
    return os.path.join(Workdir.wdr, modname or "mods")


def pidname(name):
    assert Workdir.wdr
    return os.path.join(Workdir.wdr, f"{name}.pid")


def skel():
    pth = pathlib.Path(store())
    pth.mkdir(parents=True, exist_ok=True)
    pth = pathlib.Path(moddir())
    pth.mkdir(parents=True, exist_ok=True)


def store(fnm=""):
    return os.path.join(Workdir.wdr, "store", fnm)


def types():
    return os.listdir(store())


def __dir__():
    return (
        'Cache',
        'Workdir',
        'cdir',
        'find',
        'fntime',
        'fqn',
        'fqn',
        'getpath',
        'ident',
        'read',
        'skel',
        'types',
        'write'
    )
