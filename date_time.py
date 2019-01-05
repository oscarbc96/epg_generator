from datetime import datetime, timedelta
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

        now = datetime.now()

        now_tz = timezone("Europe/Madrid").localize(now)

        self.tz = now_tz.strftime("%z")

    def format_time(self, time):
        time = time.replace("-", "")
        time = time.replace(" ", "")
        time = time.replace(":", "")

        return time + " " + self.tz

    def get_date_str(self, in_future):
        today = datetime.now()

        future_date = today + timedelta(days=in_future)

        return future_date.strftime("%Y-%m-%d")
