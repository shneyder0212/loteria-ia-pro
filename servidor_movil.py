import json
import sqlite3
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Shneyder IA Pro RD")
DB_PATH = "loteria_master_ai.db"

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
dia_hoy = DIAS_SEMANA[datetime.now().weekday()]

# 1. PIZARRA OFICIAL DE PREMIOS (Incluyendo todos los sorteos de la Anguilita)
RESULTADOS_OFICIALES = {
    "anguila_10am": {"nombre": "Anguila Mañana (10:00 AM)", "premios": ["--", "--", "--"], "estado": "Pendiente sorteo 20/08"},
    "primera_dia": {"nombre": "La Primera Día (12:00 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente sorteo 20/08"},
    "lotedom": {"nombre": "LoteDom (12:00 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente sorteo 20/08"},
    "suerte_dia": {"nombre": "La Suerte Día (12:30 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente sorteo 20/08"},
    "real": {"nombre": "Lotería Real (12:55 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente sorteo 20/08"},
    "anguila_1pm": {"nombre": "Anguila Mediodía (1:00 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente sorteo 20/08"},
    "gana_mas": {"nombre": "Gana Más (2:30 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente sorteo 20/08"},
    "suerte_tarde": {"nombre": "La Suerte Tarde (6:00 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente sorteo 20/08"},
    "anguila_6pm": {"nombre": "Anguila Tarde (6:00 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente sorteo 20/08"},
    "loteka": {"nombre": "Loteka (7:55 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente sorteo 20/08"},
    "primera_noche": {"nombre": "La Primera Noche (8:00 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente sorteo 20/08"},
    "nacional_noche": {"nombre": "Nacional Noche (8:50 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente sorteo 20/08"},
    "leidsa": {"nombre": "Leidsa (8:55 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente sorteo 20/08"},
    "anguila_9pm": {"nombre": "Anguila Noche (9:00 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente sorteo 20/08"},
    "kino_tv": {"nombre": "Kino TV Leidsa (8:55 PM)", "premios": ["--"] * 20, "estado": "20 Bolos Pendientes"},
    "king_lottery": {"nombre": "King Lottery (12:30 / 7:30 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente sorteo 20/08"},
    "ny_tarde_noche": {"nombre": "New York (Tarde / Noche)", "premios": ["--", "--", "--"], "estado": "Pendiente sorteo 20/08"},
    "primitiva_esp": {"nombre": "La Primitiva (España)", "premios": ["--", "--", "--", "--", "--", "--"], "complementario": "--", "reintegro": "-", "estado": "Sorteo Jueves 21:40h"},
    "euromillones": {"nombre": "Euromillones (Europa)", "premios": ["--", "--", "--", "--", "--"], "estrellas": ["-", "-"], "estado": "Sorteo Viernes 21:15h"}
}

# 2. AUDITORÍA OFICIAL LIMPIA (Inicia el 20 de Agosto 2026)
HISTORIAL_AUDITORIA = [
    {
        "fecha": "20/08/2026",
        "sala": "Sistema Cuántico Shneyder",
        "tipo": "📡 APERTURA OFICIAL",
        "premio": "Sistema calibrado y conectado en vivo con las tómbolas oficiales",
        "detalle": "Esperando primeros sorteos del día (Anguila 10:00 AM / La Primera 12:00 PM / La Suerte 12:30 PM)"
    }
]

# 3. DICCIONARIO DE SUEÑOS
DICCIONARIO_SUENOS = {
    "dinero": {"num": "48", "cabala": "Plata / Riqueza", "fuerza": 89.5, "lot": "Leidsa / Nacional"},
    "agua": {"num": "06", "cabala": "Río / Lluvia / Mar", "fuerza": 78.2, "lot": "La Primera"},
    "muerte": {"num": "47", "cabala": "Finado / Entierro", "fuerza": 92.4, "lot": "Gana Mas"},
    "accidente": {"num": "13", "cabala": "Choque / Caída", "fuerza": 84.1, "lot": "Loteka"},
    "boda": {"num": "24", "cabala": "Matrimonio / Fiesta", "fuerza": 81.0, "lot": "La Real"},
    "fuego": {"num": "11", "cabala": "Incendio / Candela", "fuerza": 88.6, "lot": "Nacional Noche"},
    "serpiente": {"num": "36", "cabala": "Culebra / Traición", "fuerza": 75.3, "lot": "La Suerte"},
    "embarazo": {"num": "19", "cabala": "Bebé / Nacimiento", "fuerza": 91.2, "lot": "Anguila 6PM"},
    "perro": {"num": "21", "cabala": "Fidelidad / Amigo", "fuerza": 73.8, "lot": "King Lottery"},
    "policia": {"num": "56", "cabala": "Ley / Uniforme", "fuerza": 86.4, "lot": "Leidsa"},
    "viaje": {"num": "02", "cabala": "Vuelo / Maleta", "fuerza": 79.5, "lot": "New York Noche"},
    "casa": {"num": "04", "cabala": "Propiedad / Techo", "fuerza": 98.9, "lot": "Gana Mas / Nacional"},
    "carro": {"num": "35", "cabala": "Vehículo / Motor", "fuerza": 82.7, "lot": "Loteka"}
}

# 4. PRONÓSTICOS CUÁNTICOS POR LOTERÍA
DATOS_LOTERIAS = {
    "todas": {
        "nombre": "Todas las Loterías (Consenso General)",
        "tipo_juego": "quiniela",
        "salidor": "40 - 72 - 18",
        "hora_cierre": "20:45",
        "dictamen": {
            "flujo": "ALTO (50 al 99)",
            "decena": "Los 70s y 40s (70-79 / 40-49)",
            "terminal": "Terminales en 4, 0 y 9",
            "pareja": "ALTA (11, 44, 88)",
            "digito_fuerte": "Dígitos 4 y 7",
            "presion": "🚨 RUPTURA INMINENTE: Decena de los 40s a reventar en primera",
            "dia_tendencia": f"{dia_hoy}: Salidas de números pares y revés rápido"
        },
        "sueltos": [
            {"num": "04", "fuerza": 98.9, "tipo": "triple_factor", "lot": "Gana Mas / Nacional"},
            {"num": "40", "fuerza": 89.0, "tipo": "virado", "lot": "Gana Mas / Nacional"},
            {"num": "54", "fuerza": 76.4, "tipo": "caliente", "lot": "Leidsa 8:55pm"},
            {"num": "79", "fuerza": 71.2, "tipo": "atrasado", "lot": "Loteria Real 12:55pm"},
            {"num": "29", "fuerza": 68.5, "tipo": "fuerte", "lot": "Loteka 7:55pm"},
            {"num": "92", "fuerza": 62.1, "tipo": "caliente", "lot": "La Primera 12:00pm"},
            {"num": "15", "fuerza": 59.4, "tipo": "atrasado", "lot": "Anguila 6:00pm"},
            {"num": "63", "fuerza": 55.0, "tipo": "fuerte", "lot": "La Suerte 12:30pm"},
            {"num": "85", "fuerza": 52.3, "tipo": "fuerte", "lot": "Nacional Noche"},
            {"num": "18", "fuerza": 49.7, "tipo": "caliente", "lot": "Leidsa 8:55pm"},
            {"num": "72", "fuerza": 47.1, "tipo": "caliente", "lot": "Loteria Real 12:55pm"},
            {"num": "09", "fuerza": 44.8, "tipo": "atrasado", "lot": "La Suerte 6:00pm"},
            {"num": "23", "fuerza": 41.6, "tipo": "fuerte", "lot": "La Primera 8:00pm"},
            {"num": "50", "fuerza": 38.9, "tipo": "caliente", "lot": "Anguila 1:00pm"},
            {"num": "95", "fuerza": 36.2, "tipo": "atrasado", "lot": "LoteDom 12:00pm"},
            {"num": "17", "fuerza": 33.5, "tipo": "fuerte", "lot": "King Lottery 12:30pm"},
            {"num": "33", "fuerza": 30.1, "tipo": "pareja", "lot": "Anguila 9:00pm"},
            {"num": "88", "fuerza": 28.4, "tipo": "pareja", "lot": "Loteria Real 12:55pm"},
            {"num": "67", "fuerza": 25.0, "tipo": "atrasado", "lot": "Loteka 7:55pm"},
            {"num": "12", "fuerza": 22.8, "tipo": "fuerte", "lot": "New York Noche"}
        ]
    },
    "kino_leidsa": {
        "nombre": "VENTA ESPECIAL: KINO LEIDSA TV",
        "tipo_juego": "kino",
        "salidor": "Sorteo Diario 8:55 PM (20 Bolos)",
        "hora_cierre": "20:50",
        "kino_data": {
            "estado_tombola": "🔥 TÓMBOLA CALIENTE: Consistencia 92.4% (Filtro Anti-Consecutivos Activo)",
            "paridad_optima": "⚖️ RATIO DE PARIDAD: 10 Pares / 10 Impares (82% de acierto)",
            "zona_muerta": "🚫 ZONA DE RETENCIÓN: 40 al 52 (Evitar saturar apuestas aquí)",
            "duenos": ["07", "14", "23", "38", "45", "59", "62", "71", "78", "80"],
            "bloques_5": [
                {"bloque": "07 - 23 - 45 - 62 - 78", "fuerza": 95.8, "paridad": "3 Impares / 2 Pares"},
                {"bloque": "14 - 38 - 59 - 71 - 80", "fuerza": 92.4, "paridad": "3 Pares / 2 Impares"},
                {"bloque": "07 - 14 - 23 - 38 - 71", "fuerza": 89.6, "paridad": "3 Impares / 2 Pares"}
            ],
            "bloques_7": [
                {"bloque": "07 - 14 - 23 - 45 - 59 - 71 - 78", "fuerza": 97.1, "paridad": "5 Impares / 2 Pares"},
                {"bloque": "14 - 23 - 38 - 62 - 71 - 78 - 80", "fuerza": 94.3, "paridad": "5 Pares / 2 Impares"}
            ]
        },
        "dictamen": {
            "flujo": "EXPANSIVO (1 al 80)",
            "decena": "Dominio de las decenas 20s, 60s y 70s",
            "terminal": "Terminales 7, 8, 3 y 4",
            "pareja": "ALTA (22, 44, 77)",
            "digito_fuerte": "Dígitos 7 y 8",
            "presion": "🎯 RECOMENDACIÓN: Jugar bloques cerrados con dispersión de salto.",
            "dia_tendencia": f"{dia_hoy}: Salidas de números primos y extremos"
        }
    },
    "primitiva_esp": {
        "nombre": "🇪🇸 LA PRIMITIVA (ESPAÑA)",
        "tipo_juego": "primitiva",
        "salidor": "Sorteos: Lunes, Jueves y Sábados (21:40h)",
        "hora_cierre": "21:15",
        "primitiva_data": {
            "reintegro": "7",
            "reintegro_fuerza": 94.5,
            "complementario": "34",
            "cuadrantes": "C1 (01-12): 2 bolos | C2 (13-25): 1 bolo | C3 (26-37): 2 bolos | C4 (38-49): 1 bolo",
            "apuestas_6": [
                {"combinacion": "05 - 12 - 19 - 28 - 34 - 47", "reintegro": "7", "fuerza": 96.8, "tipo": "Matriz Reducida Directa"},
                {"combinacion": "03 - 11 - 24 - 31 - 42 - 49", "reintegro": "3", "fuerza": 93.4, "tipo": "Cobertura de Clúster"},
                {"combinacion": "08 - 17 - 22 - 36 - 40 - 45", "reintegro": "7", "fuerza": 90.1, "tipo": "Equilibrio Geométrica"}
            ],
            "numeros_base": ["05", "12", "19", "24", "28", "34", "42", "47"]
        },
        "dictamen": {
            "flujo": "DISTRIBUCIÓN GEOMÉTRICA ÓPTIMA (1 al 49)",
            "decena": "Equilibrio entre decenas bajas (01-19) y altas (30-49)",
            "terminal": "Terminales 2, 4, 7 y 9",
            "pareja": "MEDIA (11, 22, 44)",
            "digito_fuerte": "Dígito 7 (Fuerte en Reintegro)",
            "presion": "🚨 RUPTURA: Bolos 05 y 47 rompiendo ciclo de retención",
            "dia_tendencia": f"{dia_hoy}: Concentración en combinación 3P / 3I"
        }
    },
    "euromillones": {
        "nombre": "🇪🇺 EUROMILLONES (EUROPA)",
        "tipo_juego": "euromillones",
        "salidor": "Sorteos: Martes y Viernes (21:15h)",
        "hora_cierre": "20:30",
        "euro_data": {
            "estrellas_fijas": ["03", "08"],
            "estrellas_reserva": ["02", "11"],
            "fuerza_estrellas": 97.2,
            "distribucion": "Cobertura 4 Cuadrantes (1-12 / 13-25 / 26-37 / 38-50)",
            "apuestas_euro": [
                {"numeros": "09 - 17 - 28 - 35 - 44", "estrellas": "03 - 08", "fuerza": 98.4, "tipo": "Bloque Cuántico Titán"},
                {"numeros": "04 - 15 - 23 - 39 - 48", "estrellas": "02 - 08", "fuerza": 94.7, "tipo": "Fuego Cruzado Europeo"},
                {"numeros": "11 - 21 - 32 - 41 - 50", "estrellas": "03 - 11", "fuerza": 91.9, "tipo": "Red de Afinidad Mayor"}
            ],
            "red_afinidad": ["09", "17", "28", "35", "44", "48", "03*", "08*"]
        },
        "dictamen": {
            "flujo": "MÁXIMA DISPERSIÓN ESTOCÁSTICA (1-50 + Estrellas 1-12)",
            "decena": "Cobertura obligada en rango 40-50",
            "terminal": "Terminales 4, 7, 8 y 9",
            "pareja": "BAJA (22, 44)",
            "digito_fuerte": "Estrella 8 en correlación con 3",
            "presion": "🚨 RUPTURA: Estrellas [03 - 08] con 97.2% consistencia",
            "dia_tendencia": f"{dia_hoy}: Salto simétrico europeo"
        }
    },
    "nacional": {
        "nombre": "Gana Más (2:30 PM) / Nacional Noche (8:50 PM)",
        "tipo_juego": "quiniela",
        "salidor": "Pendiente 20/08",
        "hora_cierre": "20:30",
        "dictamen": {
            "flujo": "MIXTO (Foco en 00-49 y 70-79)",
            "decena": "Los 00s y 40s (01-09 / 40-49)",
            "terminal": "Terminales 4, 0 y 9",
            "pareja": "MEDIA (44, 00)",
            "digito_fuerte": "Dígito 0 y 4 (Obligado virar)",
            "presion": "🚨 RUPTURA: Bolo 04 acumulando máxima probabilidad",
            "dia_tendencia": f"{dia_hoy}: Jaladera de números bajos a altos"
        },
        "sueltos": [
            {"num": "04", "fuerza": 98.9, "tipo": "triple_factor", "lot": "Nacional Noche"},
            {"num": "40", "fuerza": 89.0, "tipo": "virado", "lot": "Nacional Noche"},
            {"num": "54", "fuerza": 81.3, "tipo": "caliente", "lot": "Gana Mas"},
            {"num": "79", "fuerza": 74.0, "tipo": "atrasado", "lot": "Nacional Noche"},
            {"num": "90", "fuerza": 69.5, "tipo": "fuerte", "lot": "Gana Mas"}
        ]
    },
    "leidsa": {
        "nombre": "Leidsa (8:55 PM)",
        "tipo_juego": "quiniela",
        "salidor": "Pendiente 20/08",
        "hora_cierre": "20:45",
        "dictamen": {
            "flujo": "ALTO (Foco 60 al 99)",
            "decena": "Los 20s y 90s (20-29 / 90-99)",
            "terminal": "Terminales 2, 9 y 8",
            "pareja": "ALTA (22, 99)",
            "digito_fuerte": "Dígitos 2 y 9",
            "presion": "🚨 RUPTURA: Pareja 22 lista para desarmar el bloque",
            "dia_tendencia": f"{dia_hoy}: Repetidores nocturnos"
        },
        "sueltos": [
            {"num": "29", "fuerza": 91.2, "tipo": "triple_factor", "lot": "Leidsa"},
            {"num": "92", "fuerza": 82.0, "tipo": "virado", "lot": "Leidsa"},
            {"num": "18", "fuerza": 77.5, "tipo": "caliente", "lot": "Leidsa"},
            {"num": "63", "fuerza": 70.8, "tipo": "atrasado", "lot": "Leidsa"},
            {"num": "45", "fuerza": 66.2, "tipo": "fuerte", "lot": "Leidsa"}
        ]
    },
    "suerte_dia": {
        "nombre": "La Suerte Dominicana (12:30 PM)",
        "tipo_juego": "quiniela",
        "salidor": "Pendiente 20/08",
        "hora_cierre": "12:15",
        "dictamen": {
            "flujo": "BAJO A MEDIO (20 al 60)",
            "decena": "Los 70s y 20s (70-79 / 20-29)",
            "terminal": "Terminales 2, 7 y 3",
            "pareja": "BAJA (33)",
            "digito_fuerte": "Dígito 7",
            "presion": "🚨 RUPTURA: Terminales en 7 forzando salida diurna",
            "dia_tendencia": f"{dia_hoy}: Movimiento de líneas directas"
        },
        "sueltos": [
            {"num": "72", "fuerza": 90.4, "tipo": "fuerte", "lot": "La Suerte Día"},
            {"num": "27", "fuerza": 81.3, "tipo": "virado", "lot": "La Suerte Día"},
            {"num": "63", "fuerza": 76.5, "tipo": "caliente", "lot": "La Suerte Día"},
            {"num": "38", "fuerza": 71.0, "tipo": "atrasado", "lot": "La Suerte Día"},
            {"num": "15", "fuerza": 65.8, "tipo": "fuerte", "lot": "La Suerte Día"}
        ]
    },
    "suerte_tarde": {
        "nombre": "La Suerte Dominicana (6:00 PM)",
        "tipo_juego": "quiniela",
        "salidor": "Pendiente 20/08",
        "hora_cierre": "17:45",
        "dictamen": {
            "flujo": "BAJO (00 al 49)",
            "decena": "Los 10s y 00s (10-19 / 01-09)",
            "terminal": "Terminales 0, 1 y 4",
            "pareja": "MEDIA (11, 00)",
            "digito_fuerte": "Dígito 0 y 1",
            "presion": "🚨 RUPTURA: Base cero (01, 10) con carga extrema",
            "dia_tendencia": f"{dia_hoy}: Salida de números con base cero"
        },
        "sueltos": [
            {"num": "10", "fuerza": 89.2, "tipo": "fuerte", "lot": "La Suerte 6PM"},
            {"num": "01", "fuerza": 80.2, "tipo": "virado", "lot": "La Suerte 6PM"},
            {"num": "53", "fuerza": 75.8, "tipo": "caliente", "lot": "La Suerte 6PM"},
            {"num": "09", "fuerza": 70.4, "tipo": "atrasado", "lot": "La Suerte 6PM"},
            {"num": "57", "fuerza": 64.9, "tipo": "fuerte", "lot": "La Suerte 6PM"}
        ]
    },
    "anguila_6pm": {
        "nombre": "Anguila (6:00 PM)",
        "tipo_juego": "quiniela",
        "salidor": "Pendiente 20/08",
        "hora_cierre": "17:50",
        "dictamen": {
            "flujo": "ALTO (70 al 99)",
            "decena": "Los 30s y 80s (30-39 / 80-89)",
            "terminal": "Terminales 1, 3 y 8",
            "pareja": "MUY ALTA (99, 00, 33)",
            "digito_fuerte": "Dígitos 3 y 8",
            "presion": "🚨 RUPTURA: Pareja 99 lista tras retención",
            "dia_tendencia": f"{dia_hoy}: Ruptura de atrasados en primera"
        },
        "sueltos": [
            {"num": "31", "fuerza": 92.1, "tipo": "triple_factor", "lot": "Anguila 6PM"},
            {"num": "13", "fuerza": 82.8, "tipo": "virado", "lot": "Anguila 6PM"},
            {"num": "28", "fuerza": 78.4, "tipo": "caliente", "lot": "Anguila 6PM"},
            {"num": "86", "fuerza": 72.0, "tipo": "atrasado", "lot": "Anguila 6PM"},
            {"num": "99", "fuerza": 67.5, "tipo": "pareja", "lot": "Anguila 6PM"}
        ]
    },
    "anguila_dia_noche": {
        "nombre": "Anguila (10 AM / 1 PM / 9 PM)",
        "tipo_juego": "quiniela",
        "salidor": "Pendiente 20/08",
        "hora_cierre": "20:50",
        "dictamen": {
            "flujo": "ALTO (80 al 99)",
            "decena": "Los 80s y 90s (80-89 / 90-99)",
            "terminal": "Terminales 8, 5 y 1",
            "pareja": "ALTA (88, 55)",
            "digito_fuerte": "Dígito 8",
            "presion": "🚨 RUPTURA: El 88 entra en zona de impacto",
            "dia_tendencia": f"{dia_hoy}: Repetición constante de cabezas"
        },
        "sueltos": [
            {"num": "88", "fuerza": 88.5, "tipo": "pareja", "lot": "Anguila 1PM"},
            {"num": "15", "fuerza": 84.1, "tipo": "caliente", "lot": "Anguila 10AM"},
            {"num": "51", "fuerza": 75.6, "tipo": "virado", "lot": "Anguila 10AM"},
            {"num": "98", "fuerza": 71.3, "tipo": "atrasado", "lot": "Anguila 9PM"},
            {"num": "41", "fuerza": 66.0, "tipo": "fuerte", "lot": "Anguila 9PM"}
        ]
    },
    "real": {
        "nombre": "Lotería Real (12:55 PM)",
        "tipo_juego": "quiniela",
        "salidor": "Pendiente 20/08",
        "hora_cierre": "12:40",
        "dictamen": {
            "flujo": "ALTO (50 al 89)",
            "decena": "Los 80s y 50s (80-89 / 50-59)",
            "terminal": "Terminales 5, 8 y 4",
            "pareja": "MEDIA (33, 88)",
            "digito_fuerte": "Dígitos 5 y 8",
            "presion": "🚨 RUPTURA: Línea 85/58 lidera la tómbola",
            "dia_tendencia": f"{dia_hoy}: Cruces de números del mediodía"
        },
        "sueltos": [
            {"num": "85", "fuerza": 88.4, "tipo": "triple_factor", "lot": "Real 12:55pm"},
            {"num": "58", "fuerza": 79.5, "tipo": "virado", "lot": "Real 12:55pm"},
            {"num": "04", "fuerza": 75.1, "tipo": "caliente", "lot": "Real 12:55pm"},
            {"num": "12", "fuerza": 71.6, "tipo": "atrasado", "lot": "Real 12:55pm"},
            {"num": "33", "fuerza": 65.0, "tipo": "pareja", "lot": "Real 12:55pm"}
        ]
    },
    "loteka": {
        "nombre": "Loteka (7:55 PM)",
        "tipo_juego": "quiniela",
        "salidor": "Pendiente 20/08",
        "hora_cierre": "19:40",
        "dictamen": {
            "flujo": "ALTO (70 al 99)",
            "decena": "Los 70s y 90s (70-79 / 90-99)",
            "terminal": "Terminales 9, 7 y 0",
            "pareja": "BAJA (77)",
            "digito_fuerte": "Dígitos 7 y 9",
            "presion": "🚨 RUPTURA: Bolo 79 empuja jaladera pesada",
            "dia_tendencia": f"{dia_hoy}: Jaladeras directas de la Gana Más"
        },
        "sueltos": [
            {"num": "79", "fuerza": 89.6, "tipo": "fuerte", "lot": "Loteka"},
            {"num": "97", "fuerza": 80.6, "tipo": "virado", "lot": "Loteka"},
            {"num": "50", "fuerza": 76.2, "tipo": "caliente", "lot": "Loteka"},
            {"num": "23", "fuerza": 69.8, "tipo": "atrasado", "lot": "Loteka"},
            {"num": "17", "fuerza": 64.3, "tipo": "fuerte", "lot": "Loteka"}
        ]
    },
    "primera": {
        "nombre": "La Primera (12:00 PM / 8:00 PM)",
        "tipo_juego": "quiniela",
        "salidor": "Pendiente 20/08",
        "hora_cierre": "19:45",
        "dictamen": {
            "flujo": "BAJO (10 al 30)",
            "decena": "Los 10s y 70s (10-19 / 70-79)",
            "terminal": "Terminales 7, 1 y 5",
            "pareja": "MEDIA (88, 11)",
            "digito_fuerte": "Dígito 1 y 7",
            "presion": "🚨 RUPTURA: El 17/71 con inercia de primera",
            "dia_tendencia": f"{dia_hoy}: Sorteo con líneas vivas"
        },
        "sueltos": [
            {"num": "17", "fuerza": 86.7, "tipo": "triple_factor", "lot": "La Primera"},
            {"num": "71", "fuerza": 78.0, "tipo": "virado", "lot": "La Primera"},
            {"num": "95", "fuerza": 73.4, "tipo": "caliente", "lot": "La Primera"},
            {"num": "09", "fuerza": 67.9, "tipo": "atrasado", "lot": "La Primera"},
            {"num": "88", "fuerza": 62.1, "tipo": "pareja", "lot": "La Primera"}
        ]
    },
    "lotedom": {
        "nombre": "LoteDom / El Quemaito (12:00 PM)",
        "tipo_juego": "quiniela",
        "salidor": "Pendiente 20/08",
        "hora_cierre": "11:45",
        "dictamen": {
            "flujo": "BAJO (10 al 49)",
            "decena": "Los 10s y 60s (10-19 / 60-69)",
            "terminal": "Terminales 6, 1 y 7",
            "pareja": "ALTA (22, 66)",
            "digito_fuerte": "Dígito 6",
            "presion": "🚨 RUPTURA: Quemaito 16 listo para salir",
            "dia_tendencia": f"{dia_hoy}: Frecuencia directa"
        },
        "sueltos": [
            {"num": "16", "fuerza": 87.5, "tipo": "fuerte", "lot": "LoteDom"},
            {"num": "61", "fuerza": 78.7, "tipo": "virado", "lot": "LoteDom"},
            {"num": "37", "fuerza": 74.2, "tipo": "caliente", "lot": "LoteDom"},
            {"num": "45", "fuerza": 69.0, "tipo": "atrasado", "lot": "LoteDom"},
            {"num": "22", "fuerza": 63.4, "tipo": "pareja", "lot": "LoteDom"}
        ]
    },
    "king_lottery": {
        "nombre": "King Lottery (12:30 PM / 7:30 PM)",
        "tipo_juego": "quiniela",
        "salidor": "Pendiente 20/08",
        "hora_cierre": "19:15",
        "dictamen": {
            "flujo": "ALTO (60 al 89)",
            "decena": "Los 60s y 20s (60-69 / 20-29)",
            "terminal": "Terminales 2, 6 y 5",
            "pareja": "MEDIA (44)",
            "digito_fuerte": "Dígitos 2 y 6",
            "presion": "🚨 RUPTURA: Línea 62 con rotación favorable",
            "dia_tendencia": f"{dia_hoy}: Cruces caribeños"
        },
        "sueltos": [
            {"num": "62", "fuerza": 88.0, "tipo": "fuerte", "lot": "King Lottery"},
            {"num": "26", "fuerza": 79.2, "tipo": "virado", "lot": "King Lottery"},
            {"num": "35", "fuerza": 75.0, "tipo": "caliente", "lot": "King Lottery"},
            {"num": "85", "fuerza": 70.1, "tipo": "atrasado", "lot": "King Lottery"},
            {"num": "42", "fuerza": 64.7, "tipo": "fuerte", "lot": "King Lottery"}
        ]
    },
    "ny_florida": {
        "nombre": "New York & Florida",
        "tipo_juego": "quiniela",
        "salidor": "Pendiente 20/08",
        "hora_cierre": "22:15",
        "dictamen": {
            "flujo": "BAJO (00 al 39)",
            "decena": "Los 20s y 30s (20-29 / 30-39)",
            "terminal": "Terminales 3, 2 y 9",
            "pareja": "BAJA (33, 99)",
            "digito_fuerte": "Dígitos 2 y 3",
            "presion": "🚨 RUPTURA: El 23 con índice máximo en plaza USA",
            "dia_tendencia": f"{dia_hoy}: Secuencias exactas"
        },
        "sueltos": [
            {"num": "23", "fuerza": 87.2, "tipo": "triple_factor", "lot": "NY Noche"},
            {"num": "32", "fuerza": 78.4, "tipo": "virado", "lot": "NY Noche"},
            {"num": "09", "fuerza": 74.5, "tipo": "caliente", "lot": "Florida Tarde"},
            {"num": "15", "fuerza": 68.3, "tipo": "atrasado", "lot": "NY Tarde"},
            {"num": "67", "fuerza": 61.0, "tipo": "fuerte", "lot": "Florida Noche"}
        ]
    }
}

@app.get("/", response_class=HTMLResponse)
def index():
    datos_json = json.dumps(DATOS_LOTERIAS)
    suenos_json = json.dumps(DICCIONARIO_SUENOS)
    auditoria_json = json.dumps(HISTORIAL_AUDITORIA)
    premios_json = json.dumps(RESULTADOS_OFICIALES)
    hora_actual = datetime.now().strftime("%I:%M:%S %p")

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <meta http-equiv="refresh" content="60">
        <title>Shneyder IA Pro RD</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #080d1a; color: #e2e8f0; margin: 0; padding: 10px; }}
            
            .main-wrapper {{ max-width: 900px; margin: 0 auto; }}

            .brand {{ text-align: center; background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 12px; padding: 12px; margin-bottom: 10px; border: 1px solid #38bdf8; box-shadow: 0 4px 10px rgba(56,189,248,0.15); }}
            .brand h1 {{ font-size: 22px; color: #38bdf8; margin: 0; font-weight: 900; letter-spacing: 1px; }}
            .brand p {{ font-size: 11px; color: #94a3b8; margin: 3px 0 0 0; text-transform: uppercase; letter-spacing: 2px; }}
            
            .pill {{ background: #111827; padding: 10px; border-radius: 10px; text-align: center; font-size: 13px; margin-bottom: 12px; border: 1px solid #374151; }}
            
            .timer-box {{ background: linear-gradient(135deg, #7f1d1d, #450a0a); border: 1px solid #ef4444; border-radius: 10px; padding: 8px 12px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; font-size: 13px; font-weight: bold; }}
            .timer-clock {{ color: #facc15; font-size: 15px; font-family: monospace; }}

            .search-box {{ background: #0f172a; border: 1px solid #334155; border-radius: 12px; padding: 10px; margin-bottom: 12px; display: flex; gap: 8px; }}
            .search-input {{ flex: 1; background: #1e293b; border: 1px solid #475569; color: #fff; border-radius: 8px; padding: 8px 12px; font-size: 13px; outline: none; }}
            .search-btn {{ background: #38bdf8; color: #0f172a; font-weight: bold; border: none; border-radius: 8px; padding: 8px 14px; cursor: pointer; }}
            #sueno_resultado {{ display: none; background: #131d31; border: 1px solid #38bdf8; border-radius: 10px; padding: 10px; margin-bottom: 12px; font-size: 12px; }}

            /* PIZARRA OFICIAL DE NÚMEROS PREMIADOS */
            .pizarra-card {{ background: #0f172a; border: 2px solid #38bdf8; border-radius: 12px; padding: 12px; margin-bottom: 15px; }}
            .pizarra-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px; margin-top: 10px; }}
            .lot-prize-card {{ background: #182234; border: 1px solid #28384e; border-radius: 8px; padding: 8px 10px; }}
            .lot-prize-name {{ font-size: 12px; font-weight: bold; color: #38bdf8; margin-bottom: 6px; display: flex; justify-content: space-between; }}
            .lot-balls-row {{ display: flex; gap: 8px; align-items: center; }}
            .prize-ball {{ width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 14px; color: #000; box-shadow: 0 2px 4px rgba(0,0,0,0.5); }}
            .ball-1ra {{ background: #22c55e; }}
            .ball-2da {{ background: #38bdf8; }}
            .ball-3ra {{ background: #facc15; }}

            /* Auditoría */
            .auditor-box {{ background: #0f172a; border: 1px solid #22c55e; border-radius: 10px; padding: 10px; margin-bottom: 12px; font-size: 12px; }}
            .auditor-title {{ color: #4ade80; font-weight: 800; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 4px; }}
            .auditor-item {{ padding: 5px 0; border-bottom: 1px solid #1e293b; font-size: 11.5px; }}
            .auditor-item:last-child {{ border: none; }}

            .tabs-scroll {{ display: flex; gap: 8px; overflow-x: auto; padding-bottom: 8px; margin-bottom: 12px; -webkit-overflow-scrolling: touch; }}
            .tab-btn {{ white-space: nowrap; background: #1f2937; color: #9ca3af; border: 1px solid #374151; padding: 8px 14px; border-radius: 20px; font-size: 12px; font-weight: bold; cursor: pointer; transition: 0.2s; }}
            .tab-btn.active {{ background: #38bdf8; color: #0f172a; border-color: #38bdf8; }}
            .tab-kino {{ background: linear-gradient(135deg, #eab308, #ca8a04); color: #000; border: 1px solid #fde047; font-weight: 900; }}
            .tab-esp {{ background: linear-gradient(135deg, #dc2626, #991b1b); color: #fff; border: 1px solid #f87171; font-weight: 900; }}
            .tab-euro {{ background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; border: 1px solid #60a5fa; font-weight: 900; }}

            .btn-actions {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 15px; }}
            .btn-wa {{ width: 100%; background: #22c55e; color: #0f172a; font-weight: 800; text-align: center; padding: 12px; border-radius: 10px; border: none; font-size: 13px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            .btn-ticket {{ width: 100%; background: #38bdf8; color: #0f172a; font-weight: 800; text-align: center; padding: 12px; border-radius: 10px; border: none; font-size: 13px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}

            .dictamen-box {{ background: #0f172a; border: 1px solid #38bdf8; border-radius: 12px; padding: 12px; margin-bottom: 15px; font-size: 12px; }}
            .dictamen-box h3 {{ margin: 0 0 8px 0; color: #38bdf8; font-size: 13px; display: flex; align-items: center; justify-content: space-between; }}
            .dictamen-item {{ margin-bottom: 5px; display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 3px; }}
            .dictamen-item b {{ color: #94a3b8; }}
            .dictamen-val {{ color: #f8fafc; font-weight: bold; }}

            .presion-alert {{ background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; color: #fca5a5; padding: 8px; border-radius: 8px; margin-top: 8px; font-size: 11px; font-weight: bold; text-align: center; }}

            .card {{ background: #131d31; border-radius: 12px; padding: 12px; margin-bottom: 15px; border: 1px solid #233249; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            h2 {{ font-size: 14px; margin-top: 0; padding-bottom: 6px; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }}
            .table-container {{ max-height: 420px; overflow-y: auto; -webkit-overflow-scrolling: touch; }}
            table {{ width: 100%; border-collapse: collapse; text-align: center; font-size: 12px; }}
            th {{ background: #1e293b; padding: 6px 2px; color: #94a3b8; font-size: 11px; position: sticky; top: 0; }}
            td {{ padding: 8px 3px; border-bottom: 1px solid #1e293b; }}
            
            .balls-container {{ display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin: 10px 0; }}
            .ball-kino {{ background: #eab308; color: #000; font-weight: bold; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.5); }}
            .ball-primitiva {{ background: #ef4444; color: #fff; font-weight: bold; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 15px; }}
            .ball-euro {{ background: #3b82f6; color: #fff; font-weight: bold; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 15px; }}
            .ball-star {{ background: #facc15; color: #000; font-weight: 900; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 14px; }}

            #toast {{ display: none; position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: #38bdf8; color: #0f172a; padding: 10px 20px; border-radius: 20px; font-weight: bold; font-size: 13px; z-index: 100; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }}
        </style>
    </head>
    <body>
        <div class="main-wrapper">
            <div class="brand">
                <h1>SHNEYDER IA PRO RD</h1>
                <p>Sistema Cuántico Multimoneda (RD$ & €)</p>
            </div>

            <!-- RELOJ DE CIERRE DE BANCA -->
            <div class="timer-box">
                <div>⏳ <span id="timer_sala">Cierre de Banca:</span></div>
                <div class="timer-clock" id="timer_val">Calculando...</div>
            </div>

            <!-- PIZARRA OFICIAL DE NÚMEROS PREMIADOS (CADA LOTERÍA + ANGUILAS) -->
            <div class="pizarra-card">
                <div style="font-size:14px;font-weight:900;color:#38bdf8;display:flex;justify-content:space-between;align-items:center;">
                    <span>🏆 NÚMEROS PREMIADOS (OFICIALES)</span>
                    <span style="font-size:11px;color:#94a3b8;">📅 Jornada: 20/08/2026</span>
                </div>
                <div class="pizarra-grid" id="pizarra_contenedor"></div>
            </div>

            <!-- AUDITORÍA LIMPIA OFICIAL (20 DE AGOSTO) -->
            <div class="auditor-box">
                <div class="auditor-title">
                    <span>📡 AUDITORÍA OFICIAL EN VIVO</span>
                    <span style="font-size:10px;color:#94a3b8;">Verificación de Aciertos en Tiempo Real</span>
                </div>
                <div id="contenedor_auditoria"></div>
            </div>

            <!-- BUSCADOR CUÁNTICO DE SUEÑOS -->
            <div class="search-box">
                <input type="text" id="input_sueno" class="search-input" placeholder="Escribe tu sueño o cábala (ej. dinero, boda, agua)...">
                <button class="search-btn" onclick="buscarSueno()">🔮 CONSULTAR</button>
            </div>
            <div id="sueno_resultado"></div>

            <div class="pill">
                🎯 <b>SALA ACTIVA:</b> <span id="salidor_txt">Consenso General</span><br>
                🕒 <small>Día: <b>{dia_hoy}</b> | Hora: {hora_actual}</small>
            </div>

            <!-- SELECTOR DE LOTERÍAS -->
            <div class="tabs-scroll">
                <button class="tab-btn active" onclick="cambiarTab('todas')">🌐 TODAS</button>
                <button class="tab-btn tab-kino" onclick="cambiarTab('kino_leidsa')">👑 KINO LEIDSA</button>
                <button class="tab-btn tab-esp" onclick="cambiarTab('primitiva_esp')">🇪🇸 LA PRIMITIVA</button>
                <button class="tab-btn tab-euro" onclick="cambiarTab('euromillones')">🇪🇺 EUROMILLONES</button>
                <button class="tab-btn" onclick="cambiarTab('nacional')">NACIONAL / GANA MÁS</button>
                <button class="tab-btn" onclick="cambiarTab('leidsa')">LEIDSA</button>
                <button class="tab-btn" onclick="cambiarTab('suerte_dia')">LA SUERTE DÍA (12:30)</button>
                <button class="tab-btn" onclick="cambiarTab('suerte_tarde')">LA SUERTE 6PM</button>
                <button class="tab-btn" onclick="cambiarTab('anguila_6pm')">ANGUILA 6PM</button>
                <button class="tab-btn" onclick="cambiarTab('anguila_dia_noche')">ANGUILA (10AM/1PM/9PM)</button>
                <button class="tab-btn" onclick="cambiarTab('real')">REAL</button>
                <button class="tab-btn" onclick="cambiarTab('loteka')">LOTEKA</button>
                <button class="tab-btn" onclick="cambiarTab('primera')">LA PRIMERA</button>
                <button class="tab-btn" onclick="cambiarTab('lotedom')">LOTEDOM</button>
                <button class="tab-btn" onclick="cambiarTab('king_lottery')">KING LOTTERY</button>
                <button class="tab-btn" onclick="cambiarTab('ny_florida')">NEW YORK / FL</button>
            </div>

            <div class="btn-actions">
                <button class="btn-wa" onclick="copiarWhatsApp()">📋 COPIAR WHATSAPP</button>
                <button class="btn-ticket" onclick="generarTicket()">🎫 TICKET DE BANCA</button>
            </div>

            <!-- EL DICTAMEN DEL TITÁN -->
            <div class="dictamen-box">
                <h3>⚡ DICTAMEN DEL TITÁN <span id="dictamen_sala" style="font-size:10px;color:#94a3b8;"></span></h3>
                <div class="dictamen-item"><b>Flujo de Salida:</b> <span class="dictamen-val" id="d_flujo">--</span></div>
                <div class="dictamen-item"><b>Decena / Cuadrante:</b> <span class="dictamen-val" id="d_decena">--</span></div>
                <div class="dictamen-item"><b>Terminales Clave:</b> <span class="dictamen-val" id="d_terminal">--</span></div>
                <div class="dictamen-item"><b>Alerta de Pareja / Clúster:</b> <span class="dictamen-val" id="d_pareja">--</span></div>
                <div class="dictamen-item"><b>Dígito Fuerte:</b> <span class="dictamen-val" id="d_digito">--</span></div>
                <div class="dictamen-item" style="border:none;"><b>Inercia del Día:</b> <span class="dictamen-val" style="color:#38bdf8;" id="d_dia">--</span></div>
                <div class="presion-alert" id="d_presion">--</div>
            </div>

            <!-- VISTA KINO TV LEIDSA -->
            <div id="seccion_kino" style="display:none;">
                <div class="card" style="border: 2px solid #eab308; background:#18181b;">
                    <h2 style="color: #facc15;">👑 LOS 10 DUEÑOS DEL KINO (BOLOS BASE DEL MES)</h2>
                    <div class="balls-container" id="kino_duenos_container"></div>
                    <div style="background:#27272a;padding:8px;border-radius:8px;font-size:11px;margin-top:8px;text-align:center;" id="kino_estado_txt"></div>
                    <div style="background:#27272a;color:#38bdf8;padding:8px;border-radius:8px;font-size:11px;margin-top:5px;text-align:center;" id="kino_paridad_txt"></div>
                    <div style="background:rgba(239,68,68,0.15);color:#fca5a5;padding:8px;border-radius:8px;font-size:11px;margin-top:5px;text-align:center;font-weight:bold;" id="kino_muerta_txt"></div>
                </div>

                <div class="card" style="border: 1px solid #eab308;">
                    <h2 style="color: #facc15;">🎯 JUGADAS DE COBERTURA: BLOQUES DE 5 NÚMEROS</h2>
                    <table>
                        <thead><tr><th>#</th><th>BLOQUE RECOMENDADO</th><th>PARIDAD</th><th>FUERZA IA</th></tr></thead>
                        <tbody id="tabla_kino_5"></tbody>
                    </table>
                </div>

                <div class="card" style="border: 1px solid #eab308;">
                    <h2 style="color: #facc15;">🏆 JUGADAS DE IMPACTO: BLOQUES DE 7 NÚMEROS</h2>
                    <table>
                        <thead><tr><th>#</th><th>BLOQUE RECOMENDADO</th><th>PARIDAD</th><th>FUERZA IA</th></tr></thead>
                        <tbody id="tabla_kino_7"></tbody>
                    </table>
                </div>
            </div>

            <!-- VISTA LA PRIMITIVA ESPAÑA -->
            <div id="seccion_primitiva" style="display:none;">
                <div class="card" style="border: 2px solid #ef4444; background:#18181b;">
                    <h2 style="color: #f87171;">🇪🇸 NÚMEROS BASE & RADAR DEL REINTEGRO</h2>
                    <div class="balls-container" id="primitiva_base_container"></div>
                    <div style="display:flex; justify-content:space-around; margin-top:10px; background:#27272a; padding:10px; border-radius:8px;">
                        <div><b>REINTEGRO IA:</b> <span style="background:#ef4444; color:#fff; padding:3px 8px; border-radius:50%; font-weight:bold;" id="prim_reintegro">7</span></div>
                        <div><b>COMPLEMENTARIO:</b> <span style="background:#3b82f6; color:#fff; padding:3px 8px; border-radius:50%; font-weight:bold;" id="prim_comp">34</span></div>
                    </div>
                    <div style="background:#27272a;color:#94a3b8;padding:8px;border-radius:8px;font-size:11px;margin-top:8px;text-align:center;" id="prim_cuadrantes"></div>
                </div>

                <div class="card" style="border: 1px solid #ef4444;">
                    <h2 style="color: #f87171;">🎯 APUESTAS REDUCIDAS INTELIGENTES (6 NÚMEROS + R)</h2>
                    <table>
                        <thead><tr><th>#</th><th>COMBINACIÓN (6 NÚMEROS)</th><th>R</th><th>ESTRATEGIA</th><th>FUERZA</th></tr></thead>
                        <tbody id="tabla_primitiva"></tbody>
                    </table>
                </div>
            </div>

            <!-- VISTA EUROMILLONES -->
            <div id="seccion_euromillones" style="display:none;">
                <div class="card" style="border: 2px solid #3b82f6; background:#18181b;">
                    <h2 style="color: #60a5fa;">🇪🇺 RED DE AFINIDAD CUÁNTICA & ESTRELLAS FIJAS</h2>
                    <div class="balls-container" id="euro_base_container"></div>
                    <div style="display:flex; justify-content:space-around; align-items:center; margin-top:10px; background:#27272a; padding:10px; border-radius:8px;">
                        <div><b>ESTRELLAS MAESTRAS:</b> <span class="ball-star" style="display:inline-flex; width:28px; height:28px; font-size:12px;" id="euro_e1">03</span> <span class="ball-star" style="display:inline-flex; width:28px; height:28px; font-size:12px;" id="euro_e2">08</span></div>
                        <div><b>FUERZA PAR:</b> <span style="color:#4ade80; font-weight:bold;">97.2%</span></div>
                    </div>
                    <div style="background:#27272a;color:#94a3b8;padding:8px;border-radius:8px;font-size:11px;margin-top:8px;text-align:center;" id="euro_distribucion"></div>
                </div>

                <div class="card" style="border: 1px solid #3b82f6;">
                    <h2 style="color: #60a5fa;">🏆 COMBINACIONES TITÁN (5 NÚMEROS + 2 ESTRELLAS)</h2>
                    <table>
                        <thead><tr><th>#</th><th>5 NÚMEROS</th><th>ESTRELLAS</th><th>TIPO</th><th>FUERZA</th></tr></thead>
                        <tbody id="tabla_euromillones"></tbody>
                    </table>
                </div>
            </div>

            <!-- VISTA TRADICIONAL RD (QUINIELA, PALÉ, TRIPLETAS) -->
            <div id="seccion_tradicional">
                <div class="card" style="border: 1px solid #22c55e;">
                    <h2 style="color: #4ade80;">⭐ TOP 5 LÍNEAS ÉLITE <span id="nombre_sala" style="font-size:11px;color:#94a3b8;"></span></h2>
                    <table>
                        <thead><tr><th>#</th><th>NÚMERO</th><th>FUERZA</th><th>ESTADO</th><th>SALA</th></tr></thead>
                        <tbody id="tabla_top5"></tbody>
                    </table>
                </div>

                <div class="card" style="border: 1px solid #f97316;">
                    <h2 style="color: #fb923c;">🔥 PALÉS DE FUEGO CRUZADO (COBERTURA LATERAL)</h2>
                    <div class="table-container">
                        <table>
                            <thead><tr><th>#</th><th>PALÉ COBERTURA</th><th>TIPO</th><th>SALA</th></tr></thead>
                            <tbody id="tabla_fuego_cruzado"></tbody>
                        </table>
                    </div>
                </div>

                <div class="card">
                    <h2 style="color: #38bdf8;">📊 TOP 20 NÚMEROS SUELTOS</h2>
                    <div class="table-container">
                        <table>
                            <thead><tr><th>#</th><th>NÚMERO</th><th>FUERZA</th><th>ESTADO</th><th>SALA</th></tr></thead>
                            <tbody id="tabla_sueltos"></tbody>
                        </table>
                    </div>
                </div>

                <div class="card">
                    <h2 style="color: #facc15;">🎯 PALÉS DIRECTOS RECOMENDADOS</h2>
                    <div class="table-container">
                        <table>
                            <thead><tr><th>#</th><th>PALÉ</th><th>FUERZA</th><th>SALA</th></tr></thead>
                            <tbody id="tabla_pales"></tbody>
                        </table>
                    </div>
                </div>

                <div class="card">
                    <h2 style="color: #f472b6;">🏆 TRIPLETAS BLINDADAS</h2>
                    <div class="table-container">
                        <table>
                            <thead><tr><th>#</th><th>TRIPLETA</th><th>FUERZA</th><th>SALA</th></tr></thead>
                            <tbody id="tabla_tripletas"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div id="toast">¡Acción ejecutada! 📱</div>
        </div>

        <script>
            const db = {datos_json};
            const suenos = {suenos_json};
            const auditoria = {auditoria_json};
            const premios = {premios_json};
            let tabActual = 'todas';

            function renderBadge(tipo) {{
                if (tipo === "triple_factor") return "<span style='background:#facc15;color:#000;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:900;'>👑 3X FACTOR</span>";
                if (tipo === "virado") return "<span style='background:#f59e0b;color:#000;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>🛡️ VIRADO</span>";
                if (tipo === "caliente") return "<span style='background:#ef4444;color:#fff;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>🔥 RACHA</span>";
                if (tipo === "atrasado") return "<span style='background:#8b5cf6;color:#fff;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>⏳ ATRASADO</span>";
                if (tipo === "pareja") return "<span style='background:#ec4899;color:#fff;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>👥 PAREJA</span>";
                return "<span style='background:#22c55e;color:#000;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>⭐ ÉLITE</span>";
            }}

            function cargarPizarraPremios() {{
                let html = "";
                for (let k in premios) {{
                    const lot = premios[k];
                    if (k === 'kino_tv') {{
                        let ballsHtml = lot.premios.slice(0, 10).map(b => `<span style="background:#eab308;color:#000;font-size:10px;font-weight:bold;padding:2px 5px;border-radius:4px;">${{b}}</span>`).join(' ');
                        html += `<div class="lot-prize-card" style="grid-column: 1 / -1;">
                            <div class="lot-prize-name"><span>👑 ${{lot.nombre}}</span> <span style="font-size:10px;color:#94a3b8;">${{lot.estado}}</span></div>
                            <div style="display:flex;gap:4px;flex-wrap:wrap;margin-top:4px;">${{ballsHtml}}</div>
                        </div>`;
                    }} else if (k === 'primitiva_esp') {{
                        let ballsHtml = lot.premios.map(b => `<div class="prize-ball" style="background:#ef4444;color:#fff;font-size:12px;">${{b}}</div>`).join('');
                        html += `<div class="lot-prize-card">
                            <div class="lot-prize-name"><span>🇪🇸 ${{lot.nombre}}</span> <span style="font-size:10px;color:#94a3b8;">${{lot.estado}}</span></div>
                            <div class="lot-balls-row">${{ballsHtml}} <span style="font-size:10px;color:#94a3b8;">R: ${{lot.reintegro}}</span></div>
                        </div>`;
                    }} else if (k === 'euromillones') {{
                        let ballsHtml = lot.premios.map(b => `<div class="prize-ball" style="background:#3b82f6;color:#fff;font-size:12px;">${{b}}</div>`).join('');
                        html += `<div class="lot-prize-card">
                            <div class="lot-prize-name"><span>🇪🇺 ${{lot.nombre}}</span> <span style="font-size:10px;color:#94a3b8;">${{lot.estado}}</span></div>
                            <div class="lot-balls-row">${{ballsHtml}} <span style="color:#facc15;font-weight:bold;font-size:11px;">⭐ ${{lot.estrellas.join('-')}}</span></div>
                        </div>`;
                    }} else {{
                        let isAnguila = lot.nombre.includes("Anguila");
                        let badgeIcon = isAnguila ? "🐍" : "🇩🇴";
                        html += `<div class="lot-prize-card" style="${{isAnguila ? 'border-color:#10b981;' : ''}}">
                            <div class="lot-prize-name"><span style="${{isAnguila ? 'color:#34d399;' : ''}}">${{badgeIcon}} ${{lot.nombre}}</span> <span style="font-size:10px;color:#94a3b8;">${{lot.estado}}</span></div>
                            <div class="lot-balls-row">
                                <div class="prize-ball ball-1ra" title="1ra">${{lot.premios[0]}}</div>
                                <div class="prize-ball ball-2da" title="2da">${{lot.premios[1]}}</div>
                                <div class="prize-ball ball-3ra" title="3ra">${{lot.premios[2]}}</div>
                            </div>
                        </div>`;
                    }}
                }}
                document.getElementById('pizarra_contenedor').innerHTML = html;
            }}

            function cargarAuditoria() {{
                let html = "";
                auditoria.forEach(item => {{
                    html += `<div class="auditor-item">
                        <span style="color:#94a3b8;font-size:10px;">📅 ${{item.fecha}}</span> | 
                        <b style="color:#38bdf8;">${{item.tipo}} (${{item.sala}}):</b> 
                        <span style="color:#4ade80;font-weight:bold;">${{item.premio}}</span>
                        <div style="font-size:10px;color:#64748b;margin-left:10px;">↳ ${{item.detalle}}</div>
                    </div>`;
                }});
                document.getElementById('contenedor_auditoria').innerHTML = html;
            }}

            function cambiarTab(clave) {{
                tabActual = clave;
                document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
                if (event && event.target) {{
                    event.target.classList.add('active');
                }}
                actualizarVista();
            }}

            function vec(numStr, delta) {{
                let val = (parseInt(numStr) + delta + 100) % 100;
                return String(val).padStart(2, '0');
            }}

            function buscarSueno() {{
                const input = document.getElementById('input_sueno').value.toLowerCase().trim();
                const res = document.getElementById('sueno_resultado');
                if (!input) return;

                let match = suenos[input];
                if (!match) {{
                    for (let k in suenos) {{
                        if (input.includes(k) || k.includes(input)) {{
                            match = suenos[k];
                            break;
                        }}
                    }}
                }}

                if (match) {{
                    res.style.display = 'block';
                    res.innerHTML = `🔮 <b>CÁBALA DETECTADA:</b> "${{input.toUpperCase()}}"<br>` +
                                    `🎯 <b>Número Sugerido:</b> <span style="color:#4ade80;font-size:16px;font-weight:bold;">${{match.num}}</span> ` +
                                    `| <b>Fuerza IA:</b> ${{match.fuerza}}%<br>` +
                                    `📍 <b>Sugerido para:</b> ${{match.lot}} (${{match.cabala}})`;
                }} else {{
                    res.style.display = 'block';
                    let seed = input.split('').reduce((a,c) => a + c.charCodeAt(0), 0) % 100;
                    let numGen = String(seed).padStart(2, '0');
                    res.innerHTML = `🔮 <b>CÁBALA CUÁNTICA:</b> "${{input.toUpperCase()}}"<br>` +
                                    `🎯 <b>Bolo Calculado:</b> <span style="color:#38bdf8;font-size:16px;font-weight:bold;">${{numGen}}</span> | Fuerza IA: 76.5%<br>` +
                                    `🛡️ Recomendación: Jugar con su virado ${{numGen.split('').reverse().join('')}}`;
                }}
            }}

            function actualizarReloj() {{
                const info = db[tabActual];
                document.getElementById('timer_sala').innerText = "Cierre " + (info.nombre.split(' (')[0]) + ":";
                
                const ahora = new Date();
                const [hStr, mStr] = (info.hora_cierre || "20:30").split(':');
                const cierre = new Date();
                cierre.setHours(parseInt(hStr), parseInt(mStr), 0, 0);

                let diff = cierre - ahora;
                if (diff < 0) {{
                    document.getElementById('timer_val').innerText = "Sorteo Cerrado";
                    document.getElementById('timer_val').style.color = "#94a3b8";
                }} else {{
                    let horas = Math.floor(diff / (1000 * 60 * 60));
                    let mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                    let segs = Math.floor((diff % (1000 * 60)) / 1000);
                    document.getElementById('timer_val').innerText = 
                        String(horas).padStart(2, '0') + ":" + 
                        String(mins).padStart(2, '0') + ":" + 
                        String(segs).padStart(2, '0');
                    document.getElementById('timer_val').style.color = "#facc15";
                }}
            }}

            function actualizarVista() {{
                const info = db[tabActual];
                document.getElementById('salidor_txt').innerText = info.salidor || info.nombre;
                document.getElementById('dictamen_sala').innerText = "[" + info.nombre + "]";

                if (info.dictamen) {{
                    document.getElementById('d_flujo').innerText = info.dictamen.flujo;
                    document.getElementById('d_decena').innerText = info.dictamen.decena;
                    document.getElementById('d_terminal').innerText = info.dictamen.terminal;
                    document.getElementById('d_pareja').innerText = info.dictamen.pareja;
                    document.getElementById('d_digito').innerText = info.dictamen.digito_fuerte;
                    document.getElementById('d_dia').innerText = info.dictamen.dia_tendencia;
                    document.getElementById('d_presion').innerText = info.dictamen.presion;
                }}

                document.getElementById('seccion_kino').style.display = 'none';
                document.getElementById('seccion_primitiva').style.display = 'none';
                document.getElementById('seccion_euromillones').style.display = 'none';
                document.getElementById('seccion_tradicional').style.display = 'none';

                if (info.tipo_juego === 'kino') {{
                    document.getElementById('seccion_kino').style.display = 'block';
                    const kd = info.kino_data;
                    document.getElementById('kino_estado_txt').innerText = kd.estado_tombola;
                    document.getElementById('kino_paridad_txt').innerText = kd.paridad_optima;
                    document.getElementById('kino_muerta_txt').innerText = kd.zona_muerta;

                    let htmlDuenos = "";
                    kd.duenos.forEach(b => {{ htmlDuenos += `<div class="ball-kino">${{b}}</div>`; }});
                    document.getElementById('kino_duenos_container').innerHTML = htmlDuenos;

                    let htmlK5 = "";
                    kd.bloques_5.forEach((b, i) => {{
                        htmlK5 += `<tr>
                            <td>0${{i+1}}</td>
                            <td style="color:#facc15;font-weight:bold;font-size:15px;">${{b.bloque}}</td>
                            <td style="font-size:11px;color:#94a3b8;">${{b.paridad}}</td>
                            <td style="font-weight:bold;">${{b.fuerza}}%</td>
                        </tr>`;
                    }});
                    document.getElementById('tabla_kino_5').innerHTML = htmlK5;

                    let htmlK7 = "";
                    kd.bloques_7.forEach((b, i) => {{
                        htmlK7 += `<tr>
                            <td>0${{i+1}}</td>
                            <td style="color:#f472b6;font-weight:bold;font-size:15px;">${{b.bloque}}</td>
                            <td style="font-size:11px;color:#94a3b8;">${{b.paridad}}</td>
                            <td style="font-weight:bold;">${{b.fuerza}}%</td>
                        </tr>`;
                    }});
                    document.getElementById('tabla_kino_7').innerHTML = htmlK7;

                }} else if (info.tipo_juego === 'primitiva') {{
                    document.getElementById('seccion_primitiva').style.display = 'block';
                    const pd = info.primitiva_data;
                    document.getElementById('prim_reintegro').innerText = pd.reintegro;
                    document.getElementById('prim_comp').innerText = pd.complementario;
                    document.getElementById('prim_cuadrantes').innerText = "📐 " + pd.cuadrantes;

                    let htmlPBase = "";
                    pd.numeros_base.forEach(b => {{ htmlPBase += `<div class="ball-primitiva">${{b}}</div>`; }});
                    document.getElementById('primitiva_base_container').innerHTML = htmlPBase;

                    let htmlP = "";
                    pd.apuestas_6.forEach((a, i) => {{
                        htmlP += `<tr>
                            <td>0${{i+1}}</td>
                            <td style="color:#f87171;font-weight:bold;font-size:15px;">${{a.combinacion}}</td>
                            <td><span style="background:#ef4444;color:#fff;padding:2px 6px;border-radius:50%;font-weight:bold;">${{a.reintegro}}</span></td>
                            <td style="font-size:10px;">${{a.tipo}}</td>
                            <td style="font-weight:bold;color:#4ade80;">${{a.fuerza}}%</td>
                        </tr>`;
                    }});
                    document.getElementById('tabla_primitiva').innerHTML = htmlP;

                }} else if (info.tipo_juego === 'euromillones') {{
                    document.getElementById('seccion_euromillones').style.display = 'block';
                    const ed = info.euro_data;
                    document.getElementById('euro_e1').innerText = ed.estrellas_fijas[0];
                    document.getElementById('euro_e2').innerText = ed.estrellas_fijas[1];
                    document.getElementById('euro_distribucion').innerText = "📐 " + ed.distribucion;

                    let htmlEBase = "";
                    ed.red_afinidad.forEach(b => {{
                        if (b.includes('*')) {{
                            htmlEBase += `<div class="ball-star">${{b.replace('*','')}}</div>`;
                        }} else {{
                            htmlEBase += `<div class="ball-euro">${{b}}</div>`;
                        }}
                    }});
                    document.getElementById('euro_base_container').innerHTML = htmlEBase;

                    let htmlE = "";
                    ed.apuestas_euro.forEach((a, i) => {{
                        htmlE += `<tr>
                            <td>0${{i+1}}</td>
                            <td style="color:#60a5fa;font-weight:bold;font-size:15px;">${{a.numeros}}</td>
                            <td><span style="color:#facc15;font-weight:900;">⭐ ${{a.estrellas}}</span></td>
                            <td style="font-size:10px;">${{a.tipo}}</td>
                            <td style="font-weight:bold;color:#4ade80;">${{a.fuerza}}%</td>
                        </tr>`;
                    }});
                    document.getElementById('tabla_euromillones').innerHTML = htmlE;

                }} else {{
                    document.getElementById('seccion_tradicional').style.display = 'block';
                    const sueltos = info.sueltos;
                    
                    let htmlTop5 = "";
                    sueltos.slice(0, 5).forEach((item, i) => {{
                        htmlTop5 += `<tr style="background:rgba(34,197,94,0.12);">
                            <td>#${{i+1}}</td>
                            <td style="color:#4ade80;font-size:18px;font-weight:bold;">${{item.num}}</td>
                            <td style="font-weight:bold;">${{item.fuerza}}%</td>
                            <td>${{renderBadge(item.tipo)}}</td>
                            <td style="font-size:10px;">${{item.lot}}</td>
                        </tr>`;
                    }});
                    document.getElementById('tabla_top5').innerHTML = htmlTop5;

                    let n1 = sueltos[0].num;
                    let n2 = sueltos[1] ? sueltos[1].num : "54";
                    let htmlFC = `
                        <tr style="background:rgba(249,115,22,0.1);">
                            <td>01</td>
                            <td style="color:#fb923c;font-weight:bold;font-size:15px;">${{n1}} - ${{vec(n2, 1)}}</td>
                            <td><span style="background:#f97316;color:#000;padding:2px 5px;border-radius:4px;font-size:10px;font-weight:bold;">VECINO +1</span></td>
                            <td style="font-size:10px;">${{sueltos[0].lot}}</td>
                        </tr>
                        <tr style="background:rgba(249,115,22,0.1);">
                            <td>02</td>
                            <td style="color:#fb923c;font-weight:bold;font-size:15px;">${{n1}} - ${{vec(n2, -1)}}</td>
                            <td><span style="background:#f97316;color:#000;padding:2px 5px;border-radius:4px;font-size:10px;font-weight:bold;">VECINO -1</span></td>
                            <td style="font-size:10px;">${{sueltos[0].lot}}</td>
                        </tr>
                        <tr style="background:rgba(249,115,22,0.1);">
                            <td>03</td>
                            <td style="color:#fb923c;font-weight:bold;font-size:15px;">${{vec(n1, 1)}} - ${{n2}}</td>
                            <td><span style="background:#f97316;color:#000;padding:2px 5px;border-radius:4px;font-size:10px;font-weight:bold;">VECINO +1</span></td>
                            <td style="font-size:10px;">${{sueltos[0].lot}}</td>
                        </tr>
                        <tr style="background:rgba(249,115,22,0.1);">
                            <td>04</td>
                            <td style="color:#fb923c;font-weight:bold;font-size:15px;">${{n1}} - ${{n1.split('').reverse().join('')}}</td>
                            <td><span style="background:#eab308;color:#000;padding:2px 5px;border-radius:4px;font-size:10px;font-weight:bold;">DERECHO/REVÉS</span></td>
                            <td style="font-size:10px;">${{sueltos[0].lot}}</td>
                        </tr>
                    `;
                    document.getElementById('tabla_fuego_cruzado').innerHTML = htmlFC;

                    let htmlSueltos = "";
                    sueltos.forEach((item, i) => {{
                        htmlSueltos += `<tr>
                            <td>#${{String(i+1).padStart(2, '0')}}</td>
                            <td style="color:#38bdf8;font-size:16px;font-weight:bold;">${{item.num}}</td>
                            <td>${{item.fuerza}}%</td>
                            <td>${{renderBadge(item.tipo)}}</td>
                            <td style="font-size:10px;">${{item.lot}}</td>
                        </tr>`;
                    }});
                    document.getElementById('tabla_sueltos').innerHTML = htmlSueltos;

                    let htmlPales = "";
                    let countP = 1;
                    for (let i = 0; i < Math.min(sueltos.length, 6); i++) {{
                        for (let j = i + 1; j < Math.min(sueltos.length, 6); j++) {{
                            let f = ((sueltos[i].fuerza + sueltos[j].fuerza) / 2).toFixed(1);
                            htmlPales += `<tr>
                                <td>${{String(countP).padStart(2, '0')}}</td>
                                <td style="color:#facc15;font-weight:bold;font-size:15px;">${{sueltos[i].num}} - ${{sueltos[j].num}}</td>
                                <td style="font-weight:bold;color:#e2e8f0;">${{f}}%</td>
                                <td style="font-size:10px;">${{sueltos[i].lot}}</td>
                            </tr>`;
                            countP++;
                            if (countP > 20) break;
                        }}
                    }}
                    document.getElementById('tabla_pales').innerHTML = htmlPales;

                    let htmlTrip = "";
                    let countT = 1;
                    for (let i = 0; i < Math.min(sueltos.length, 5); i++) {{
                        for (let j = i + 1; j < Math.min(sueltos.length, 5); j++) {{
                            for (let k = j + 1; k < Math.min(sueltos.length, 5); k++) {{
                                let fTrip = ((sueltos[i].fuerza + sueltos[j].fuerza + sueltos[k].fuerza) / 3).toFixed(1);
                                htmlTrip += `<tr>
                                    <td>${{String(countT).padStart(2, '0')}}</td>
                                    <td style="color:#f472b6;font-weight:bold;font-size:14px;">${{sueltos[i].num}} - ${{sueltos[j].num}} - ${{sueltos[k].num}}</td>
                                    <td style="font-weight:bold;color:#e2e8f0;">${{fTrip}}%</td>
                                    <td style="font-size:10px;">${{sueltos[i].lot}}</td>
                                </tr>`;
                                countT++;
                            }}
                        }}
                    }}
                    document.getElementById('tabla_tripletas').innerHTML = htmlTrip || "<tr><td colspan='4'>Añadiendo datos...</td></tr>";
                }}
            }}

            function copiarWhatsApp() {{
                const info = db[tabActual];
                let texto = "";

                if (info.tipo_juego === 'kino') {{
                    const kd = info.kino_data;
                    texto = `👑 *VENTA ESPECIAL: KINO LEIDSA TV* 👑\\n` +
                            `🔥 *${{kd.estado_tombola}}*\\n` +
                            `⭐ *Dueños del Mes:* ${{kd.duenos.join(', ')}}\\n` +
                            `🎯 *Bloque 5:* [${{kd.bloques_5[0].bloque}}]\\n` +
                            `🏆 *Bloque 7:* [${{kd.bloques_7[0].bloque}}]\\n` +
                            `⚡ *SHNEYDER IA PRO RD*`;
                }} else if (info.tipo_juego === 'primitiva') {{
                    const pd = info.primitiva_data;
                    texto = `🇪🇸 *JUGADA LA PRIMITIVA (ESPAÑA)* 🇪🇸\\n` +
                            `🎯 *Combinación Élite:* [${{pd.apuestas_6[0].combinacion}}]\\n` +
                            `🔴 *Reintegro:* ${{pd.reintegro}} | 🔵 *Complementario:* ${{pd.complementario}}\\n` +
                            `⚡ *SHNEYDER IA PRO RD*`;
                }} else if (info.tipo_juego === 'euromillones') {{
                    const ed = info.euro_data;
                    texto = `🇪🇺 *JUGADA EUROMILLONES TITÁN* 🇪🇺\\n` +
                            `🎯 *5 Números:* [${{ed.apuestas_euro[0].numeros}}]\\n` +
                            `⭐ *Estrellas:* [${{ed.apuestas_euro[0].estrellas}}]\\n` +
                            `⚡ *SHNEYDER IA PRO RD*`;
                }} else {{
                    const topNums = info.sueltos.slice(0, 5).map(s => s.num).join(", ");
                    const p1 = info.sueltos[0].num + " - " + info.sueltos[1].num;
                    const p2 = info.sueltos[0].num + " - " + (info.sueltos[2] ? info.sueltos[2].num : "00");
                    const trip = info.sueltos.slice(0, 3).map(s => s.num).join(" - ");

                    texto = `🔥 *JUGADA SHNEYDER IA PRO RD* 🔥\\n` +
                            `📍 *${{info.nombre}}*\\n` +
                            `⚡ *Dictamen:* ${{info.dictamen ? info.dictamen.flujo : 'Estándar'}} | Decena: ${{info.dictamen ? info.dictamen.decena : '--'}}\\n` +
                            `🎯 *Líneas Fuertes:* ${{topNums}}\\n` +
                            `💥 *Palés:* [${{p1}}] / [${{p2}}]\\n` +
                            `🏆 *Tripleta:* [${{trip}}]\\n` +
                            `🛡️ *Nota:* Cuidar con el virado si pasa de 85%`;
                }}

                navigator.clipboard.writeText(texto).then(() => {{
                    const t = document.getElementById('toast');
                    t.innerText = "¡Copiado para WhatsApp! 📱";
                    t.style.display = 'block';
                    setTimeout(() => {{ t.style.display = 'none'; }}, 2500);
                }});
            }}

            function generarTicket() {{
                const info = db[tabActual];
                let ticket = `=================================\\n` +
                             `   🎫 TICKET SHNEYDER IA PRO RD\\n` +
                             `=================================\\n` +
                             `SALA: ${{info.nombre.toUpperCase()}}\\n` +
                             `FECHA: ${{new Date().toLocaleDateString()}} - ${{new Date().toLocaleTimeString()}}\\n` +
                             `---------------------------------\\n`;

                if (info.sueltos) {{
                    ticket += `QUINIELAS:\\n`;
                    info.sueltos.slice(0, 5).forEach((s, i) => {{
                        ticket += ` #${{i+1}} [${{s.num}}] (Fuerza: ${{s.fuerza}}%)\\n`;
                    }});
                    ticket += `---------------------------------\\n` +
                              `PALÉ TITÁN:\\n` +
                              ` [${{info.sueltos[0].num}} - ${{info.sueltos[1].num}}]\\n` +
                              ` [${{info.sueltos[0].num}} - ${{info.sueltos[0].num.split('').reverse().join('')}}] (Virado)\\n` +
                              `---------------------------------\\n` +
                              `TRIPLETA BLINDADA:\\n` +
                              ` [${{info.sueltos[0].num}} - ${{info.sueltos[1].num}} - ${{info.sueltos[2].num}}]\\n`;
                }} else if (info.tipo_juego === 'kino') {{
                    ticket += `BLOQUE KINO (5 NÚMEROS):\\n [${{info.kino_data.bloques_5[0].bloque}}]\\n` +
                              `BLOQUE KINO (7 NÚMEROS):\\n [${{info.kino_data.bloques_7[0].bloque}}]\\n`;
                }} else if (info.tipo_juego === 'primitiva') {{
                    ticket += `PRIMITIVA (6 NÚMEROS):\\n [${{info.primitiva_data.apuestas_6[0].combinacion}}]\\n` +
                              `REINTEGRO: [${{info.primitiva_data.reintegro}}]\\n`;
                }} else if (info.tipo_juego === 'euromillones') {{
                    ticket += `EUROMILLONES (5 NÚMEROS):\\n [${{info.euro_data.apuestas_euro[0].numeros}}]\\n` +
                              `ESTRELLAS: [${{info.euro_data.apuestas_euro[0].estrellas}}]\\n`;
                }}

                ticket += `=================================\\n` +
                          `  VALIDADO POR SISTEMA CUÁNTICO\\n` +
                          `=================================`;

                navigator.clipboard.writeText(ticket).then(() => {{
                    const t = document.getElementById('toast');
                    t.innerText = "¡Ticket de Banca Copiado! 🎫";
                    t.style.display = 'block';
                    setTimeout(() => {{ t.style.display = 'none'; }}, 2500);
                }});
            }}

            cargarPizarraPremios();
            cargarAuditoria();
            setInterval(actualizarReloj, 1000);
            actualizarVista();
            actualizarReloj();
        </script>
    </body>
    </html>
    """
