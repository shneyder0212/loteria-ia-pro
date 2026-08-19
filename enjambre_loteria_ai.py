import sqlite3
import numpy as np
from datetime import datetime
from collections import Counter, defaultdict

class AgenteNumero:
    def __init__(self, id_num):
        self.id_num = id_num
        self.str_num = str(id_num).zfill(2)
        self.peso_confianza = 1.0
        self.retraso_actual = 0
        self.afinidad_loterias = Counter()
        self.red_socios = Counter()

    def evaluar_presion(self, historial_p1):
        apariciones = [i for i, n in enumerate(historial_p1[-40:]) if int(n) == self.id_num]
        if not apariciones:
            self.retraso_actual = 40
            score_presion = 3.0
        else:
            self.retraso_actual = len(historial_p1[-40:]) - 1 - apariciones[-1]
            score_presion = 1.0 + (self.retraso_actual * 0.1)
        return score_presion * self.peso_confianza


class Enjambre100AgentesLoteria:
    def __init__(self, db_path="loteria_master_ai.db"):
        self.db_path = db_path
        self._inicializar_bd()
        self.agentes = [AgenteNumero(i) for i in range(100)]
        self.matriz_comunicacion = np.zeros((100, 100))
        self._inicializar_matriz_comunicacion()

    def _inicializar_bd(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
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
            conn.commit()

    def _inicializar_matriz_comunicacion(self):
        for i in range(100):
            self.matriz_comunicacion[i][(i + 25) % 100] = 2.5
            self.matriz_comunicacion[i][(i + 50) % 100] = 2.5
            self.matriz_comunicacion[i][(i + 75) % 100] = 2.0
            self.matriz_comunicacion[i][int(str(i).zfill(2)[::-1])] = 2.0

    def sincronizar_aprendizaje_historico(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT primero, segundo, tercero, loteria FROM sorteos ORDER BY id ASC")
            filas = c.fetchall()

        if not filas:
            return

        for p1, p2, p3, lot in filas:
            nums = [int(n) for n in [p1, p2, p3] if n and n.isdigit()]
            if nums:
                p1_idx = nums[0]
                self.agentes[p1_idx].afinidad_loterias[lot] += 1
                for socio in nums[1:]:
                    self.agentes[p1_idx].red_socios[socio] += 1
                    self.matriz_comunicacion[p1_idx][socio] += 0.5
                    self.matriz_comunicacion[socio][p1_idx] += 0.5

    def autoajustar_red(self, numero_ganador):
        g = int(numero_ganador)
        self.agentes[g].peso_confianza = min(3.0, self.agentes[g].peso_confianza * 1.05)
        for i, ag in enumerate(self.agentes):
            if i != g:
                ag.peso_confianza = max(0.5, ag.peso_confianza * 0.99)

    def ejecutar_consenso_100_agentes(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT primero, loteria FROM sorteos ORDER BY id ASC")
            filas = c.fetchall()

        if len(filas) < 3:
            return {"error": "Se requieren al menos 3 sorteos registrados para que la IA debata."}

        self.sincronizar_aprendizaje_historico()
        hist_p1 = [f[0] for f in filas]
        ultimo_salidor = int(hist_p1[-1])

        votos_base = np.zeros(100)
        for i, ag in enumerate(self.agentes):
            votos_base[i] = ag.evaluar_presion(hist_p1)

        senales_cruzadas = np.dot(self.matriz_comunicacion[ultimo_salidor], self.matriz_comunicacion)
        vector_consenso = votos_base * 0.4 + senales_cruzadas * 0.6
        max_val = np.max(vector_consenso)
        ranking = np.argsort(vector_consenso)[::-1]

        top_20 = []
        for idx in ranking[:20]:
            ag = self.agentes[idx]
            fuerza = round((vector_consenso[idx] / max_val) * 98.9, 1)
            lot_fav = ag.afinidad_loterias.most_common(1)
            lot_nombre = lot_fav[0][0] if lot_fav else "Gana Mas 2:30pm / Nacional Noche"
            top_20.append({
                "numero": ag.str_num,
                "fuerza_ia": fuerza,
                "loteria": lot_nombre
            })

        top_5_fuerte = top_20[:5]
        m1, m2, m3 = top_20[0], top_20[1], top_20[2]

        pales = []
        for c in top_20[1:11]:
            pales.append({"pale": f"{m1['numero']} - {c['numero']}", "fuerza": round((m1['fuerza_ia'] + c['fuerza_ia'])/2, 1), "loteria": m1['loteria']})
        for c in top_20[2:8]:
            pales.append({"pale": f"{m2['numero']} - {c['numero']}", "fuerza": round((m2['fuerza_ia'] + c['fuerza_ia'])/2, 1), "loteria": m2['loteria']})
        for c in top_20[3:7]:
            pales.append({"pale": f"{m3['numero']} - {c['numero']}", "fuerza": round((m3['fuerza_ia'] + c['fuerza_ia'])/2, 1), "loteria": m3['loteria']})

        tripletas = []
        for c in top_20[2:12]:
            tripletas.append({"tripleta": f"{m1['numero']} - {m2['numero']} - {c['numero']}", "loteria": m1['loteria']})
        for c in top_20[3:9]:
            tripletas.append({"tripleta": f"{m1['numero']} - {m3['numero']} - {c['numero']}", "loteria": m1['loteria']})
        for c in top_20[3:7]:
            tripletas.append({"tripleta": f"{m2['numero']} - {m3['numero']} - {c['numero']}", "loteria": m2['loteria']})

        return {
            "ultimo_salidor": str(ultimo_salidor).zfill(2),
            "top_5_lineas_fuertes": top_5_fuerte,
            "pivotes_mayores": [m1, m2, m3],
            "top_20_sueltos": top_20,
            "top_20_pales": pales[:20],
            "top_20_tripletas": tripletas[:20]
        }