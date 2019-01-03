import requests
import xml.etree.ElementTree as ET

from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from conf import DAYS_TO_DOWNLOAD, EPG_FILE, MOVISTAR_AJAX_URL, MOVISTAR_CHANNEL_LOGO_URL, MOVISTAR_DESCRIPTION


class Movistar(object):
    @classmethod
    def get_channels(self):
        payload = {
            "action": "getChannels",
        }

        response = requests.post(MOVISTAR_AJAX_URL, data=payload)

        return [ch["cod_cadena_tv"] for ch in response.json()]

    @classmethod
    def get_programation(self, date, channels):
        payload = {
            "action": "getProgramation",
            "categorires": "",
            "channels[]": channels,
            "day": date
        }

        response = requests.post(MOVISTAR_AJAX_URL, data=payload)

        return response.json()

    @classmethod
    def get_channel_logo(self, channel):
        return MOVISTAR_CHANNEL_LOGO_URL + channel

    @classmethod
    def get_extra_info(self, cee):
        info = {}

        url = MOVISTAR_DESCRIPTION + cee

        response = requests.get(url)

        soup = BeautifulSoup(response.content, "html.parser")

        # info["image"] = soup.find("img", class_="img-v-detail")["src"]

        info["desc"] = soup.find("div", class_="sinopsis_large").find(text=True, recursive=False).strip()

        # info["details"] = {}

        # details = soup.find("div", class_="details_container").find_all("div")

        # for i in range(0, len(details)-1, 2):
        #     title = details[i].text.strip().capitalize()
        #     value_item = details[i+1].find("span", class_="details_value")

        #     content_list = value_item.find_all("span")
        #     if content_list:
        #         value = ", ".join([v.text.strip() for v in content_list])
        #     else:
        #         value = value_item.text.strip()

        #     info["details"][title] = value

        # info["age_restriction"] = soup.find("span", class_="nivel_moral").text.strip()

        return info

    @classmethod
    def parse_time(self, time):
        time = time.replace("-", "")
        time = time.replace(" ", "")
        time = time.replace(":", "")

        return time + " +0000"


class EPGGenerator(object):

    def run(self):
        movistar_data = self.download_movistar_data()

        channels, programmes = self.generate_epg_data(movistar_data)

        self.dump_epg_data(channels, programmes)

    def download_movistar_data(self):
        today = datetime.now()

        date_str = today.strftime("%Y-%m-%d")

        channels = Movistar.get_channels()

        return Movistar.get_programation(date_str, channels)

    def generate_epg_data(self, data):
        # ["date", "channels", "channelsProgram", "channelsProgramDayBefore"]

        channels = []
        programmes = []

        for channel in data["channels"]:
            channels.append({
                "name": channel["des_cadena_tv"],
                "code": channel["cod_cadena_tv"],
                "logo": Movistar.get_channel_logo(channel["cod_cadena_tv"])
            })

        for programme in data["channelsProgram"][0]:
            start_time = Movistar.parse_time(programme["f_evento_rejilla"])
            stop_time = Movistar.parse_time(programme["f_fin_evento_rejilla"])

            info = {
                "channel": programme["cod_cadena_tv"],
                "title": programme["des_evento_rejilla"],
                "category": programme["des_genero"],
                "start": start_time,
                "stop": stop_time
            }

            # cee = programme["cod_elemento_emision"]
            # if cee:
            #     info.update(Movistar.get_extra_info(cee))

            programmes.append(info)

        return channels, programmes

    def dump_epg_data(self, channels, programmes):
        tv = ET.Element("tv")

        for channel_data in channels:
            channel = ET.SubElement(tv, "channel")
            channel.set("id", channel_data["code"])

            display_name = ET.SubElement(channel, "display-name")
            display_name.set("lang", "es")
            display_name.text = channel_data["name"]

            icon = ET.SubElement(channel, "display-name")
            icon.set("src", channel_data["logo"])

        for programme_data in programmes:
            programme = ET.SubElement(tv, "programme")
            programme.set("start", programme_data["start"])
            programme.set("stop", programme_data["stop"])
            programme.set("channel", programme_data["channel"])

            title = ET.SubElement(programme, "title")
            title.set("lang", "es")
            title.text = programme_data["title"]

            category = ET.SubElement(programme, "category")
            category.set("lang", "es")
            category.text = programme_data["category"]

            # if "desc" in programme:
            #     desc = ET.SubElement(programme, "desc")
            #     desc.set("lang", "es")
            #     desc.text = programme_data["desc"]

        xml = ET.tostring(tv, encoding="utf8", method="xml")

        output = open(EPG_FILE, "wb")

        output.write(xml)

        output.close()


if __name__ == "__main__":
    EPGGenerator().run()
