import itertools
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from multiprocessing import Pool, cpu_count

from diskcache import Cache

from conf import OUTPUT_FOLDER, CACHE_FOLDER, EPG_FILE, DOWNLOAD_EXTRA_INFO, DAYS_TO_DOWNLOAD, DELAYS, HD_CHANNELS, \
    CHANNELS_TO_DOWNLOAD
from date_time import DateTime
from movistar import Movistar


class EPGGenerator(object):

    def __init__(self):
        self.cache = Cache(CACHE_FOLDER)

    def run(self):
        movistar_data = self.download_movistar_data()

        channels_data, programmes_data = self.merge_movistar_data(movistar_data)

        channels, programmes = self.generate_epg_data(channels_data, programmes_data)

        self.dump_epg_data(channels, programmes)

        self.cache.expire()

    def download_movistar_data(self):
        print("Downloading movistar data...")
        return [
            Movistar.get_programation(
                (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d"),
                CHANNELS_TO_DOWNLOAD,
            )
            for days in range(-1, DAYS_TO_DOWNLOAD)
        ]

    def merge_movistar_data(self, data):
        data_channels = []
        data_programmes = []

        for dt in data:
            data_channels.extend(dt["channels"])

        for dt in data:
            data_programmes.extend(dt["channelsProgram"][0])
            data_programmes.extend(dt["channelsProgramDayBefore"][0])

        channels = list({v["cod_cadena_tv"]: v for v in data_channels}.values())

        programmes = list({v["cod_evento_rejilla"]: v for v in data_programmes}.values())

        return channels, programmes

    def create_channels(self, channel_data):
        channels = [self.create_channel(channel_data)]

        if channel_data["cod_cadena_tv"] in HD_CHANNELS:
            channel = dict(channels[0])  # We clone the original channel
            channel["name"] = f"{channel['name']} HD"
            channel["code"] = f"{channel['code']} HD"
            channels.append(channel)

        delays = DELAYS.get(channel_data["cod_cadena_tv"], 0)
        for delay in range(1, delays + 1):
            channel = dict(channels[0])  # We clone the original channel
            channel["name"] = f"{channel['name']}-{delay}h"
            channel["code"] = f"{channel['code']}-{delay}h"
            channels.append(channel)
        return channels

    def create_channel(self, channel):
        return {
            "name": channel["des_cadena_tv"],
            "code": channel["cod_cadena_tv"],
            "logo": Movistar.get_channel_logo(channel["cod_cadena_tv"])
        }

    def create_programmes(self, programme_data):
        programmes = [self.create_programme(programme_data)]

        if programme_data["cod_cadena_tv"] in HD_CHANNELS:
            programme = dict(programmes[0])  # We clone the original programme
            programme["channel"] = f"{programme['channel']} HD"
            programmes.append(programme)

        delays = DELAYS.get(programme_data["cod_cadena_tv"], 0)
        for delay in range(1, delays + 1):
            programme = dict(programmes[0])  # We clone the original programme
            programme["channel"] = f"{programme['channel']}-{delay}h"
            programme["start"] += timedelta(hours=delay)
            programme["stop"] += timedelta(hours=delay)
            programmes.append(programme)

        return programmes

    def create_programme(self, programme):
        cer = programme["cod_evento_rejilla"]

        if cer in self.cache:
            return self.cache.get(cer)

        info = {
            "channel": programme["cod_cadena_tv"],
            "title": programme["des_evento_rejilla"],
            "category": programme["des_genero"],
            "start": DateTime().parse(programme["f_evento_rejilla"]),
            "stop": DateTime().parse(programme["f_fin_evento_rejilla"])
        }

        cee = programme["cod_elemento_emision"]
        if cee and DOWNLOAD_EXTRA_INFO:
            info.update(Movistar.get_extra_info(cee))

        # DAYS_TO_DOWNLOAD + 1 we add the day before data | 86400 seconds in a day
        expire_time = (DAYS_TO_DOWNLOAD + 1) * 86400
        self.cache.set(cer, info, expire=expire_time)

        return info

    def generate_epg_data(self, channels, programmes):
        print("Generating epg data...")

        p = Pool(cpu_count())
        epg_channels = p.map(self.create_channels, channels)
        p.terminate()
        p.join()

        p = Pool(cpu_count())
        epg_programmes = p.map(self.create_programmes, programmes)
        p.terminate()
        p.join()

        return itertools.chain(*epg_channels), itertools.chain(*epg_programmes)

    def dump_epg_data(self, channels, programmes):
        print("Dumping epg data to xml...")

        tv = ET.Element("tv")
        tv.set("date", datetime.now().strftime("%Y-%m-%d"))
        tv.set("source-info-url", "http://comunicacion.movistarplus.es/programacion/")
        tv.set("source-info-name", "Movistar")
        tv.set("generator-info-name", "Movistar EPG generator")
        tv.set("generator-info-url", "https://github.com/oscarbc96/epg_generator")

        for channel_data in channels:
            channel = ET.SubElement(tv, "channel")
            channel.set("id", channel_data["code"])

            display_name = ET.SubElement(channel, "display-name")
            display_name.set("lang", "es")
            display_name.text = channel_data["name"]

            icon = ET.SubElement(channel, "icon")
            icon.set("src", channel_data["logo"])

        for programme_data in programmes:
            programme = ET.SubElement(tv, "programme")
            programme.set("start", DateTime().format(programme_data["start"]))
            programme.set("stop", DateTime().format(programme_data["stop"]))
            programme.set("channel", programme_data["channel"])

            title = ET.SubElement(programme, "title")
            title.set("lang", "es")
            title.text = programme_data["title"]

            category = ET.SubElement(programme, "category")
            category.set("lang", "es")
            category.text = programme_data["category"]

            if "desc" in programme_data:
                desc = ET.SubElement(programme, "desc")
                desc.set("lang", "es")
                desc.text = programme_data["desc"]

            if "image" in programme_data:
                icon = ET.SubElement(programme, "icon")
                icon.set("src", programme_data["image"])

            if "age_rating" in programme_data:
                rating = ET.SubElement(programme, "rating")
                rating.set("system", "ES")

                value = ET.SubElement(rating, "value")
                value.text = programme_data["age_rating"]

            if "details" in programme_data:
                details = programme_data["details"]

                if "temporada" in details and "capitulo" in details:
                    season = details["temporada"]
                    chapter = details["capitulo"]

                    episode_num = ET.SubElement(programme, "episode-num")
                    episode_num.set("system", "xmltv_ns")
                    episode_num.text = f"{season}.{chapter}.0/1"

                credits = ET.SubElement(programme, "credits")

                if "actor" in details:
                    for actor_data in details["actor"]:
                        actor = ET.SubElement(credits, "actor")
                        actor.text = actor_data

                if "director" in details:
                    for director_data in details["director"]:
                        director = ET.SubElement(credits, "director")
                        director.text = director_data

        xml = ET.tostring(tv, encoding="ISO-8859-1", method="xml")

        if not os.path.exists(OUTPUT_FOLDER):
            os.makedirs(OUTPUT_FOLDER)

        output = open(EPG_FILE, "wb")

        output.write(xml)

        output.close()


if __name__ == "__main__":
    print("EPG Generator")

    print(f"N. cores: {cpu_count()}")

    print(f"Download extra info: {DOWNLOAD_EXTRA_INFO}")

    print(f"Days to download: {DAYS_TO_DOWNLOAD}")

    start = datetime.now()

    print(f"Start: {start}")

    EPGGenerator().run()

    stop = datetime.now()

    print(f"Stop: {stop}")

    print(f"Execution time: {stop - start}")
