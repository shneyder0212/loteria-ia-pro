import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

class BaseDatosLoteria:
    def __init__(self, db_path="loteria_master_ai.db"):
        self.db_path = db_path
        self._inicializar_bd()

    def _inicializar_bd(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sorteos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT NOT NULL,
                    dia_semana INTEGER NOT NULL,
                    dia_mes INTEGER NOT NULL,
                    loteria TEXT NOT NULL,
                    primero TEXT NOT NULL,
                    segundo TEXT,
                    tercero TEXT,
                    timestamp REAL NOT NULL,
                    UNIQUE(fecha, loteria)
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_loteria_fecha ON sorteos(fecha, loteria)")
            conn.commit()

    def guardar_sorteo(self, fecha_str, loteria, primero, segundo=None, tercero=None):
        dt = datetime.strptime(fecha_str, "%Y-%m-%d")
        p1 = str(primero).zfill(2)
        p2 = str(segundo).zfill(2) if segundo else None
        p3 = str(tercero).zfill(2) if tercero else None

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO sorteos (fecha, dia_semana, dia_mes, loteria, primero, segundo, tercero, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (fecha_str, dt.weekday(), dt.day, loteria, p1, p2, p3, time.time()))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False


class ScraperLoteriasRD:
    def __init__(self, db_path="loteria_master_ai.db"):
        self.db = BaseDatosLoteria(db_path)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.mapeo_nombres = {
            "gana mas": "Gana Mas 2:30pm",
            "nacional": "Nacional Noche 8:50pm",
            "leidsa": "Quiniela Pale Leidsa",
            "real": "Real 1pm",
            "primera dia": "Primera Dia 12pm",
            "primera noche": "Primera Noche 8pm",
            "suerte dia": "Suerte Dia 12:30pm",
            "suerte noche": "Suerte Noche 6pm",
            "lotedom": "Lotedom 1:55pm",
            "anguila 10": "Anguilla 10am",
            "anguila 1": "Anguilla 1pm",
            "anguila 6": "Anguilla 6pm",
            "anguila 9": "Anguilla Noche 9pm",
            "new york dia": "New York Dia",
            "new york noche": "New York Noche",
            "florida dia": "Florida Dia",
            "florida noche": "Florida Noche"
        }

    def _normalizar_nombre(self, texto_bruto):
        texto = texto_bruto.lower().strip()
        for clave, nombre_oficial in self.mapeo_nombres.items():
            if clave in texto:
                return nombre_oficial
        return texto_bruto.strip().title()

    def sincronizar_todo(self):
        url = "https://www.conectate.com.do/loterias/"
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        sorteos_procesados = []

        try:
            response = requests.get(url, headers=self.headers, timeout=12)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                bloques = soup.find_all("div", class_=re.compile(r"game-block|lottery-block|block-game|card|game"))

                for bloque in bloques:
                    titulo_tag = bloque.find(["a", "h3", "h4", "span", "div"], class_=re.compile(r"title|game-title|name"))
                    if not titulo_tag:
                        continue

                    nombre_loteria = self._normalizar_nombre(titulo_tag.get_text(strip=True))
                    bolos = [b.get_text(strip=True).zfill(2) for b in bloque.find_all(["span", "div"], class_=re.compile(r"score|number|bolo|ball")) if b.get_text(strip=True).isdigit()]

                    if len(bolos) >= 1:
                        p1 = bolos[0]
                        p2 = bolos[1] if len(bolos) > 1 else None
                        p3 = bolos[2] if len(bolos) > 2 else None

                        insertado = self.db.guardar_sorteo(fecha_hoy, nombre_loteria, p1, p2, p3)
                        sorteos_procesados.append({
                            "loteria": nombre_loteria,
                            "1ra": p1,
                            "2da": p2,
                            "3ra": p3,
                            "nuevo": insertado
                        })
        except Exception as e:
            print(f"[Aviso Scraper] {e}")

        return sorteos_procesados