from unidecode import unidecode


def clean_string(string):
    return unidecode(string.strip().lower())
