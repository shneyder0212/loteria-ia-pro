import json
import sqlite3
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Shneyder IA Pro RD")
DB_PATH = "loteria_master_ai.db"

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
dia_hoy = DIAS_SEMANA[datetime.now().weekday()]

# Base de datos cuántica con Loterías Tradicionales + Venta Especial Kino Leidsa
DATOS_LOTERIAS = {
    "todas": {
        "nombre": "Todas las Loterías (Consenso General)",
        "salidor": "40 - 72 - 18",
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
            {"num": "04", "fuerza": 98.9, "tipo": "fuerte", "lot": "Gana Mas / Nacional"},
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
        "salidor": "Último Sorteo: 20 Bolos Registrados",
        "kino_data": {
            "estado_tombola": "🔥 TÓMBOLA CALIENTE: Consistencia 92.4% (Momento Óptimo)",
            "zona_muerta": "🚫 ZONA DE RETENCIÓN: 40 al 52 (No botar dinero en este rango)",
            "duenos": ["07", "14", "23", "38", "45", "59", "62", "71", "78", "80"],
            "bloques_5": [
                {"bloque": "07 - 23 - 45 - 62 - 78", "fuerza": 94.8},
                {"bloque": "14 - 38 - 59 - 71 - 80", "fuerza": 91.5},
                {"bloque": "07 - 14 - 23 - 38 - 71", "fuerza": 88.2}
            ],
            "bloques_7": [
                {"bloque": "07 - 14 - 23 - 45 - 59 - 71 - 78", "fuerza": 96.2},
                {"bloque": "14 - 23 - 38 - 62 - 71 - 78 - 80", "fuerza": 93.0}
            ]
        },
        "dictamen": {
            "flujo": "EXPANSIVO (1 al 80)",
            "decena": "Dominio de las decenas 20s, 60s y 70s",
            "terminal": "Terminales 7, 8, 3 y 4",
            "pareja": "ALTA (22, 44, 77)",
            "digito_fuerte": "Dígitos 7 y 8",
            "presion": "🎯 RECOMENDACIÓN: Jugar bloques cerrados de 5 y 7 números.",
            "dia_tendencia": f"{dia_hoy}: Alta concentración en números impares"
        },
        "sueltos": [
            {"num": "07", "fuerza": 96.5, "tipo": "fuerte", "lot": "Kino TV 8:55pm"},
            {"num": "78", "fuerza": 94.2, "tipo": "fuerte", "lot": "Kino TV 8:55pm"},
            {"num": "23", "fuerza": 91.0, "tipo": "caliente", "lot": "Kino TV 8:55pm"},
            {"num": "71", "fuerza": 88.7, "tipo": "caliente", "lot": "Kino TV 8:55pm"},
            {"num": "45", "fuerza": 85.3, "tipo": "atrasado", "lot": "Kino TV 8:55pm"}
        ]
    },
    "nacional": {
        "nombre": "Gana Más (2:30 PM) / Nacional Noche (8:50 PM)",
        "salidor": "40 - 72 - 18",
        "dictamen": {
            "flujo": "MIXTO (Foco en 00-49 y 70-79)",
            "decena": "Los 00s y 40s (01-09 / 40-49)",
            "terminal": "Terminales 4, 0 y 9",
            "pareja": "MEDIA (44, 00)",
            "digito_fuerte": "Dígito 0 y 4 (Obligado virar)",
            "presion": "🚨 RUPTURA: Bolo 04 acumulando máxima probabilidad de tómbola",
            "dia_tendencia": f"{dia_hoy}: Jaladera de números bajos a altos"
        },
        "sueltos": [
            {"num": "04", "fuerza": 98.9, "tipo": "fuerte", "lot": "Nacional Noche"},
            {"num": "40", "fuerza": 89.0, "tipo": "virado", "lot": "Nacional Noche"},
            {"num": "54", "fuerza": 81.3, "tipo": "caliente", "lot": "Gana Mas"},
            {"num": "79", "fuerza": 74.0, "tipo": "atrasado", "lot": "Nacional Noche"},
            {"num": "90", "fuerza": 69.5, "tipo": "fuerte", "lot": "Gana Mas"}
        ]
    },
    "leidsa": {
        "nombre": "Leidsa (8:55 PM)",
        "salidor": "29 - 92 - 15",
        "dictamen": {
            "flujo": "ALTO (Foco 60 al 99)",
            "decena": "Los 20s y 90s (20-29 / 90-99)",
            "terminal": "Terminales 2, 9 y 8",
            "pareja": "ALTA (22, 99)",
            "digito_fuerte": "Dígitos 2 y 9",
            "presion": "🚨 RUPTURA: Pareja 22 lista para desarmar el bloque nocturno",
            "dia_tendencia": f"{dia_hoy}: Sorteo de impacto nocturno con repetidores"
        },
        "sueltos": [
            {"num": "29", "fuerza": 91.2, "tipo": "fuerte", "lot": "Leidsa"},
            {"num": "92", "fuerza": 82.0, "tipo": "virado", "lot": "Leidsa"},
            {"num": "18", "fuerza": 77.5, "tipo": "caliente", "lot": "Leidsa"},
            {"num": "63", "fuerza": 70.8, "tipo": "atrasado", "lot": "Leidsa"},
            {"num": "45", "fuerza": 66.2, "tipo": "fuerte", "lot": "Leidsa"}
        ]
    },
    "suerte_dia": {
        "nombre": "La Suerte Dominicana (12:30 PM)",
        "salidor": "72 - 09 - 23",
        "dictamen": {
            "flujo": "BAJO A MEDIO (Foco 20 al 60)",
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
        "salidor": "10 - 98 - 24",
        "dictamen": {
            "flujo": "BAJO (00 al 49)",
            "decena": "Los 10s y 00s (10-19 / 01-09)",
            "terminal": "Terminales 0, 1 y 4",
            "pareja": "MEDIA (11, 00)",
            "digito_fuerte": "Dígito 0 y 1",
            "presion": "🚨 RUPTURA: Familia de base cero (01, 10) con carga extrema",
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
        "salidor": "00 - 61 - 27",
        "dictamen": {
            "flujo": "ALTO (Foco 70 al 99)",
            "decena": "Los 30s y 80s (30-39 / 80-89)",
            "terminal": "Terminales 1, 3 y 8",
            "pareja": "MUY ALTA (99, 00, 33)",
            "digito_fuerte": "Dígitos 3 y 8",
            "presion": "🚨 RUPTURA: Pareja 99 lista tras ciclo prolongado de retención",
            "dia_tendencia": f"{dia_hoy}: Ruptura de atrasados en primera"
        },
        "sueltos": [
            {"num": "31", "fuerza": 92.1, "tipo": "fuerte", "lot": "Anguila 6PM"},
            {"num": "13", "fuerza": 82.8, "tipo": "virado", "lot": "Anguila 6PM"},
            {"num": "28", "fuerza": 78.4, "tipo": "caliente", "lot": "Anguila 6PM"},
            {"num": "86", "fuerza": 72.0, "tipo": "atrasado", "lot": "Anguila 6PM"},
            {"num": "99", "fuerza": 67.5, "tipo": "pareja", "lot": "Anguila 6PM"}
        ]
    },
    "anguila_dia_noche": {
        "nombre": "Anguila (10 AM / 1 PM / 9 PM)",
        "salidor": "98 - 71 - 80",
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
        "salidor": "04 - 85 - 63",
        "dictamen": {
            "flujo": "ALTO (50 al 89)",
            "decena": "Los 80s y 50s (80-89 / 50-59)",
            "terminal": "Terminales 5, 8 y 4",
            "pareja": "MEDIA (33, 88)",
            "digito_fuerte": "Dígitos 5 y 8",
            "presion": "🚨 RUPTURA: Línea 85/58 lidera la tómbola del Cibao",
            "dia_tendencia": f"{dia_hoy}: Cruces de números calientes del mediodía"
        },
        "sueltos": [
            {"num": "85", "fuerza": 88.4, "tipo": "fuerte", "lot": "Real 12:55pm"},
            {"num": "58", "fuerza": 79.5, "tipo": "virado", "lot": "Real 12:55pm"},
            {"num": "04", "fuerza": 75.1, "tipo": "caliente", "lot": "Real 12:55pm"},
            {"num": "12", "fuerza": 71.6, "tipo": "atrasado", "lot": "Real 12:55pm"},
            {"num": "33", "fuerza": 65.0, "tipo": "pareja", "lot": "Real 12:55pm"}
        ]
    },
    "loteka": {
        "nombre": "Loteka (7:55 PM)",
        "salidor": "79 - 54 - 40",
        "dictamen": {
            "flujo": "ALTO (70 al 99)",
            "decena": "Los 70s y 90s (70-79 / 90-99)",
            "terminal": "Terminales 9, 7 y 0",
            "pareja": "BAJA (77)",
            "digito_fuerte": "Dígitos 7 y 9",
            "presion": "🚨 RUPTURA: Bolo 79 empuja jaladera pesada nocturna",
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
        "salidor": "17 - 50 - 95",
        "dictamen": {
            "flujo": "BAJO (10 al 30)",
            "decena": "Los 10s y 70s (10-19 / 70-79)",
            "terminal": "Terminales 7, 1 y 5",
            "pareja": "MEDIA (88, 11)",
            "digito_fuerte": "Dígito 1 y 7",
            "presion": "🚨 RUPTURA: El 17/71 con inercia de primera posición",
            "dia_tendencia": f"{dia_hoy}: Sorteo de apertura y cierre con líneas vivas"
        },
        "sueltos": [
            {"num": "17", "fuerza": 86.7, "tipo": "fuerte", "lot": "La Primera"},
            {"num": "71", "fuerza": 78.0, "tipo": "virado", "lot": "La Primera"},
            {"num": "95", "fuerza": 73.4, "tipo": "caliente", "lot": "La Primera"},
            {"num": "09", "fuerza": 67.9, "tipo": "atrasado", "lot": "La Primera"},
            {"num": "88", "fuerza": 62.1, "tipo": "pareja", "lot": "La Primera"}
        ]
    },
    "lotedom": {
        "nombre": "LoteDom / El Quemaito (12:00 PM)",
        "salidor": "16 - 37 - 45",
        "dictamen": {
            "flujo": "BAJO (10 al 49)",
            "decena": "Los 10s y 60s (10-19 / 60-69)",
            "terminal": "Terminales 6, 1 y 7",
            "pareja": "ALTA (22, 66)",
            "digito_fuerte": "Dígito 6",
            "presion": "🚨 RUPTURA: Quemaito mayor 16 listo para salir en banda",
            "dia_tendencia": f"{dia_hoy}: Frecuencia de combinaciones directas"
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
        "salidor": "62 - 85 - 89",
        "dictamen": {
            "flujo": "ALTO (60 al 89)",
            "decena": "Los 60s y 20s (60-69 / 20-29)",
            "terminal": "Terminales 2, 6 y 5",
            "pareja": "MEDIA (44)",
            "digito_fuerte": "Dígitos 2 y 6",
            "presion": "🚨 RUPTURA: Línea 62 con rotación favorable",
            "dia_tendencia": f"{dia_hoy}: Cruces de números caribeños"
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
        "salidor": "23 - 09 - 03",
        "dictamen": {
            "flujo": "BAJO (00 al 39)",
