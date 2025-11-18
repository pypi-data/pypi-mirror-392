
## configurari de client ##
VERSION = "V 3.11"
GAME_VERSION_URL = "https://empire-html5.goodgamestudios.com/default/items/ItemsVersion.properties"
CLIENT_ORIGIN = "https://empire-html5.goodgamestudios.com"
SERVERS_DB = "https://empire-html5.goodgamestudios.com/config/network/1.xml"
LANG_DB = "https://langserv.public.ggs-ep.com/em/en"


## client headers ##
WS_HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "identity",  
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Connection": "Upgrade",
    "Upgrade": "websocket",
    "Sec-WebSocket-Version": "13",
    "Origin": "https://empire.goodgamestudios.com",
}


AD_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "identity",  
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Connection": "keep-alive",
    "Referer": "https://empire.goodgamestudios.com/",
    "Origin": "https://empire.goodgamestudios.com",
    "Accept-Language": "en-US,en;q=0.9",
}


## client users_agents ##
DEFAULT_UA_LIST = [
    # — Browsere moderne (versiuni actualizate pentru HTML5/WebGL) —
    # Google Chrome pe Windows 11
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36",

    # Google Chrome pe macOS Sonoma (14_0)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36",

    # Mozilla Firefox pe Windows 11
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) "
    "Gecko/20100101 Firefox/120.0",

    # Mozilla Firefox pe macOS Sonoma (14_0)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0; rv:120.0) "
    "Gecko/20100101 Firefox/120.0",

    # Microsoft Edge pe Windows 11
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",

    # Apple Safari pe macOS Sonoma (14_0)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/17.4 Safari/605.1.15",

    # Opera (Blink) pe Windows 11
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36 OPR/103.0.4924.32",


    # — Intrări din DEFAULT_UA_LIST (fișier) —
    # Chrome pe Windows 10
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0.5790.98 Safari/537.36",

    # Chrome pe macOS (10_15_7)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0.0.0 Safari/537.36",

    # Chrome pe Linux
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36",

    # Firefox pe Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:114.0) "
    "Gecko/20100101 Firefox/114.0",

    # Firefox pe macOS (10.15)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:112.0) "
    "Gecko/20100101 Firefox/112.0",

    # Safari pe macOS (10_15_7)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/14.0 Safari/605.1.15",

    # Edge pe Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36 Edg/114.0.0.0",

    # Opera pe Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0",
]

G_SERVERS = {
    "International 1": ("wss://ep-live-mz-int1-sk1-gb1-game.goodgamestudios.com", "EmpireEx"),
    "Germany 1": ("wss://ep-live-de1-game.goodgamestudios.com", "EmpireEx_2"),
    "France 1": ("wss://ep-live-fr1-game.goodgamestudios.com", "EmpireEx_3"),
    "Czech Republic 1": ("wss://ep-live-mz-cz1-es2-game.goodgamestudios.com", "EmpireEx_4"),
    "Poland 1": ("wss://ep-live-pl1-game.goodgamestudios.com", "EmpireEx_5"),
    "Portuguese 1": ("wss://ep-live-pt1-game.goodgamestudios.com", "EmpireEx_6"),
    "International 2": ("wss://ep-live-mz-int2-es1-it1-game.goodgamestudios.com", "EmpireEx_7"),
    "Spain 1": ("wss://ep-live-mz-int2-es1-it1-game.goodgamestudios.com", "EmpireEx_8"),
    "Italy 1": ("wss://ep-live-mz-int2-es1-it1-game.goodgamestudios.com", "EmpireEx_9"),
    "Turkey 1": ("wss://ep-live-mz-tr1-nl1-bg1-game.goodgamestudios.com", "EmpireEx_10"),
    "Netherlands 1": ("wss://ep-live-mz-tr1-nl1-bg1-game.goodgamestudios.com", "EmpireEx_11"),
    "Hungary 1": ("wss://ep-live-mz-hu1-skn1-gr1-lt1-game.goodgamestudios.com", "EmpireEx_12"),
    "Nordic 1": ("wss://ep-live-mz-hu1-skn1-gr1-lt1-game.goodgamestudios.com", "EmpireEx_13"),
    "Russia 1": ("wss://ep-live-ru1-game.goodgamestudios.com", "EmpireEx_14"),
    "Romania 1": ("wss://ep-live-ro1-game.goodgamestudios.com", "EmpireEx_15"),
    "Bulgaria 1": ("wss://ep-live-mz-tr1-nl1-bg1-game.goodgamestudios.com", "EmpireEx_16"),
    "Hungary 2": ("wss://ep-live-hu2-game.goodgamestudios.com", "EmpireEx_17"),
    "Slovakia 1": ("wss://ep-live-mz-int1-sk1-gb1-game.goodgamestudios.com", "EmpireEx_18"),
    "United Kingdom 1": ("wss://ep-live-mz-int1-sk1-gb1-game.goodgamestudios.com", "EmpireEx_19"),
    "Brazil 1": ("wss://ep-live-br1-game.goodgamestudios.com", "EmpireEx_20"),
    "United States 1": ("wss://ep-live-us1-game.goodgamestudios.com", "EmpireEx_21"),
    "Australia 1": ("wss://ep-live-au1-game.goodgamestudios.com", "EmpireEx_22"),
    "South Korea 1": ("wss://ep-live-mz-kr1-jp1-in1-cn1-game.goodgamestudios.com", "EmpireEx_23"),
    "Japan 1": ("wss://ep-live-mz-kr1-jp1-in1-cn1-game.goodgamestudios.com", "EmpireEx_24"),
    "Hispanic America 1": ("wss://ep-live-his1-game.goodgamestudios.com", "EmpireEx_25"),
    "India 1": ("wss://ep-live-mz-kr1-jp1-in1-cn1-game.goodgamestudios.com", "EmpireEx_26"),
    "China 1": ("wss://ep-live-mz-kr1-jp1-in1-cn1-game.goodgamestudios.com", "EmpireEx_27"),
    "Greece 1": ("wss://ep-live-mz-hu1-skn1-gr1-lt1-game.goodgamestudios.com", "EmpireEx_28"),
    "Lithuania 1": ("wss://ep-live-mz-hu1-skn1-gr1-lt1-game.goodgamestudios.com", "EmpireEx_29"),
    "Saudi Arabia 1": ("wss://ep-live-mz-sa1-ae1-eg1-arab1-game.goodgamestudios.com", "EmpireEx_32"),
    "United Arab Emirates 1": ("wss://ep-live-mz-sa1-ae1-eg1-arab1-game.goodgamestudios.com", "EmpireEx_33"),
    "Egypt 1": ("wss://ep-live-mz-sa1-ae1-eg1-arab1-game.goodgamestudios.com", "EmpireEx_34"),
    "Arab League 1": ("wss://ep-live-mz-sa1-ae1-eg1-arab1-game.goodgamestudios.com", "EmpireEx_35"),
    "Asia 1": ("wss://ep-live-mz-asia1-hant1-game.goodgamestudios.com", "EmpireEx_36"),
    "Chinese (traditional) 1": ("wss://ep-live-mz-asia1-hant1-game.goodgamestudios.com", "EmpireEx_37"),
    "Spain 2": ("wss://ep-live-mz-cz1-es2-game.goodgamestudios.com", "EmpireEx_38"),
    "International 3": ("wss://ep-live-int3-game.goodgamestudios.com", "EmpireEx_43"),
    "World 1": ("wss://ep-live-world1-game.goodgamestudios.com", "EmpireEx_46"),
}