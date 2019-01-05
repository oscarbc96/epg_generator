import requests
from bs4 import BeautifulSoup

from age_rating import AgeRating
from utils import clean_string
from conf import MOVISTAR_AJAX_URL, MOVISTAR_CHANNEL_LOGO_URL, MOVISTAR_DESCRIPTION_URL


class Movistar(object):
    @classmethod
    def get_channels(self):
        print("Getting movistar channels...")

        payload = {
            "action": "getChannels",
        }

        response = requests.post(MOVISTAR_AJAX_URL, data=payload)

        return [ch["cod_cadena_tv"] for ch in response.json()]

    @classmethod
    def get_programation(self, date, channels):
        print(f"Getting movistar programmes of {date}...")

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
        print(f"Downloading extra info for {cee}")

        info = {}

        url = MOVISTAR_DESCRIPTION_URL + cee

        response = requests.get(url)

        soup = BeautifulSoup(response.content, "html.parser")

        info["image"] = soup.find("img", class_="img-v-detail")["src"]

        info["desc"] = soup.find("div", class_="sinopsis_large").find(text=True, recursive=False).strip()

        info["details"] = {}

        details = soup.find("div", class_="details_container").find_all("div")

        for i in range(0, len(details)-1, 2):
            title = clean_string(details[i].text)
            value_item = details[i+1].find("span", class_="details_value")

            content_list = value_item.find_all("span")
            if content_list:
                value = [v.text.strip() for v in content_list]
            else:
                value = value_item.text.strip()

            info["details"][title] = value

        info["age_rating"] = AgeRating.from_str(soup.find("span", class_="nivel_moral").text)

        return info