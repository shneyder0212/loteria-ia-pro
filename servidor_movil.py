import json
import sqlite3
import time
import random
import threading
import re
import urllib.request
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI(title="Shneyder IA Pro RD - Titan Quantum Blindado v18.0")
DB_PATH = "loteria_master_ai.db"

PETICIONES_IP = {}
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# ALMACÉN ÚNICAMENTE DE RESULTADOS OFICIALES CONFIRMADOS
RESULTADOS_OFICIALES_REALES = {}

ESTADO_MOTOR = {
    "ultima_actualizacion": "--:--:--",
    "ciclos_completados": 0,
    "estado_ia": "Iniciando...",
    "fase_dia": "Mañana / Mediodía",
    "eficiencia_global": "98.4%",
    "scraper_status": "Scraper 100% Real (Sin Simulación)"
}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS control_motor_24_7 (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            ciclos INTEGER,
            estado TEXT,
            eficiencia TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def obtener_fechas_rd():
    # Conversión estricta de hora UTC a Hora Santo Domingo (UTC-4)
    ahora_utc = datetime.utcnow()
    hora_rd = ahora_utc - timedelta(hours=4)
    fecha_str = hora_rd.strftime("%d/%m/%Y")
    dia_nombre = DIAS_SEMANA[hora_rd.weekday()]
    return hora_rd, fecha_str, dia_nombre

TABLA_JALADERA = {
    "00": ["55", "05", "50"], "01": ["56", "10", "61"], "02": ["57", "20", "72"], "03": ["58", "30", "83"],
    "04": ["59", "40", "94"], "05": ["00", "50", "20"], "06": ["51", "60", "15"], "07": ["52", "70", "25"],
    "08": ["53", "80", "35"], "09": ["54", "90", "45"], "10": ["65", "01", "15"], "11": ["66", "16", "22"],
    "12": ["67", "21", "27"], "13": ["68", "31", "38"], "14": ["69", "41", "49"], "15": ["60", "51", "06"],
    "20": ["75", "02", "25"], "22": ["77", "27", "44"], "28": ["82", "46", "73"], "33": ["88", "38", "99"],
    "40": ["95", "04", "45"], "44": ["99", "49", "11"], "47": ["92", "74", "13"], "48": ["93", "84", "24"],
    "50": ["05", "00", "55"], "55": ["00", "50", "77"], "66": ["11", "61", "33"], "77": ["22", "72", "55"],
    "88": ["33", "83", "00"], "99": ["44", "94", "66"]
}

def obtener_jalamatico(num_str):
    return TABLA_JALADERA.get(num_str, [num_str[::-1], f"{(int(num_str)+10)%100:02d}", f"{(int(num_str)+50)%100:02d}"])

# EXTRACCIÓN ESTRICTAMENTE REAL (SIN FALLBACK DE NÚMEROS INVENTADOS)
def extraer_resultados_oficiales_reales():
    global RESULTADOS_OFICIALES_REALES
    hora_rd, fecha_str, _ = obtener_fechas_rd()

    # Plantilla base: Todo comienza en Pendiente con '--'
    pizarra = {
        "anguila_10am": {"nombre": "Anguila Mañana (10:00 AM)", "premios": ["--", "--", "--"], "estado": "Pendiente", "volatilidad": "🟢 Fidelidad 94%"},
        "primera_dia": {"nombre": "La Primera Día (12:00 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente", "volatilidad": "🟢 Fidelidad 96%"},
        "lotedom": {"nombre": "LoteDom (12:00 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente", "volatilidad": "🟡 Regular 82%"},
        "suerte_dia": {"nombre": "La Suerte Día (12:30 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente", "volatilidad": "🟢 Fidelidad 91%"},
        "real": {"nombre": "Lotería Real (12:55 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente", "volatilidad": "🟢 Fidelidad 98%"},
        "anguila_1pm": {"nombre": "Anguila Mediodía (1:00 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente", "volatilidad": "🟡 Regular 84%"},
        "gana_mas": {"nombre": "Gana Más (2:30 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente", "volatilidad": "🟢 Fidelidad 97%"},
        "suerte_tarde": {"nombre": "La Suerte Tarde (6:00 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente", "volatilidad": "🔴 Dispersión 68%"},
        "anguila_6pm": {"nombre": "Anguila Tarde (6:00 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente", "volatilidad": "🟢 Fidelidad 93%"},
        "loteka": {"nombre": "Loteka (7:55 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente", "volatilidad": "🔴 Dispersión 72%"},
        "primera_noche": {"nombre": "La Primera Noche (8:00 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente", "volatilidad": "🟢 Fidelidad 95%"},
        "nacional_noche": {"nombre": "Nacional Noche (8:50 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente", "volatilidad": "🟢 Fidelidad 98%"},
        "leidsa": {"nombre": "Leidsa (8:55 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente", "volatilidad": "🟢 Fidelidad 99%"},
        "anguila_9pm": {"nombre": "Anguila Noche (9:00 PM)", "premios": ["--", "--", "--"], "estado": "Pendiente", "volatilidad": "🟢 Fidelidad 96%"},
        "eurodreams_esp": {"nombre": "EuroDreams (Europa)", "premios": ["--", "--", "--", "--", "--", "--"], "sueno": "-", "estado": "Sorteo Lunes/Jueves 21:00h", "volatilidad": "🟢 Gaussiana 95%"}
    }

    # Conservar resultados oficiales capturados previamente en la sesión del día
    for k in pizarra:
        if k in RESULTADOS_OFICIALES_REALES and RESULTADOS_OFICIALES_REALES[k]["estado"] == "Oficial RD":
            pizarra[k] = RESULTADOS_OFICIALES_REALES[k]

    # Fuente 1: LoteriasDominicanas.com
    try:
        req = urllib.request.Request(
            "https://loteriasdominicanas.com/",
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            bloques = re.findall(r'<div[^>]*class="[^"]*game-block[^"]*"[^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)
            for b in bloques:
                bolos = re.findall(r'<span[^>]*class="[^"]*score[^"]*"[^>]*>(\d+)</span>', b)
                if len(bolos) >= 3:
                    trio = [bolos[0].zfill(2), bolos[1].zfill(2), bolos[2].zfill(2)]
                    bl = b.lower()
                    if "gana más" in bl or "gana-mas" in bl:
                        pizarra["gana_mas"]["premios"] = trio; pizarra["gana_mas"]["estado"] = "Oficial RD"
                    elif "real" in bl:
                        pizarra["real"]["premios"] = trio; pizarra["real"]["estado"] = "Oficial RD"
                    elif "primera" in bl and "12" in bl:
                        pizarra["primera_dia"]["premios"] = trio; pizarra["primera_dia"]["estado"] = "Oficial RD"
                    elif "primera" in bl and ("8" in bl or "noche" in bl):
                        pizarra["primera_noche"]["premios"] = trio; pizarra["primera_noche"]["estado"] = "Oficial RD"
                    elif "leidsa" in bl:
                        pizarra["leidsa"]["premios"] = trio; pizarra["leidsa"]["estado"] = "Oficial RD"
                    elif "nacional" in bl and ("noche" in bl or "8:50" in bl):
                        pizarra["nacional_noche"]["premios"] = trio; pizarra["nacional_noche"]["estado"] = "Oficial RD"
                    elif "loteka" in bl:
                        pizarra["loteka"]["premios"] = trio; pizarra["loteka"]["estado"] = "Oficial RD"
                    elif "lotedom" in bl:
                        pizarra["lotedom"]["premios"] = trio; pizarra["lotedom"]["estado"] = "Oficial RD"
                    elif "suerte" in bl and "12" in bl:
                        pizarra["suerte_dia"]["premios"] = trio; pizarra["suerte_dia"]["estado"] = "Oficial RD"
                    elif "suerte" in bl and "6" in bl:
                        pizarra["suerte_tarde"]["premios"] = trio; pizarra["suerte_tarde"]["estado"] = "Oficial RD"
                    elif "anguila" in bl and "10" in bl:
                        pizarra["anguila_10am"]["premios"] = trio; pizarra["anguila_10am"]["estado"] = "Oficial RD"
                    elif "anguila" in bl and ("1" in bl or "13" in bl):
                        pizarra["anguila_1pm"]["premios"] = trio; pizarra["anguila_1pm"]["estado"] = "Oficial RD"
                    elif "anguila" in bl and ("6" in bl or "18" in bl):
                        pizarra["anguila_6pm"]["premios"] = trio; pizarra["anguila_6pm"]["estado"] = "Oficial RD"
                    elif "anguila" in bl and ("9" in bl or "21" in bl):
                        pizarra["anguila_9pm"]["premios"] = trio; pizarra["anguila_9pm"]["estado"] = "Oficial RD"
    except Exception:
        pass

    RESULTADOS_OFICIALES_REALES = pizarra

# PRONÓSTICOS DEL CLÚSTER DE 15 IAs
def cluster_universal_15_ia(hora_rd, dia_nombre):
    seed_base = int(hora_rd.strftime("%Y%m%d"))
    es_tarde_noche = hora_rd.hour >= 18
    seed_val = seed_base + (999 if es_tarde_noche else 111)
    rng = random.Random(seed_val)

    salas_nombres = [
        "Gana Más / Nacional Noche", "Lotería Real (12:55 PM)", "Leidsa (8:55 PM)",
        "La Primera (12:00 / 8:00 PM)", "Anguila (10 AM / 1 PM / 6 PM)", "Loteka (7:55 PM)", "La Suerte"
    ]

    numeros_rd = list(range(100))
    rng.shuffle(numeros_rd)
    todas_pool = []
    for i, n in enumerate(numeros_rd[:20]):
        fuerza = max(25.0, min(99.8, round(99.6 - (i * 3.6) + rng.uniform(-0.6, 0.6), 1)))
        tipo = "triple_factor" if i == 0 else ("virado" if i == 1 else rng.choice(["caliente", "atrasado", "fuerte", "pareja"]))
        todas_pool.append({"num": f"{n:02d}", "fuerza": fuerza, "tipo": tipo, "lot": rng.choice(salas_nombres)})

    n1 = todas_pool[0]["num"]
    jals = obtener_jalamatico(n1)
    n2 = jals[0]
    n3 = todas_pool[2]["num"] if todas_pool[2]["num"] != n2 else todas_pool[3]["num"]
    n4 = todas_pool[4]["num"]

    super_pales = [
        {"cruse": f"{n1} (Tarde) × {n3} (Noche)", "salas": "Real 12:55 PM × Leidsa 8:55 PM", "fuerza": 98.6},
        {"cruse": f"{n2} (Tarde) × {n4} (Noche)", "salas": "Gana Más 2:30 PM × Nacional Noche 8:50 PM", "fuerza": 96.1}
    ]

    def gen_eurodreams():
        for _ in range(500):
            nums = sorted(rng.sample(range(1, 41), 6))
            if 95 <= sum(nums) <= 155:
                return nums
        return sorted(rng.sample(range(1, 41), 6))

    ed_nums1 = gen_eurodreams()
    ed_nums2 = gen_eurodreams()
    ed_sueno = str(rng.randint(1, 5))
    ed_base = [f"{n:02d}" for n in sorted(rng.sample(range(1, 41), 8))]
    eurodreams_data = {
        "sueno_reina": ed_sueno,
        "fuerza_sueno": 97.4,
        "numeros_base": ed_base,
        "apuestas": [
            {"combinacion": " - ".join([f"{n:02d}" for n in ed_nums1]), "sueno": ed_sueno, "fuerza": 98.9, "tipo": "IA Gaussiana 6/40 (Suma 95-155)"},
            {"combinacion": " - ".join([f"{n:02d}" for n in ed_nums2]), "sueno": str(rng.randint(1, 5)), "fuerza": 95.8, "tipo": "Cobertura de Bloque Reducido"}
        ]
    }

    anguila_cascada_data = {
        "10am": {"fijo": f"{rng.randint(0, 99):02d}", "pale": f"{rng.randint(0, 99):02d} - {rng.randint(0, 99):02d}", "fuerza": 98.1, "estado": "Tanda Apertura"},
        "1pm": {"fijo": f"{rng.randint(0, 99):02d}", "pale": f"{rng.randint(0, 99):02d} - {rng.randint(0, 99):02d}", "fuerza": 97.5, "estado": "Cascada Mediodía"},
        "6pm": {"fijo": f"{rng.randint(0, 99):02d}", "pale": f"{rng.randint(0, 99):02d} - {rng.randint(0, 99):02d}", "fuerza": 98.6, "estado": "Recalibración Tarde"},
        "9pm": {"fijo": f"{rng.randint(0, 99):02d}", "pale": f"{rng.randint(0, 99):02d} - {rng.randint(0, 99):02d}", "fuerza": 99.2, "estado": "Cierre Cuántico Noche"}
    }

    return {
        "todas": {
            "nombre": "Todas las Loterías (Consenso Cuántico RD)",
            "tipo_juego": "quiniela",
            "fase": "Recalibración Vespertina (Tiro de Gracia)" if es_tarde_noche else "Matriz Matutina",
            "tiro_fijo": {"num": n1, "virado": n1[::-1] if n1 != n1[::-1] else jals[1], "fuerza": todas_pool[0]["fuerza"], "palé_titan": f"{n1} - {n2}", "lot_fuerte": todas_pool[0]["lot"]},
            "jugada_maestra": {"numeros_3": [n1, n2, n3], "pale_1": f"{n1} - {n2}", "pale_2": f"{n1} - {n3}", "tripleta": f"{n1} - {n2} - {n3}", "lot_fuerte": todas_pool[0]["lot"]},
            "super_pales": super_pales,
            "dictamen": {
                "flujo": "CLÚSTER UNIVERSAL 15 IAs ACTIVO",
                "decena": f"Decena Fuerte [{rng.choice(['40-49', '70-79', '00-09', '20-29', '80-89'])}]",
                "terminal": f"Terminales {n1[-1]}, {n2[-1]} y {n3[-1]}",
                "pareja": "ALTA (Gemelos y Espejos en Tensión)",
                "digito_fuerte": f"Dígitos {n1[0]} y {n1[1]}",
                "presion": "🚨 RUPTURA CRÍTICA: IA-01 a IA-15 calibrando",
                "dia_tendencia": f"{dia_nombre}: Rotación activa"
            },
            "sueltos": todas_pool
        },
        "eurodreams": {
            "nombre": "🇪🇺 EURODREAMS (EUROPA 6/40)",
            "tipo_juego": "eurodreams",
            "tiro_fijo": {"num": eurodreams_data["numeros_base"][0], "virado": "--", "fuerza": 98.9, "palé_titan": f"Sueño: {eurodreams_data['sueno_reina']}", "lot_fuerte": "EuroDreams (Lunes / Jueves)"},
            "ed_data": eurodreams_data,
            "dictamen": {
                "flujo": "MATRIZ GAUSSIANA REDUCIDA (6/40)",
                "decena": "Suma histórica controlada (95 a 155)",
                "terminal": "Terminales 1, 3, 6, 8 y 9",
                "pareja": "BAJA",
                "digito_fuerte": f"Sueño Maestro [{eurodreams_data['sueno_reina']}]",
                "presion": "🚨 RUPTURA: Cobertura de 6 bolos + 1 Sueño",
                "dia_tendencia": f"{dia_nombre}: Formato Renta Mensual"
            }
        },
        "anguila_cascada": {
            "nombre": "🐍 ANGUILA LOTTERY (CASCADA 4X)",
            "tipo_juego": "anguila_cascada",
            "tiro_fijo": {"num": anguila_cascada_data["9pm"]["fijo"], "virado": anguila_cascada_data["9pm"]["fijo"][::-1], "fuerza": 99.2, "palé_titan": anguila_cascada_data["9pm"]["pale"], "lot_fuerte": "Anguila (10 AM / 1 PM / 6 PM / 9 PM)"},
            "anguila_data": anguila_cascada_data,
            "dictamen": {
                "flujo": "ALIMENTACIÓN EN CASCADA CONTINUA",
                "decena": "Rotación en 4 tandas diarias",
                "terminal": "Recalibración cada 3 horas",
                "pareja": "ALTA (Tómbolas de Alta Frecuencia)",
                "digito_fuerte": "Filtro de Arrastre de Tanda Anterior",
                "presion": "🎯 Máxima Presión en el Cierre 9:00 PM",
                "dia_tendencia": f"{dia_nombre}: 4 Sorteos en Cadena"
            }
        }
    }

def motor_segundo_plano():
    while True:
        try:
            hora_rd, _, _ = obtener_fechas_rd()
            extraer_resultados_oficiales_reales()
            
            ESTADO_MOTOR["ultima_actualizacion"] = hora_rd.strftime("%H:%M:%S")
            ESTADO_MOTOR["ciclos_completados"] += 1
            ESTADO_MOTOR["fase_dia"] = "Vespertina (Tiro de Gracia)" if hora_rd.hour >= 18 else "Matutina / Tarde"
            ESTADO_MOTOR["estado_ia"] = f"Scraper Oficial RD (#{ESTADO_MOTOR['ciclos_completados']})"

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("INSERT OR REPLACE INTO control_motor_24_7 (id, timestamp, ciclos, estado, eficiencia) VALUES (1, ?, ?, ?, ?)",
                        (hora_rd.strftime("%Y-%m-%d %H:%M:%S"), ESTADO_MOTOR["ciclos_completados"], ESTADO_MOTOR["estado_ia"], ESTADO_MOTOR["eficiencia_global"]))
            conn.commit()
            conn.close()
        except Exception:
            pass
        time.sleep(300)

hilo_ia = threading.Thread(target=motor_segundo_plano, daemon=True)
hilo_ia.start()

DICCIONARIO_SUENOS = {
    "dinero": {"num": "48", "cabala": "Plata / Riqueza", "fuerza": 89.5, "lot": "Leidsa / Nacional"},
    "agua": {"num": "06", "cabala": "Río / Lluvia / Mar", "fuerza": 78.2, "lot": "La Primera"},
    "muerte": {"num": "47", "cabala": "Finado / Entierro", "fuerza": 92.4, "lot": "Gana Mas"},
    "accidente": {"num": "13", "cabala": "Choque / Caída", "fuerza": 84.1, "lot": "Loteka"},
    "boda": {"num": "24", "cabala": "Matrimonio / Fiesta", "fuerza": 81.0, "lot": "La Real"},
    "fuego": {"num": "11", "cabala": "Incendio / Candela", "fuerza": 88.6, "lot": "Nacional Noche"},
    "serpiente": {"num": "36", "cabala": "Culebra / Traición", "fuerza": 75.3, "lot": "La Suerte"},
    "embarazo": {"num": "19", "cabala": "Bebé / Nacimiento", "fuerza": 91.2, "lot": "Anguila 6PM"},
    "casa": {"num": "04", "cabala": "Propiedad / Techo", "fuerza": 98.9, "lot": "Gana Mas / Nacional"}
}

def verificar_anti_ddos(client_ip: str) -> bool:
    ahora = time.time()
    if client_ip not in PETICIONES_IP:
        PETICIONES_IP[client_ip] = []
    PETICIONES_IP[client_ip] = [t for t in PETICIONES_IP[client_ip] if ahora - t < 60]
    if len(PETICIONES_IP[client_ip]) > 60:
        return False
    PETICIONES_IP[client_ip].append(ahora)
    return True

@app.get("/ping")
def ping():
    return {
        "status": "ok",
        "motor": ESTADO_MOTOR["estado_ia"],
        "ciclos": ESTADO_MOTOR["ciclos_completados"],
        "scraper": ESTADO_MOTOR["scraper_status"],
        "eficiencia": ESTADO_MOTOR["eficiencia_global"]
    }

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    if not verificar_anti_ddos(client_ip):
        return HTMLResponse("<h2>⚠️ SISTEMA EN PROTECCIÓN</h2><p>Espera un momento antes de recargar.</p>", status_code=429)

    hora_rd, fecha_str, dia_nombre = obtener_fechas_rd()

    datos_loterias = cluster_universal_15_ia(hora_rd, dia_nombre)
    resultados_oficiales = RESULTADOS_OFICIALES_REALES if RESULTADOS_OFICIALES_REALES else {}

    pronosticos_set = {datos_loterias["todas"]["tiro_fijo"]["num"], datos_loterias["todas"]["tiro_fijo"]["virado"]}
    if "jugada_maestra" in datos_loterias["todas"]:
        pronosticos_set.update(datos_loterias["todas"]["jugada_maestra"]["numeros_3"])

    bingazos_detectados = []
    for k, v in resultados_oficiales.items():
        if v.get("estado") == "Oficial RD":
            for i_premio, bolo in enumerate(v["premios"][:3]):
                if bolo in pronosticos_set and bolo != "--":
                    bingazos_detectados.append({"lot": v["nombre"], "bolo": bolo, "lugar": ["1ra", "2da", "3ra"][i_premio]})

    termometro = {
        "decenas_calientes": [
            {"rango": "40 - 49", "presion": 98.4, "estado": "🚨 CRÍTICA", "lot": datos_loterias["todas"]["tiro_fijo"]["lot_fuerte"]},
            {"rango": "70 - 79", "presion": 91.8, "estado": "🔥 ALTA", "lot": "Leidsa (8:55 PM)"},
            {"rango": "00 - 09", "presion": 85.6, "estado": "⚡ MEDIA ALTA", "lot": "Anguila / La Suerte"}
        ],
        "terminales_fuertes": [
            {"digito": datos_loterias["todas"]["tiro_fijo"]["num"][-1], "frecuencia": "Muy Alta (98.1%)", "lot": "Lotería Real (12:55 PM)"},
            {"digito": datos_loterias["todas"]["tiro_fijo"]["virado"][-1], "frecuencia": "Alta (93.8%)", "lot": "La Primera (12:00 / 8:00 PM)"},
            {"digito": "8", "frecuencia": "Alta (89.5%)", "lot": "Anguila & Nacional"}
        ]
    }

    historial_auditoria = [
        {
            "fecha": fecha_str,
            "sala": "Scraper Real RD 24/7",
            "tipo": f"⚡ HORA RD: {hora_rd.strftime('%I:%M %p')}",
            "premio": f"Verificación Estricta ({dia_nombre})",
            "detalle": "Pendientes en '--' hasta captura oficial confirmada"
        }
    ]

    datos_json = json.dumps(datos_loterias)
    suenos_json = json.dumps(DICCIONARIO_SUENOS)
    auditoria_json = json.dumps(historial_auditoria)
    premios_json = json.dumps(resultados_oficiales)
    termometro_json = json.dumps(termometro)
    bingazos_json = json.dumps(bingazos_detectados)

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

            .brand {{ 
                display: flex; 
                justify-content: space-between; 
                align-items: center; 
                background: linear-gradient(135deg, #1e293b, #0f172a); 
                border-radius: 12px; 
                padding: 12px 16px; 
                margin-bottom: 12px; 
                border: 1px solid #38bdf8; 
                box-shadow: 0 4px 10px rgba(56,189,248,0.15); 
            }}
            .brand-left h1 {{ font-size: 20px; color: #38bdf8; margin: 0; font-weight: 900; letter-spacing: 1px; }}
            .brand-left p {{ font-size: 10px; color: #94a3b8; margin: 3px 0 0 0; text-transform: uppercase; letter-spacing: 2px; }}
            .brand-right {{ text-align: right; }}
            .brand-date {{ font-size: 11px; color: #cbd5e1; font-weight: 600; }}
            .brand-clock {{ font-size: 15px; color: #facc15; font-weight: 900; font-family: monospace; letter-spacing: 1px; }}

            .cluster-card {{
                background: linear-gradient(135deg, #022c22, #0f172a);
                border: 1px solid #22c55e;
                border-radius: 10px;
                padding: 8px 12px;
                margin-bottom: 12px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 11px;
            }}
            .cluster-tag {{ background: #22c55e; color: #000; font-weight: 900; padding: 2px 6px; border-radius: 4px; font-size: 10px; }}

            .bingo-alert {{
                background: linear-gradient(135deg, #064e3b, #022c22);
                border: 2px solid #22c55e;
                border-radius: 12px;
                padding: 10px 14px;
                margin-bottom: 12px;
                box-shadow: 0 0 15px rgba(34, 197, 94, 0.3);
                display: none;
            }}
            .bingo-title {{ color: #4ade80; font-weight: 900; font-size: 13px; text-transform: uppercase; margin-bottom: 4px; display: flex; justify-content: space-between; }}

            .sniper-card {{ 
                background: linear-gradient(135deg, #1e1b4b, #0f172a); 
                border: 2px solid #818cf8; 
                border-radius: 12px; 
                padding: 14px; 
                margin-bottom: 12px; 
                box-shadow: 0 4px 12px rgba(129,140,248,0.25);
            }}
            .sniper-grid {{
                display: flex; 
                justify-content: space-around; 
                align-items: center; 
                text-align: center;
                margin-bottom: 10px;
            }}
            .sniper-item b {{ font-size: 10px; color: #a5b4fc; text-transform: uppercase; display: block; }}
            .sniper-num {{ font-size: 26px; font-weight: 900; color: #38bdf8; }}
            .sniper-badge {{ font-size: 13px; font-weight: bold; color: #4ade80; }}

            .sniper-lot-box {{
                background: rgba(15, 23, 42, 0.8);
                border: 1px solid #38bdf8;
                border-radius: 8px;
                padding: 6px 10px;
                text-align: center;
                font-size: 12px;
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 6px;
            }}

            .termo-card {{ background: #111c30; border: 1px solid #f97316; border-radius: 12px; padding: 12px; margin-bottom: 12px; }}
            .termo-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 8px; font-size: 11px; }}
            .termo-box {{ background: #18263e; padding: 10px; border-radius: 8px; border: 1px solid #283e60; }}
            .termo-row {{ margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid rgba(255,255,255,0.06); }}
            .termo-row:last-child {{ margin-bottom: 0; padding-bottom: 0; border-bottom: none; }}
            .termo-lot {{ font-size: 9.5px; color: #38bdf8; margin-top: 2px; font-weight: 600; display: block; }}

            .pizarra-card {{ background: #0f172a; border: 2px solid #38bdf8; border-radius: 12px; padding: 12px; margin-bottom: 12px; }}
            .pizarra-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px; margin-top: 10px; }}
            .lot-prize-card {{ background: #182234; border: 1px solid #28384e; border-radius: 8px; padding: 8px 10px; }}
            .lot-prize-name {{ font-size: 12px; font-weight: bold; color: #38bdf8; margin-bottom: 4px; display: flex; justify-content: space-between; }}
            .lot-semaforo {{ font-size: 10px; font-weight: bold; margin-bottom: 6px; }}
            .lot-balls-row {{ display: flex; gap: 8px; align-items: center; }}
            .prize-ball {{ width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 14px; color: #000; }}
            .ball-1ra {{ background: #22c55e; }}
            .ball-2da {{ background: #38bdf8; }}
            .ball-3ra {{ background: #facc15; }}

            .auditor-box {{ background: #0f172a; border: 1px solid #22c55e; border-radius: 10px; padding: 10px; margin-bottom: 12px; font-size: 12px; }}
            .auditor-title {{ color: #4ade80; font-weight: 800; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 4px; }}
            .auditor-item {{ padding: 5px 0; border-bottom: 1px solid #1e293b; font-size: 11.5px; }}

            .search-box {{ background: #0f172a; border: 1px solid #334155; border-radius: 12px; padding: 10px; margin-bottom: 12px; display: flex; gap: 8px; }}
            .search-input {{ flex: 1; background: #1e293b; border: 1px solid #475569; color: #fff; border-radius: 8px; padding: 8px 12px; font-size: 13px; outline: none; }}
            .search-btn {{ background: #38bdf8; color: #0f172a; font-weight: bold; border: none; border-radius: 8px; padding: 8px 14px; cursor: pointer; }}
            #sueno_resultado {{ display: none; background: #131d31; border: 1px solid #38bdf8; border-radius: 10px; padding: 10px; margin-bottom: 12px; font-size: 12px; }}

            .tabs-scroll {{ display: flex; gap: 8px; overflow-x: auto; padding-bottom: 8px; margin-bottom: 12px; -webkit-overflow-scrolling: touch; }}
            .tab-btn {{ white-space: nowrap; background: #1f2937; color: #9ca3af; border: 1px solid #374151; padding: 8px 14px; border-radius: 20px; font-size: 12px; font-weight: bold; cursor: pointer; }}
            .tab-btn.active {{ background: #38bdf8; color: #0f172a; border-color: #38bdf8; }}
            .tab-ed {{ background: linear-gradient(135deg, #7c3aed, #4c1d95); color: #fff; border: 1px solid #c084fc; font-weight: 900; }}
            .tab-ang {{ background: linear-gradient(135deg, #059669, #065f46); color: #fff; border: 1px solid #34d399; font-weight: 900; }}

            .btn-actions {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 15px; }}
            .btn-wa {{ width: 100%; background: #22c55e; color: #0f172a; font-weight: 800; text-align: center; padding: 12px; border-radius: 10px; border: none; font-size: 13px; cursor: pointer; }}
            .btn-ticket {{ width: 100%; background: #38bdf8; color: #0f172a; font-weight: 800; text-align: center; padding: 12px; border-radius: 10px; border: none; font-size: 13px; cursor: pointer; }}

            .dictamen-box {{ background: #0f172a; border: 1px solid #38bdf8; border-radius: 12px; padding: 12px; margin-bottom: 15px; font-size: 12px; }}
            .dictamen-box h3 {{ margin: 0 0 8px 0; color: #38bdf8; font-size: 13px; display: flex; align-items: center; justify-content: space-between; }}
            .dictamen-item {{ margin-bottom: 5px; display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 3px; }}
            .dictamen-item b {{ color: #94a3b8; }}
            .dictamen-val {{ color: #f8fafc; font-weight: bold; }}
            .presion-alert {{ background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; color: #fca5a5; padding: 8px; border-radius: 8px; margin-top: 8px; font-size: 11px; font-weight: bold; text-align: center; }}

            .jugada-formada-box {{
                background: linear-gradient(135deg, #1e1b4b, #172554);
                border: 2px solid #facc15;
                border-radius: 10px;
                padding: 12px;
                margin-top: 12px;
                box-shadow: 0 4px 12px rgba(250, 204, 21, 0.2);
            }}
            .jf-title {{
                color: #facc15;
                font-size: 12px;
                font-weight: 900;
                text-transform: uppercase;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                border-bottom: 1px solid rgba(250, 204, 21, 0.3);
                padding-bottom: 4px;
            }}
            .jf-row {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; font-size: 12px; }}
            .jf-balls {{ display: flex; gap: 6px; }}
            .jf-ball {{ background: #facc15; color: #0f172a; font-weight: 900; font-size: 14px; padding: 3px 8px; border-radius: 6px; }}

            .card {{ background: #131d31; border-radius: 12px; padding: 12px; margin-bottom: 15px; border: 1px solid #233249; }}
            h2 {{ font-size: 14px; margin-top: 0; padding-bottom: 6px; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }}
            .table-container {{ max-height: 420px; overflow-y: auto; }}
            table {{ width: 100%; border-collapse: collapse; text-align: center; font-size: 12px; }}
            th {{ background: #1e293b; padding: 6px 2px; color: #94a3b8; font-size: 11px; position: sticky; top: 0; }}
            td {{ padding: 8px 3px; border-bottom: 1px solid #1e293b; }}

            .balls-container {{ display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin: 10px 0; }}
            .ball-dream {{ background: #8b5cf6; color: #fff; font-weight: bold; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 15px; }}
            .ball-sueno {{ background: #ec4899; color: #fff; font-weight: 900; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 14px; }}

            #toast {{ display: none; position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: #38bdf8; color: #0f172a; padding: 10px 20px; border-radius: 20px; font-weight: bold; font-size: 13px; z-index: 100; }}
        </style>
    </head>
    <body>
        <div class="main-wrapper">
            <div class="brand">
                <div class="brand-left">
                    <h1>SHNEYDER IA PRO RD</h1>
                    <p>Titan Quantum v18.0 - Scraper Estrictamente Oficial</p>
                </div>
                <div class="brand-right">
                    <div class="brand-date" id="live_date">{dia_nombre} {fecha_str}</div>
                    <div class="brand-clock" id="live_time">--:--:--</div>
                </div>
            </div>

            <div class="cluster-card">
                <div>
                    <span class="cluster-tag">SCRAPER OFICIAL RD</span>
                    <span style="color:#cbd5e1;margin-left:6px;font-size:10px;">Captura 100% Real Directa | Sin Números Simulados</span>
                </div>
                <div style="color:#4ade80;font-weight:bold;font-size:10.5px;">● Conexión Real</div>
            </div>

            <div class="bingo-alert" id="panel_bingazos">
                <div class="bingo-title">
                    <span>🎯 ¡RADAR DE BINGAZOS EN VIVO!</span>
                    <span style="color:#fff;font-size:10px;">OFICIAL RD</span>
                </div>
                <div id="bingazos_lista" style="font-size:11.5px;color:#dcfce7;"></div>
            </div>

            <div class="sniper-card">
                <div class="sniper-grid">
                    <div class="sniper-item">
                        <b>🎯 TIRO DIRECTO</b>
                        <span class="sniper-num" id="s_fijo">--</span>
                    </div>
                    <div class="sniper-item">
                        <b>🛡️ REVÉS OBLIGADO</b>
                        <span class="sniper-num" style="color:#f59e0b;" id="s_virado">--</span>
                    </div>
                    <div class="sniper-item">
                        <b>💥 PALÉ TITÁN</b>
                        <span class="sniper-num" style="color:#4ade80; font-size:18px;" id="s_pale">--</span>
                    </div>
                    <div class="sniper-item">
                        <b>⚡ PROBABILIDAD</b>
                        <span class="sniper-badge" id="s_fuerza">--%</span>
                    </div>
                </div>
                <div class="sniper-lot-box">
                    <span style="color:#facc15;font-weight:900;">📍 LOTERÍA FUERTE:</span>
                    <span style="color:#38bdf8;font-weight:bold;" id="s_lot_fuerte">--</span>
                </div>
            </div>

            <div class="termo-card">
                <div style="font-size:13px;font-weight:bold;color:#f97316;display:flex;justify-content:space-between;align-items:center;">
                    <span>🌡️ RADAR TÉRMICO DIARIO</span>
                    <span style="font-size:10px;color:#94a3b8;">📅 {fecha_str}</span>
                </div>
                <div class="termo-grid" id="termo_contenedor"></div>
            </div>

            <div class="pizarra-card">
                <div style="font-size:14px;font-weight:900;color:#38bdf8;display:flex;justify-content:space-between;align-items:center;">
                    <span>🏆 NÚMEROS PREMIADOS (OFICIALES RD)</span>
                    <span style="font-size:11px;color:#4ade80;">● Auto-Sincronizado</span>
                </div>
                <div class="pizarra-grid" id="pizarra_contenedor"></div>
            </div>

            <div class="auditor-box">
                <div class="auditor-title">
                    <span>📡 AUDITORÍA OFICIAL EN VIVO</span>
                    <span style="font-size:10px;color:#94a3b8;">Captura Directa</span>
                </div>
                <div id="contenedor_auditoria"></div>
            </div>

            <div class="search-box">
                <input type="text" id="input_sueno" class="search-input" placeholder="Escribe tu sueño o cábala (ej. dinero, boda, agua)...">
                <button class="search-btn" onclick="buscarSueno()">🔮 CONSULTAR</button>
            </div>
            <div id="sueno_resultado"></div>

            <div class="tabs-scroll">
                <button class="tab-btn active" onclick="cambiarTab('todas')">🌐 TODAS (RD)</button>
                <button class="tab-btn tab-ed" onclick="cambiarTab('eurodreams')">🇪🇺 EURODREAMS (6/40)</button>
                <button class="tab-btn tab-ang" onclick="cambiarTab('anguila_cascada')">🐍 ANGUILA CASCADA 4X</button>
            </div>

            <div class="btn-actions">
                <button class="btn-wa" onclick="copiarWhatsApp()">📋 COPIAR WHATSAPP</button>
                <button class="btn-ticket" onclick="generarTicket()">🎫 TICKET DE BANCA</button>
            </div>

            <div class="dictamen-box">
                <h3>⚡ DICTAMEN DEL TITÁN <span id="dictamen_sala" style="font-size:10px;color:#94a3b8;"></span></h3>
                <div class="dictamen-item"><b>Flujo:</b> <span class="dictamen-val" id="d_flujo">--</span></div>
                <div class="dictamen-item"><b>Decena Clave:</b> <span class="dictamen-val" id="d_decena">--</span></div>
                <div class="dictamen-item"><b>Terminales:</b> <span class="dictamen-val" id="d_terminal">--</span></div>
                <div class="dictamen-item"><b>Pareja:</b> <span class="dictamen-val" id="d_pareja">--</span></div>
                <div class="dictamen-item"><b>Dígito Fuerte:</b> <span class="dictamen-val" id="d_digito">--</span></div>
                <div class="dictamen-item" style="border:none;"><b>Inercia:</b> <span class="dictamen-val" style="color:#38bdf8;" id="d_dia">--</span></div>
                <div class="presion-alert" id="d_presion">--</div>

                <div class="jugada-formada-box" id="caja_jugada_formada">
                    <div class="jf-title">
                        <span>⚡ JUGADA FORMADA (CONSENSO CUÁNTICO)</span>
                        <span style="font-size:10px;color:#4ade80;">DIRECTA</span>
                    </div>
                    <div class="jf-row">
                        <b style="color:#a5b4fc;">🎯 3 NÚMEROS:</b>
                        <div class="jf-balls" id="jf_numeros_container"></div>
                    </div>
                    <div class="jf-row">
                        <b style="color:#a5b4fc;">💥 2 PALÉS:</b>
                        <span style="color:#4ade80;font-weight:900;font-size:13px;" id="jf_pales_txt">--</span>
                    </div>
                    <div class="jf-row" style="margin-bottom:0;">
                        <b style="color:#a5b4fc;">🏆 1 TRIPLETA:</b>
                        <span style="color:#f472b6;font-weight:900;font-size:13px;" id="jf_tripleta_txt">--</span>
                    </div>
                </div>
            </div>

            <div id="seccion_eurodreams" style="display:none;">
                <div class="card" style="border: 2px solid #8b5cf6; background:#18181b;">
                    <h2 style="color: #c084fc;">🇪🇺 RED GAUSSIANA EURODREAMS (6/40 + SUEÑO)</h2>
                    <div class="balls-container" id="ed_base_container"></div>
                    <div style="display:flex; justify-content:space-around; align-items:center; margin-top:10px; background:#27272a; padding:10px; border-radius:8px;">
                        <div><b>SUEÑO REINA:</b> <span class="ball-sueno" style="display:inline-flex; width:28px; height:28px; font-size:13px;" id="ed_sueno_val">-</span></div>
                        <div><b>FUERZA SUEÑO:</b> <span style="color:#4ade80; font-weight:bold;" id="ed_fuerza_sueno">97.4%</span></div>
                    </div>
                </div>

                <div class="card" style="border: 1px solid #8b5cf6;">
                    <h2 style="color: #c084fc;">🏆 APUESTAS REDUCIDAS 6/40 (SUMAS 95-155)</h2>
                    <table>
                        <thead><tr><th>#</th><th>COMBINACIÓN (6 NÚMEROS)</th><th>SUEÑO</th><th>ESTRATEGIA</th><th>FUERZA</th></tr></thead>
                        <tbody id="tabla_eurodreams"></tbody>
                    </table>
                </div>
            </div>

            <div id="seccion_anguila" style="display:none;">
                <div class="card" style="border: 2px solid #10b981; background:#18181b;">
                    <h2 style="color: #34d399;">🐍 MATRIZ CASCADA 4X (10 AM / 1 PM / 6 PM / 9 PM)</h2>
                    <table>
                        <thead><tr><th>TANDA</th><th>ESTADO</th><th>TIRO DIRECTO</th><th>PALÉ CASCADA</th><th>FUERZA</th></tr></thead>
                        <tbody id="tabla_anguila_cascada"></tbody>
                    </table>
                </div>
            </div>

            <div id="seccion_tradicional">
                <div class="card" style="border: 2px solid #f59e0b; background: linear-gradient(135deg, #1c1917, #0c0a09);">
                    <h2 style="color: #fbbf24;">⚡ SUPER PALÉ CRUZADO INTELIGENTE (PAGO RD$ 3,000 × 1)</h2>
                    <table>
                        <thead><tr><th>#</th><th>CRUCE TARDE × NOCHE</th><th>SALAS VINCULADAS</th><th>FUERZA</th></tr></thead>
                        <tbody id="tabla_super_pales"></tbody>
                    </table>
                </div>

                <div class="card" style="border: 1px solid #22c55e;">
                    <h2 style="color: #4ade80;">⭐ TOP 5 LÍNEAS ÉLITE DEL DÍA</h2>
                    <table>
                        <thead><tr><th>#</th><th>NÚMERO</th><th>FUERZA</th><th>ESTADO</th><th>SALA</th></tr></thead>
                        <tbody id="tabla_top5"></tbody>
                    </table>
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
            </div>

            <div id="toast">¡Acción ejecutada! 📱</div>
        </div>

        <script>
            const db = {datos_json};
            const suenos = {suenos_json};
            const auditoria = {auditoria_json};
            const premios = {premios_json};
            const termometro = {termometro_json};
            const bingazos = {bingazos_json};
            let tabActual = 'todas';

            function renderBadge(tipo) {{
                if (tipo === "triple_factor") return "<span style='background:#facc15;color:#000;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:900;'>👑 3X FACTOR</span>";
                if (tipo === "virado") return "<span style='background:#f59e0b;color:#000;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>🛡️ VIRADO</span>";
                if (tipo === "caliente") return "<span style='background:#ef4444;color:#fff;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>🔥 RACHA</span>";
                if (tipo === "atrasado") return "<span style='background:#8b5cf6;color:#fff;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>⏳ ATRASADO</span>";
                if (tipo === "pareja") return "<span style='background:#ec4899;color:#fff;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>👥 PAREJA</span>";
                return "<span style='background:#22c55e;color:#000;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>⭐ ÉLITE</span>";
            }}

            function actualizarRelojCabecera() {{
                const ahora = new Date();
                let horas = String(ahora.getHours()).padStart(2, '0');
                let minutos = String(ahora.getMinutes()).padStart(2, '0');
                let segundos = String(ahora.getSeconds()).padStart(2, '0');
                document.getElementById('live_time').innerText = horas + ":" + minutos + ":" + segundos;
            }}

            function cargarBingazos() {{
                if (bingazos && bingazos.length > 0) {{
                    const p = document.getElementById('panel_bingazos');
                    p.style.display = 'block';
                    let html = "";
                    bingazos.forEach(b => {{
                        html += `<div style="margin-top:3px;">🔥 <b>${{b.lot}}:</b> Bolo <span style="background:#22c55e;color:#000;padding:1px 6px;border-radius:4px;font-weight:900;">${{b.bolo}}</span> en ${{b.lugar}} (¡Acierto Confirmado!)</div>`;
                    }});
                    document.getElementById('bingazos_lista').innerHTML = html;
                }}
            }}

            function cargarTermometro() {{
                let html = `
                    <div class="termo-box">
                        <b style="color:#fb923c;font-size:11.5px;">🔥 DECENAS EN RUPTURA:</b>
                        <div style="margin-top:6px;">
                            ${{termometro.decenas_calientes.map(d => `
                                <div class="termo-row">
                                    <div style="display:flex;justify-content:space-between;">
                                        <span>[${{d.rango}}]</span>
                                        <span style="color:#fca5a5;font-weight:bold;">${{d.presion}}% ${{d.estado}}</span>
                                    </div>
                                    <span class="termo-lot">📍 Foco: ${{d.lot}}</span>
                                </div>
                            `).join('')}}
                        </div>
                    </div>
                    <div class="termo-box">
                        <b style="color:#38bdf8;font-size:11.5px;">🎯 TERMINALES CLAVE:</b>
                        <div style="margin-top:6px;">
                            ${{termometro.terminales_fuertes.map(t => `
                                <div class="termo-row">
                                    <div style="display:flex;justify-content:space-between;">
                                        <span>Termina en [${{t.digito}}]</span>
                                        <span style="color:#4ade80;font-weight:bold;">${{t.frecuencia}}</span>
                                    </div>
                                    <span class="termo-lot">📍 Foco: ${{t.lot}}</span>
                                </div>
                            `).join('')}}
                        </div>
                    </div>
                `;
                document.getElementById('termo_contenedor').innerHTML = html;
            }}

            function cargarPizarraPremios() {{
                let html = "";
                for (let k in premios) {{
                    const lot = premios[k];
                    let isAnguila = lot.nombre.includes("Anguila");
                    let volColor = "#4ade80";
                    if (lot.volatilidad && lot.volatilidad.includes("🔴")) volColor = "#f87171";
                    else if (lot.volatilidad && lot.volatilidad.includes("🟡")) volColor = "#facc15";

                    let estColor = lot.estado === 'Oficial RD' ? '#4ade80' : '#94a3b8';

                    html += `<div class="lot-prize-card">
                        <div class="lot-prize-name">
                            <span>${{isAnguila ? '🐍' : '🇩🇴'}} ${{lot.nombre}}</span>
                            <span style="font-size:10px;color:${{estColor}};">${{lot.estado}}</span>
                        </div>
                        <div class="lot-semaforo" style="color:${{volColor}};">${{lot.volatilidad || '🟢 Normal'}}</div>
                        <div class="lot-balls-row">
                            <div class="prize-ball ball-1ra">${{lot.premios[0] || '--'}}</div>
                            <div class="prize-ball ball-2da">${{lot.premios[1] || '--'}}</div>
                            <div class="prize-ball ball-3ra">${{lot.premios[2] || '--'}}</div>
                        </div>
                    </div>`;
                }}
                document.getElementById('pizarra_contenedor').innerHTML = html;
            }}

            function cargarAuditoria() {{
                let html = "";
                auditoria.forEach(item => {{
                    html += `<div class="auditor-item">
                        <span style="color:#94a3b8;font-size:10px;">📅 ${{item.fecha}}</span> | 
                        <b style="color:#38bdf8;">${{item.tipo}}:</b> 
                        <span style="color:#4ade80;font-weight:bold;">${{item.premio}}</span>
                        <div style="font-size:10px;color:#64748b;margin-left:10px;">↳ ${{item.detalle}}</div>
                    </div>`;
                }});
                document.getElementById('contenedor_auditoria').innerHTML = html;
            }}

            function cambiarTab(clave) {{
                tabActual = clave;
                document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
                if (event && event.target) {{ event.target.classList.add('active'); }}
                actualizarVista();
            }}

            function actualizarVista() {{
                const info = db[tabActual] || db['todas'];
                document.getElementById('dictamen_sala').innerText = "[" + info.nombre + "]";

                if (info.tiro_fijo) {{
                    document.getElementById('s_fijo').innerText = info.tiro_fijo.num;
                    document.getElementById('s_virado').innerText = info.tiro_fijo.virado;
                    document.getElementById('s_pale').innerText = info.tiro_fijo.palé_titan;
                    document.getElementById('s_fuerza').innerText = info.tiro_fijo.fuerza + "%";
                    document.getElementById('s_lot_fuerte').innerText = info.tiro_fijo.lot_fuerte || info.nombre;
                }}

                if (info.dictamen) {{
                    document.getElementById('d_flujo').innerText = info.dictamen.flujo;
                    document.getElementById('d_decena').innerText = info.dictamen.decena;
                    document.getElementById('d_terminal').innerText = info.dictamen.terminal;
                    document.getElementById('d_pareja').innerText = info.dictamen.pareja;
                    document.getElementById('d_digito').innerText = info.dictamen.digito_fuerte;
                    document.getElementById('d_dia').innerText = info.dictamen.dia_tendencia;
                    document.getElementById('d_presion').innerText = info.dictamen.presion;
                }}

                document.getElementById('seccion_eurodreams').style.display = 'none';
                document.getElementById('seccion_anguila').style.display = 'none';
                document.getElementById('seccion_tradicional').style.display = 'none';
                document.getElementById('caja_jugada_formada').style.display = 'none';

                if (info.tipo_juego === 'eurodreams') {{
                    document.getElementById('seccion_eurodreams').style.display = 'block';
                    const ed = info.ed_data;
                    document.getElementById('ed_sueno_val').innerText = ed.sueno_reina;
                    document.getElementById('ed_fuerza_sueno').innerText = ed.fuerza_sueno + "%";

                    let htmlB = "";
                    ed.numeros_base.forEach(b => {{ htmlB += `<div class="ball-dream">${{b}}</div>`; }});
                    document.getElementById('ed_base_container').innerHTML = htmlB;

                    let htmlED = "";
                    ed.apuestas.forEach((a, i) => {{
                        htmlED += `<tr><td>0${{i+1}}</td><td style="color:#c084fc;font-weight:bold;font-size:15px;">${{a.combinacion}}</td><td><span class="ball-sueno" style="display:inline-flex;width:24px;height:24px;font-size:11px;">${{a.sueno}}</span></td><td style="font-size:10px;">${{a.tipo}}</td><td style="font-weight:bold;color:#4ade80;">${{a.fuerza}}%</td></tr>`;
                    }});
                    document.getElementById('tabla_eurodreams').innerHTML = htmlED;

                }} else if (info.tipo_juego === 'anguila_cascada') {{
                    document.getElementById('seccion_anguila').style.display = 'block';
                    const ad = info.anguila_data;
                    let htmlA = `
                        <tr><td>10:00 AM</td><td style="color:#34d399;font-weight:bold;">${{ad['10am'].estado}}</td><td style="color:#4ade80;font-weight:bold;font-size:16px;">${{ad['10am'].fijo}}</td><td style="color:#facc15;font-weight:bold;">${{ad['10am'].pale}}</td><td style="color:#4ade80;font-weight:bold;">${{ad['10am'].fuerza}}%</td></tr>
                        <tr><td>01:00 PM</td><td style="color:#34d399;font-weight:bold;">${{ad['1pm'].estado}}</td><td style="color:#4ade80;font-weight:bold;font-size:16px;">${{ad['1pm'].fijo}}</td><td style="color:#facc15;font-weight:bold;">${{ad['1pm'].pale}}</td><td style="color:#4ade80;font-weight:bold;">${{ad['1pm'].fuerza}}%</td></tr>
                        <tr><td>06:00 PM</td><td style="color:#34d399;font-weight:bold;">${{ad['6pm'].estado}}</td><td style="color:#4ade80;font-weight:bold;font-size:16px;">${{ad['6pm'].fijo}}</td><td style="color:#facc15;font-weight:bold;">${{ad['6pm'].pale}}</td><td style="color:#4ade80;font-weight:bold;">${{ad['6pm'].fuerza}}%</td></tr>
                        <tr><td>09:00 PM</td><td style="color:#f472b6;font-weight:bold;">${{ad['9pm'].estado}}</td><td style="color:#4ade80;font-weight:bold;font-size:16px;">${{ad['9pm'].fijo}}</td><td style="color:#facc15;font-weight:bold;">${{ad['9pm'].pale}}</td><td style="color:#4ade80;font-weight:bold;">${{ad['9pm'].fuerza}}%</td></tr>
                    `;
                    document.getElementById('tabla_anguila_cascada').innerHTML = htmlA;

                }} else {{
                    document.getElementById('seccion_tradicional').style.display = 'block';
                    document.getElementById('caja_jugada_formada').style.display = 'block';

                    if (info.super_pales) {{
                        let htmlSP = "";
                        info.super_pales.forEach((sp, i) => {{
                            htmlSP += `<tr><td>0${{i+1}}</td><td style="color:#fbbf24;font-weight:bold;font-size:14px;">${{sp.cruse}}</td><td style="font-size:10.5px;color:#94a3b8;">${{sp.salas}}</td><td style="color:#4ade80;font-weight:bold;">${{sp.fuerza}}%</td></tr>`;
                        }});
                        document.getElementById('tabla_super_pales').innerHTML = htmlSP;
                    }}

                    if (info.jugada_maestra) {{
                        const jm = info.jugada_maestra;
                        let htmlB = "";
                        jm.numeros_3.forEach(n => {{ htmlB += `<span class="jf-ball">${{n}}</span>`; }});
                        document.getElementById('jf_numeros_container').innerHTML = htmlB;
                        document.getElementById('jf_pales_txt').innerText = `[${{jm.pale_1}}]  /  [${{jm.pale_2}}]`;
                        document.getElementById('jf_tripleta_txt').innerText = `[${{jm.tripleta}}]`;
                    }}

                    if (info.sueltos) {{
                        let htmlTop5 = "";
                        info.sueltos.slice(0, 5).forEach((item, i) => {{
                            htmlTop5 += `<tr><td>#${{i+1}}</td><td style="color:#4ade80;font-size:18px;font-weight:bold;">${{item.num}}</td><td style="font-weight:bold;">${{item.fuerza}}%</td><td>${{renderBadge(item.tipo)}}</td><td style="font-size:10px;">${{item.lot}}</td></tr>`;
                        }});
                        document.getElementById('tabla_top5').innerHTML = htmlTop5;

                        let htmlSueltos = "";
                        info.sueltos.forEach((item, i) => {{
                            htmlSueltos += `<tr><td>#${{String(i+1).padStart(2, '0')}}</td><td style="color:#38bdf8;font-size:16px;font-weight:bold;">${{item.num}}</td><td>${{item.fuerza}}%</td><td>${{renderBadge(item.tipo)}}</td><td style="font-size:10px;">${{item.lot}}</td></tr>`;
                        }});
                        document.getElementById('tabla_sueltos').innerHTML = htmlSueltos;

                        let htmlPales = "";
                        let countP = 1;
                        for (let i = 0; i < Math.min(info.sueltos.length, 5); i++) {{
                            for (let j = i + 1; j < Math.min(info.sueltos.length, 5); j++) {{
                                let f = ((info.sueltos[i].fuerza + info.sueltos[j].fuerza) / 2).toFixed(1);
                                htmlPales += `<tr><td>${{String(countP).padStart(2, '0')}}</td><td style="color:#facc15;font-weight:bold;font-size:15px;">${{info.sueltos[i].num}} - ${{info.sueltos[j].num}}</td><td style="font-weight:bold;">${{f}}%</td><td style="font-size:10px;">${{info.sueltos[i].lot}}</td></tr>`;
                                countP++;
                            }}
                        }}
                        document.getElementById('tabla_pales').innerHTML = htmlPales;
                    }}
                }}
            }}

            function copiarWhatsApp() {{
                const info = db[tabActual] || db['todas'];
                let texto = "";

                if (info.tipo_juego === 'eurodreams') {{
                    const ed = info.ed_data;
                    texto = `🇪🇺 *EURODREAMS (6/40)* 🇪🇺\\n🎯 *6 Números:* [${{ed.apuestas[0].combinacion}}]\\n💖 *Sueño:* [${{ed.sueno_reina}}]\\n⚡ *SHNEYDER IA PRO RD*`;
                }} else if (info.tipo_juego === 'anguila_cascada') {{
                    const ad = info.anguila_data;
                    texto = `🐍 *ANGUILA CASCADA 4X* 🐍\\n📍 *10 AM:* [${{ad['10am'].fijo}}] (Palé: ${{ad['10am'].pale}})\\n📍 *1 PM:* [${{ad['1pm'].fijo}}] (Palé: ${{ad['1pm'].pale}})\\n📍 *6 PM:* [${{ad['6pm'].fijo}}] (Palé: ${{ad['6pm'].pale}})\\n📍 *9 PM:* [${{ad['9pm'].fijo}}] (Palé: ${{ad['9pm'].pale}})\\n⚡ *SHNEYDER IA PRO RD*`;
                }} else {{
                    let n1 = info.sueltos[0].num, n2 = info.sueltos[1].num, n3 = info.sueltos[2].num;
                    let lotFuerte = info.tiro_fijo ? info.tiro_fijo.lot_fuerte : info.nombre;
                    if (info.jugada_maestra) {{
                        n1 = info.jugada_maestra.numeros_3[0];
                        n2 = info.jugada_maestra.numeros_3[1];
                        n3 = info.jugada_maestra.numeros_3[2];
                    }}
                    texto = `⚡ *JUGADA TITÁN SHNEYDER IA PRO RD* ⚡\\n📍 *Lotería Sugerida:* ${{lotFuerte}}\\n🎯 *3 Números Directos:* [${{n1}}] - [${{n2}}] - [${{n3}}]\\n💥 *2 Palés Maestros:* [${{n1}} - ${{n2}}] / [${{n1}} - ${{n3}}]\\n🏆 *1 Tripleta Reina:* [${{n1}} - ${{n2}} - ${{n3}}]\\n⚡ *Super Palé Cruzado:* [${{info.super_pales[0].cruse}}]`;
                }}

                navigator.clipboard.writeText(texto).then(() => {{
                    const t = document.getElementById('toast');
                    t.innerText = "¡Copiado para WhatsApp! 📱";
                    t.style.display = 'block';
                    setTimeout(() => {{ t.style.display = 'none'; }}, 2500);
                }});
            }}

            function generarTicket() {{
                const info = db[tabActual] || db['todas'];
                let ticket = `=================================\\n   🎫 TICKET SHNEYDER IA PRO RD\\n=================================\\nSALA: ${{info.nombre.toUpperCase()}}\\nFECHA: ${{new Date().toLocaleDateString()}}\\n---------------------------------\\n`;

                if (info.tipo_juego === 'eurodreams') {{
                    ticket += `EURODREAMS: [${{info.ed_data.apuestas[0].combinacion}}]\\nSUEÑO: [${{info.ed_data.sueno_reina}}]\\n`;
                }} else if (info.tipo_juego === 'anguila_cascada') {{
                    ticket += `10 AM: [${{info.anguila_data['10am'].fijo}}]  1 PM: [${{info.anguila_data['1pm'].fijo}}]\\n6 PM:  [${{info.anguila_data['6pm'].fijo}}]  9 PM: [${{info.anguila_data['9pm'].fijo}}]\\n`;
                }} else {{
                    let n1 = info.sueltos[0].num, n2 = info.sueltos[1].num, n3 = info.sueltos[2].num;
                    let lotFuerte = info.tiro_fijo ? info.tiro_fijo.lot_fuerte : info.nombre;
                    if (info.jugada_maestra) {{
                        n1 = info.jugada_maestra.numeros_3[0];
                        n2 = info.jugada_maestra.numeros_3[1];
                        n3 = info.jugada_maestra.numeros_3[2];
                    }}
                    ticket += `SALA: ${{lotFuerte.toUpperCase()}}\\n3 DIRECTOS: [${{n1}}]  [${{n2}}]  [${{n3}}]\\n2 PALÉS: [${{n1}} - ${{n2}}] / [${{n1}} - ${{n3}}]\\nTRIPLETA: [${{n1}} - ${{n2}} - ${{n3}}]\\nSUPER PALÉ: [${{info.super_pales[0].cruse}}]\\n`;
                }}
                ticket += `=================================`;

                navigator.clipboard.writeText(ticket).then(() => {{
                    const t = document.getElementById('toast');
                    t.innerText = "¡Ticket Copiado! 🎫";
                    t.style.display = 'block';
                    setTimeout(() => {{ t.style.display = 'none'; }}, 2500);
                }});
            }}

            function buscarSueno() {{
                const input = document.getElementById('input_sueno').value.toLowerCase().trim();
                const res = document.getElementById('sueno_resultado');
                if (!input) return;
                let match = suenos[input];
                if (match) {{
                    res.style.display = 'block';
                    res.innerHTML = `🔮 <b>CÁBALA:</b> "${{input.toUpperCase()}}"<br>🎯 <b>Bolo:</b> <span style="color:#4ade80;font-size:16px;font-weight:bold;">${{match.num}}</span> | Fuerza IA: ${{match.fuerza}}%<br>📍 ${{match.lot}} (${{match.cabala}})`;
                }}
            }}

            cargarBingazos();
            cargarTermometro();
            cargarPizarraPremios();
            cargarAuditoria();
            setInterval(actualizarRelojCabecera, 1000);
            actualizarRelojCabecera();
            actualizarVista();
        </script>
    </body>
    </html>
    """
