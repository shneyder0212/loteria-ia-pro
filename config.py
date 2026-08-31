from zoneinfo import ZoneInfo

TZ_RD = ZoneInfo("America/Santo_Domingo")
TZ_ES = ZoneInfo("Europe/Madrid")

SALAS = [
    ("anguila_10am", "Anguila Mañana (10:00 AM)", "quiniela", "rd"),
    ("primera_dia", "La Primera Día (12:00 PM)", "quiniela", "rd"),
    ("lotedom", "LoteDom (12:00 PM)", "quiniela", "rd"),
    ("real", "Lotería Real (12:55 PM)", "quiniela", "rd"),
    ("anguila_1pm", "Anguila Mediodía (1:00 PM)", "quiniela", "rd"),
    ("gana_mas", "Gana Más (2:30 PM)", "quiniela", "rd"),
    ("anguila_6pm", "Anguila Tarde (6:00 PM)", "quiniela", "rd"),
    ("loteka", "Loteka (7:55 PM)", "quiniela", "rd"),
    ("primera_noche", "La Primera Noche (8:00 PM)", "quiniela", "rd"),
    ("nacional_noche", "Nacional Noche (8:50 PM)", "quiniela", "rd"),
    ("leidsa", "Leidsa (8:55 PM)", "quiniela", "rd"),
    ("anguila_9pm", "Anguila Noche (9:00 PM)", "quiniela", "rd"),
    ("kino_leidsa", "Kino Leidsa TV", "kino", "rd"),
    ("primitiva_esp", "La Primitiva", "primitiva", "esp"),
    ("euromillones", "Euromillones", "euromillones", "esp"),
]

RD_NOMBRES = {
    "gana_mas": ["Loteria Nacional- Gana Más", "Gana Más"],
    "nacional_noche": ["Loteria Nacional- Noche", "Lotería Nacional"],
    "real": ["Quiniela Real", "Lotería Real"],
    "loteka": ["Quiniela Loteka", "Loteka"],
    "primera_dia": ["Quiniela La Primera", "La Primera"],
    "primera_noche": ["Quiniela La Primera Noche", "Primera Noche"],
    "lotedom": ["Quiniela Lotedom", "LoteDom"],
    "leidsa": ["Quiniela Leidsa", "Leidsa"],
}

CONECTATE_URLS = {
    "gana_mas": "https://loterias.conectate.com.do/nacional/gana-mas/",
    "nacional_noche": "https://loterias.conectate.com.do/nacional/quiniela/",
    "real": "https://loterias.conectate.com.do/loto-real/quiniela/",
    "loteka": "https://loterias.conectate.com.do/loteka/quiniela-mega-decenas/",
    "primera_dia": "https://loterias.conectate.com.do/la-primera/quiniela-medio-dia/",
    "primera_noche": "https://loterias.conectate.com.do/la-primera/quiniela-noche/",
    "lotedom": "https://loterias.conectate.com.do/lotedom/quiniela/",
    "leidsa": "https://loterias.conectate.com.do/leidsa/quiniela-pale/",
}


# Cortes de estudio en hora de República Dominicana.
# Cada bloque usa solo información disponible antes de su hora de publicación.
CORTES_RD = {
    "manana": {
        "hora": 5,
        "minuto": 0,
        "titulo": "ESTUDIO MAÑANA",
        "salas": ["anguila_10am","primera_dia","lotedom","real","anguila_1pm"],
    },
    "tarde": {
        "hora": 13,
        "minuto": 15,
        "titulo": "REESTUDIO TARDE",
        "salas": ["gana_mas","anguila_6pm","loteka"],
    },
    "noche": {
        "hora": 19,
        "minuto": 0,
        "titulo": "REESTUDIO NOCTURNO",
        "salas": ["primera_noche","nacional_noche","leidsa","anguila_9pm","kino_leidsa"],
    },
}
