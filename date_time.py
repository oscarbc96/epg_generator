from datetime import datetime

from pytz import timezone


class DateTime(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(DateTime)

        return cls.__instance

    def __init__(self):
        if DateTime.__instance is None:
            DateTime.__instance = self

    def parse(self, time):
        return datetime.strptime(time, "%Y-%m-%d %H:%M:%S")

    def format(self, time):
        time = timezone("Europe/Madrid").localize(time)
        return datetime.strftime(time, "%Y%m%d%H%M%S %z")
