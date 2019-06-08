from os.path import dirname, realpath, join

SCRIPT_FOLDER = dirname(realpath(__file__))

CACHE_FOLDER = join(SCRIPT_FOLDER, "cache/")
OUTPUT_FOLDER = join(SCRIPT_FOLDER, "output/")
EPG_FILE = join(OUTPUT_FOLDER, "epg.xml")

MOVISTAR_AJAX_URL = "https://comunicacion.movistarplus.es/wp-admin/admin-ajax.php"
MOVISTAR_CHANNEL_LOGO_URL = "https://www.movistarplus.es/recorte/m-NEO/canal/"
MOVISTAR_DESCRIPTION_URL = "https://comunicacion.movistarplus.es/detalle-de-programacion/?cee="

DOWNLOAD_EXTRA_INFO = False

DAYS_TO_DOWNLOAD = 2

HD_CHANNELS = []

DELAYS = {}
