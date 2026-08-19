import json
import sqlite3
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Shneyder IA Pro RD")
DB_PATH = "loteria_master_ai.db"

# Base de datos cuántica con todas las loterías de RD y el Caribe
DATOS_LOTERIAS = {
    "todas": {
        "nombre": "Todas las Loterías (Consenso General)",
        "salidor": "40 - 72 - 18",
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
            {"num": "33", "fuerza": 30.1, "tipo": "fuerte", "lot": "Anguila 9:00pm"},
            {"num": "88", "fuerza": 28.4, "tipo": "caliente", "lot": "Loteria Real 12:55pm"},
            {"num": "67", "fuerza": 25.0, "tipo": "atrasado", "lot": "Loteka 7:55pm"},
            {"num": "12", "fuerza": 22.8, "tipo": "fuerte", "lot": "New York Noche"}
        ]
    },
    "nacional": {
        "nombre": "Gana Más (2:30 PM) / Nacional Noche (8:50 PM)",
        "salidor": "40 - 72 - 18",
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
        "sueltos": [
            {"num": "10", "fuerza": 89.2, "tipo": "fuerte", "lot": "La Suerte 6PM"},
            {"num": "01", "fuerza": 80.2, "tipo": "virado", "lot": "La Suerte 6PM"},
            {"num": "53", "fuerza": 75.8, "tipo": "caliente", "lot": "La Suerte 6PM"},
            {"num": "09", "fuerza": 70.4, "tipo": "atrasado", "lot": "La Suerte 6PM"},
            {"num": "57", "fuerza": 64.9, "tipo
