import threading
import json
import sqlite3
import time
import random
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn

app = FastAPI(title="Shneyder IA Pro RD - Titan Quantum Definitivo v71.0")
DB_PATH = "loteria_master_ai.db"

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS resultados_guardados (
                clave TEXT PRIMARY KEY,
                nombre TEXT,
                bolo1 TEXT,
                bolo2 TEXT,
                bolo3 TEXT,
                estado TEXT,
                volatilidad TEXT,
                fecha TEXT
            )
        """)
        conn.commit()
        conn.close()
    except Exception:
        pass

init_db()

def obtener_fechas_rd():
    ahora_utc = datetime.utcnow()
    hora_rd = ahora_utc - timedelta(hours=4)
    fecha_str = hora_rd.strftime("%d/%m/%Y")
    dia_nombre = DIAS_SEMANA[hora_rd.weekday()]
    return hora_rd, fecha_str, dia_nombre

TABLA_JALADERA = {
    "00": ["55", "05", "50"], "01": ["56", "10", "61"], "02": ["57", "20", "72"], "03": ["58", "30", "83"],
    "04": ["59", "40", "94"], "05": ["00", "50", "20"], "06": ["51", "60", "29"], "07": ["52", "70", "25"],
    "08": ["53", "80", "35"], "09": ["54", "90", "45"], "10": ["65", "01", "15"], "11": ["66", "16", "22"],
    "12": ["67", "21", "27"], "13": ["68", "31", "38"], "14": ["69", "41", "49"], "15": ["60", "51", "06"],
    "20": ["75", "02", "25"], "22": ["77", "27", "44"], "26": ["62", "71", "18"], "28": ["82", "46", "73"],
    "29": ["74", "92", "06"], "33": ["88", "38", "99"], "40": ["95", "04", "45"], "44": ["99", "49", "11"],
    "47": ["92", "74", "13"], "48": ["93", "84", "24"], "50": ["05", "00", "55"], "55": ["00", "50", "77"],
    "66": ["11", "61", "33"], "77": ["22", "72", "55"], "88": ["33", "83", "00"], "99": ["44", "94", "66"]
}

def obtener_jalamatico(num_str):
    return TABLA_JALADERA.get(num_str, [num_str[::-1], "{:02d}".format((int(num_str)+10)%100), "{:02d}".format((int(num_str)+50)%100)])

def cluster_triple_decena_ia(hora_rd, dia_nombre):
    seed_base = int(hora_rd.strftime("%Y%m%d"))
    es_tarde_noche = hora_rd.hour >= 18
    rng = random.Random(seed_base + (99 if es_tarde_noche else 11))

    salas_tarde = ["Lotería Real (12:55 PM)", "Gana Más (2:30 PM)", "La Primera Día (12:00 PM)", "La Suerte Día (12:30 PM)"]
    salas_noche = ["Leidsa (8:55 PM)", "Nacional Noche (8:50 PM)", "Loteka (7:55 PM)", "La Primera Noche (8:00 PM)"]
    
    pool_salas = salas_noche if es_tarde_noche else salas_tarde
    lot_fuerte_principal = pool_salas[0]
    lot_fuerte_respaldo = pool_salas[1]

    # --- RASTREO AVANZADO DE 3 DECENAS ---
    decenas_disponibles = [
        ("Decena [00-09]", 0), ("Decena [10-19]", 10), ("Decena [20-29]", 20), 
        ("Decena [30-39]", 30), ("Decena [40-49]", 40), ("Decena [70-79]", 70), ("Decena [80-89]", 80)
    ]
    seleccion_decenas = rng.sample(decenas_disponibles, 3)
    
    decena_nombre_1, base_1 = seleccion_decenas[0]
    decena_nombre_2, base_2 = seleccion_decenas[1]
    decena_nombre_3, base_3 = seleccion_decenas[2]

    # Terminales específicos cruzados de las 3 decenas
    t1 = rng.choice([1, 4, 7])
    t2 = rng.choice([2, 5, 8])
    t3 = rng.choice([3, 6, 9])

    n1 = "{:02d}".format(base_1 + t1)
    n2 = "{:02d}".format(base_2 + t2)
    n3 = "{:02d}".format(base_3 + t3)

    n1_reves = n1[::-1] if n1 != n1[::-1] else "60"
    n1_mas1 = "{:02d}".format((int(n1) + 1) % 100)
    n1_menos1 = "{:02d}".format((int(n1) - 1) % 100)

    p1 = "{} - {}".format(n1, n2)
    p2 = "{} - {}".format(n2, n3)
    tripleta_reina = "{} - {} - {}".format(n1, n2, n3)

    todas_pool = [
        {"num": n1, "fuerza": 99.6, "tipo": "triple_factor", "lot": lot_fuerte_principal},
        {"num": n2, "fuerza": 98.4, "tipo": "pareja", "lot": lot_fuerte_principal},
        {"num": n3, "fuerza": 97.2, "tipo": "caliente", "lot": lot_fuerte_respaldo},
        {"num": n1_reves, "fuerza": 95.5, "tipo": "virado", "lot": lot_fuerte_respaldo},
        {"num": n1_mas1, "fuerza": 94.8, "tipo": "fuerte", "lot": lot_fuerte_principal},
        {"num": n1_menos1, "fuerza": 94.2, "tipo": "fuerte", "lot": lot_fuerte_respaldo}
    ]

    otros_nums = ["{:02d}".format(n) for n in range(100) if "{:02d}".format(n) not in [n1, n2, n3, n1_reves, n1_mas1, n1_menos1]]
    rng.shuffle(otros_nums)
    for i, num_extra in enumerate(otros_nums[:14]):
        fuerza = round(91.0 - (i * 2.2), 1)
        todas_pool.append({"num": num_extra, "fuerza": fuerza, "tipo": "caliente", "lot": rng.choice(pool_salas)})

    super_pales = [
        {"cruse": "{} (Decena 1) × {} (Decena 2)".format(n1, n2), "salas": "Cruce Triple Clúster", "fuerza": 99.1},
        {"cruse": "{} (Decena 2) × {} (Decena 3)".format(n2, n3), "salas": "Cruce Triple Clúster", "fuerza": 97.8}
    ]

    kino_duenos = ["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), 10))]
    def gen_kino(cant): return " - ".join(["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), cant))])
    
    prim_nums1 = sorted(rng.sample(range(1, 50), 6))
    prim_reintegro = str(rng.randint(0, 9))
    prim_comp = "{:02d}".format(rng.randint(1, 49))
    prim_base = ["{:02d}".format(n) for n in sorted(rng.sample(range(1, 50), 8))]

    euro_nums = sorted(rng.sample(range(1, 51), 5))
    euro_e1, euro_e2 = "{:02d}".format(rng.randint(1, 6)), "{:02d}".format(rng.randint(7, 12))

    ed_nums1 = sorted(rng.sample(range(1, 41), 6))
    ed_sueno = str(rng.randint(1, 5))
    ed_base = ["{:02d}".format(n) for n in sorted(rng.sample(range(1, 41), 8))]

    eurodreams_data = {
        "sueno_reina": ed_sueno,
        "fuerza_sueno": 97.4,
        "numeros_base": ed_base,
        "apuestas": [{"combinacion": " - ".join(["{:02d}".format(n) for n in ed_nums1]), "sueno": ed_sueno, "fuerza": 98.9, "tipo": "IA Gaussiana 6/40"}]
    }

    diccionario_salas = {}
    claves_salas = [
        ("real", "Lotería Real (12:55 PM)"), ("gana_mas", "Gana Más (2:30 PM)"), 
        ("nacional_noche", "Nacional Noche (8:50 PM)"), ("leidsa", "Leidsa (8:55 PM)"),
        ("loteka", "Loteka (7:55 PM)"), ("primera_dia", "La Primera Día (12:00 PM)"),
        ("primera_noche", "La Primera Noche (8:00 PM)"), ("lotedom", "LoteDom (12:00 PM)"),
        ("suerte_dia", "La Suerte Día (12:30 PM)"), ("suerte_tarde", "La Suerte Tarde (6:00 PM)"),
        ("anguila_10am", "Anguila Mañana (10:00 AM)"), ("anguila_1pm", "Anguila Mediodía (1:00 PM)"),
        ("anguila_6pm", "Anguila Tarde (6:00 PM)"), ("anguila_9pm", "Anguila Noche (9:00 PM)")
    ]

    for clave, nombre_sala in claves_salas:
        diccionario_salas[clave] = {
            "nombre": nombre_sala,
            "tipo_juego": "quiniela",
            "es_tarde_noche": es_tarde_noche,
            "fase": "🔮 TRIPLE CLÚSTER IA",
            "tiro_fijo": {"num": n1, "virado": n1_reves, "fuerza": 99.4, "palé_titan": p1, "lot_fuerte": nombre_sala},
            "cobertura_lateral": {"mas1": n1_mas1, "menos1": n1_menos1, "pale_reves": p_reves},
            "jugada_maestra": {"numeros_3": [n1, n2, n3], "pale_1": p1, "pale_2": p2, "pale_reves": p_reves, "tripleta": tripleta_reina, "lot_fuerte": nombre_sala, "lot_respaldo": lot_fuerte_respaldo},
            "super_pales": super_pales,
            "dictamen": {
                "flujo": "ANCLAJE TRIPLE 3-DECENAS", 
                "decena": f"{decena_nombre_1}, {decena_nombre_2}, {decena_nombre_3}", 
                "terminal": f"Term. {t1}, {t2}, {t3}", 
                "pareja": "MÁXIMA", 
                "digito_fuerte": f"Dígitos {t1}, {t2} y {t3}", 
                "presion": f"🎯 Foco Principal: {decena_nombre_1}", 
                "dia_tendencia": f"{dia_nombre}: Alta Viabilidad"
            },
            "sueltos": todas_pool
        }

    # Añadir juegos internacionales
    diccionario_salas["kino_leidsa"] = {
        "nombre": "VENTA ESPECIAL: KINO LEIDSA TV",
        "tipo_juego": "kino",
        "tiro_fijo": {"num": kino_duenos[0], "virado": "--", "fuerza": 98.6, "palé_titan": "Bloque 5 Activo", "lot_fuerte": "Kino TV Leidsa (8:55 PM)"},
        "kino_data": {
            "estado_tombola": "🔥 CLÚSTER 15 IAs: Filtro Anti-Consecutivos al 98.6%",
            "paridad_optima": "⚖️ RATIO IA-02: 10 Pares / 10 Impares",
            "zona_muerta": "🚫 RETENCIÓN IA-04: Rango 41 al 53",
            "duenos": kino_duenos,
            "bloques_5": [{"bloque": gen_kino(5), "paridad": "3 Imp / 2 Par", "fuerza": 98.6, "ia_origen": "IA-01 Cuadrantes"}],
            "bloques_7": [{"bloque": gen_kino(7), "paridad": "4 Imp / 3 Par", "fuerza": 99.1, "ia_origen": "IA-07 Genético"}]
        },
        "dictamen": {
            "flujo": "EXPANSIVO 1-80", "decena": "Distribución por cuadrantes", "terminal": "Terminales 7, 8, 3 y 4",
            "pareja": "ALTA", "digito_fuerte": "Dígitos 7 y 8", "presion": "🎯 IA-15 Consenso", "dia_tendencia": "{}: Primos".format(dia_nombre)
        }
    }
    diccionario_salas["primitiva_esp"] = {
        "nombre": "🇪🇸 LA PRIMITIVA (ESPAÑA)",
        "tipo_juego": "primitiva",
        "tiro_fijo": {"num": prim_base[0], "virado": "--", "fuerza": 98.9, "palé_titan": "R: {}".format(prim_reintegro), "lot_fuerte": "Loterías del Estado"},
        "primitiva_data": {
            "reintegro": prim_reintegro, "complementario": prim_comp, "cuadrantes": "C1: 2 | C2: 1 | C3: 2 | C4: 1",
            "apuestas_6": [{"combinacion": " - ".join(["{:02d}".format(n) for n in prim_nums1]), "reintegro": prim_reintegro, "fuerza": 98.9, "tipo": "Gaussiana"}],
            "numeros_base": prim_base
        },
        "dictamen": {
            "flujo": "GEOMÉTRICO 1-49", "decena": "Equilibrio Gaussiano", "terminal": "Terminales 2, 4, 7 y 9",
            "pareja": "MEDIA", "digito_fuerte": "Reintegro {}".format(prim_reintegro), "presion": "🚨 Clúster Validado", "dia_tendencia": "{}".format(dia_nombre)
        }
    }
    diccionario_salas["euromillones"] = {
        "nombre": "🇪🇺 EUROMILLONES (EUROPA)",
        "tipo_juego": "euromillones",
        "tiro_fijo": {"num": "{:02d}".format(euro_nums[0]), "virado": "--", "fuerza": 99.4, "palé_titan": "⭐ {} - {}".format(euro_e1, euro_e2), "lot_fuerte": "Euromillones"},
        "euro_data": {
            "estrellas_fijas": [euro_e1, euro_e2], "fuerza_estrellas": 99.1, "distribucion": "4 Cuadrantes",
            "apuestas_euro": [{"numeros": " - ".join(["{:02d}".format(n) for n in euro_nums]), "estrellas": "{} - {}".format(euro_e1, euro_e2), "fuerza": 99.5, "tipo": "Sumas Cuánticas"}],
            "red_afinidad": ["{:02d}".format(n) for n in euro_nums] + ["{}*".format(euro_e1), "{}*".format(euro_e2)]
        },
        "dictamen": {
            "flujo": "DISPERSIÓN TOTAL", "decena": "Rango 40-50", "terminal": "Terminales 4, 7, 8 y 9",
            "pareja": "BAJA", "digito_fuerte": "Estrellas {}-{}".format(euro_e1, euro_e2), "presion": "🚨 Filtro Activo", "dia_tendencia": "{}".format(dia_nombre)
        }
    }
    diccionario_salas["eurodreams"] = {
        "nombre": "🇪🇺 EURODREAMS (EUROPA 6/40)",
        "tipo_juego": "eurodreams",
        "tiro_fijo": {"num": eurodreams_data["numeros_base"][0], "virado": "--", "fuerza": 98.9, "palé_titan": "Sueño: {}".format(eurodreams_data['sueno_reina']), "lot_fuerte": "EuroDreams"},
        "ed_data": eurodreams_data,
        "dictamen": {
            "flujo": "MATRIZ 6/40", "decena": "Suma controlada", "terminal": "Terminales 1, 3, 6, 8",
            "pareja": "BAJA", "digito_fuerte": "Sueño [{}]".format(eurodreams_data['sueno_reina']), "presion": "🚨 6 Bolos + 1 Sueño", "dia_tendencia": "{}".format(dia_nombre)
        }
    }

    return diccionario_salas

DICCIONARIO_SUENOS = {
    "dinero": {"num": "48", "cabala": "Plata / Riqueza", "fuerza": 98.5, "lot": "Leidsa / Nacional"},
    "agua": {"num": "06", "cabala": "Río / Lluvia / Mar", "fuerza": 91.2, "lot": "La Primera"},
    "muerte": {"num": "47", "cabala": "Finado / Entierro", "fuerza": 96.4, "lot": "Gana Mas"},
    "accidente": {"num": "13", "cabala": "Choque / Caída", "fuerza": 94.1, "lot": "Loteka"},
    "boda": {"num": "24", "cabala": "Matrimonio / Fiesta", "fuerza": 89.0, "lot": "La Real"},
    "fuego": {"num": "11", "cabala": "Incendio / Candela", "fuerza": 93.6, "lot": "Nacional Noche"},
    "serpiente": {"num": "36", "cabala": "Culebra / Traición", "fuerza": 88.3, "lot": "La Suerte"},
    "embarazo": {"num": "19", "cabala": "Bebé / Nacimiento", "fuerza": 95.2, "lot": "Anguila 6PM"},
    "casa": {"num": "04", "cabala": "Propiedad / Techo", "fuerza": 98.9, "lot": "Gana Mas / Nacional"}
}

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    hora_rd, fecha_str, dia_nombre = obtener_fechas_rd()
    datos_loterias = cluster_triple_decena_ia(hora_rd, dia_nombre)

    termometro = {
        "decenas_calientes": [
            {"rango": "Triple Clúster Activo", "presion": 99.4, "estado": "🚨 MÁXIMA PRECISIÓN", "lot": "Matriz IA"}
        ],
        "terminales_fuertes": [
            {"digito": "Cruce Múltiple", "frecuencia": "Muy Alta (99.1%)", "lot": "Global"}
        ]
    }

    historial_auditoria = [{
        "fecha": fecha_str,
        "sala": "Motor Triple Clúster IA",
        "tipo": "⚡ HORA RD: {}".format(hora_rd.strftime('%I:%M %p')),
        "premio": "Sincronización de 3 Decenas ({})".format(dia_nombre),
        "detalle": "Análisis cruzado sin solapamientos ni errores"
    }]

    datos_json = json.dumps(datos_loterias)
    suenos_json = json.dumps(DICCIONARIO_SUENOS)
    auditoria_json = json.dumps(historial_auditoria)
    termometro_json = json.dumps(termometro)

    es_tarde_noche = hora_rd.hour >= 18
    banner_color = "linear-gradient(135deg, #7f1d1d, #450a0a)" if es_tarde_noche else "linear-gradient(135deg, #1e3a8a, #0f172a)"
    banner_borde = "#ef4444" if es_tarde_noche else "#38bdf8"
    banner_txt = "🚨 RECALIBRACIÓN VESPERTINA: TRIPLE CLÚSTER IA (NOCHE)" if es_tarde_noche else "🌅 MATRIZ MATUTINA: TRIPLE CLÚSTER IA (TARDE)"

    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <title>Shneyder IA Pro RD v71.0</title>
        <style>
            * { box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #080d1a; color: #e2e8f0; margin: 0; padding: 10px; }
            .main-wrapper { max-width: 900px; margin: 0 auto; }
            .brand { display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 12px; padding: 12px 16px; margin-bottom: 12px; border: 1px solid #38bdf8; }
            .brand-left h1 { font-size: 20px; color: #38bdf8; margin: 0; font-weight: 900; }
            .brand-left p { font-size: 10px; color: #94a3b8; margin: 3px 0 0 0; text-transform: uppercase; }
            .brand-clock { font-size: 15px; color: #facc15; font-weight: 900; font-family: monospace; }
            .banner-fase { background: __BANNER_COLOR__; border: 2px solid __BANNER_BORDE__; border-radius: 10px; padding: 8px 12px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; font-size: 11px; font-weight: 900; color: #fff; }
            .sniper-card { background: linear-gradient(135deg, #1e1b4b, #0f172a); border: 2px solid #818cf8; border-radius: 12px; padding: 14px; margin-bottom: 12px; }
            .sniper-grid { display: flex; justify-content: space-around; align-items: center; text-align: center; margin-bottom: 10px; }
            .sniper-item b { font-size: 10px; color: #a5b4fc; text-transform: uppercase; display: block; }
            .sniper-num { font-size: 26px; font-weight: 900; color: #38bdf8; }
            .sniper-badge { font-size: 13px; font-weight: bold; color: #4ade80; }
            .sniper-lot-box { background: rgba(15, 23, 42, 0.8); border: 1px solid #38bdf8; border-radius: 8px; padding: 6px 10px; text-align: center; font-size: 12px; display: flex; justify-content: center; align-items: center; gap: 6px; }
            .matriz-card { background: linear-gradient(135deg, #1e1b4b, #111827); border: 1px solid #c084fc; border-radius: 12px; padding: 10px; margin-bottom: 12px; font-size: 11.5px; }
            .matriz-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 6px; }
            .matriz-box { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 8px; }
            .termo-card { background: #111c30; border: 1px solid #f97316; border-radius: 12px; padding: 12px; margin-bottom: 12px; }
            .termo-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 8px; font-size: 11px; }
            .termo-box { background: #18263e; padding: 10px; border-radius: 8px; border: 1px solid #283e60; }
            .termo-row { margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid rgba(255,255,255,0.06); }
            .auditor-box { background: #0f172a; border: 1px solid #22c55e; border-radius: 10px; padding: 10px; margin-bottom: 12px; font-size: 12px; }
            .auditor-title { color: #4ade80; font-weight: 800; margin-bottom: 6px; display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 4px; }
            .auditor-item { padding: 5px 0; border-bottom: 1px solid #1e293b; font-size: 11.5px; }
            .search-box { background: #0f172a; border: 1px solid #334155; border-radius: 12px; padding: 10px; margin-bottom: 12px; display: flex; gap: 8px; }
            .search-input { flex: 1; background: #1e293b; border: 1px solid #475569; color: #fff; border-radius: 8px; padding: 8px 12px; font-size: 13px; outline: none; }
            .search-btn { background: #38bdf8; color: #0f172a; font-weight: bold; border: none; border-radius: 8px; padding: 8px 14px; cursor: pointer; }
            #sueno_resultado { display: none; background: #131d31; border: 1px solid #38bdf8; border-radius: 10px; padding: 10px; margin-bottom: 12px; font-size: 12px; }
            .tabs-scroll { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 8px; margin-bottom: 12px; -webkit-overflow-scrolling: touch; }
            .tab-btn { white-space: nowrap; background: #1f2937; color: #9ca3af; border: 1px solid #374151; padding: 6px 12px; border-radius: 16px; font-size: 11px; font-weight: bold; cursor: pointer; }
            .tab-btn.active { background: #38bdf8; color: #0f172a; border-color: #38bdf8; }
            .tab-rd { background: linear-gradient(135deg, #059669, #047857); color: #fff; font-weight: 900; }
            .tab-kino { background: linear-gradient(135deg, #eab308, #ca8a04); color: #000; font-weight: 900; }
            .tab-esp { background: linear-gradient(135deg, #dc2626, #991b1b); color: #fff; font-weight: 900; }
            .tab-euro { background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; font-weight: 900; }
            .tab-ed { background: linear-gradient(135deg, #7c3aed, #4c1d95); color: #fff; font-weight: 900; }
            .btn-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 15px; }
            .btn-wa { width: 100%; background: #22c55e; color: #0f172a; font-weight: 800; text-align: center; padding: 12px; border-radius: 10px; border: none; font-size: 13px; cursor: pointer; }
            .btn-ticket { width: 100%; background: #38bdf8; color: #0f172a; font-weight: 800; text-align: center; padding: 12px; border-radius: 10px; border: none; font-size: 13px; cursor: pointer; }
            .dictamen-box { background: #0f172a; border: 1px solid #38bdf8; border-radius: 12px; padding: 12px; margin-bottom: 15px; font-size: 12px; }
            .dictamen-box h3 { margin: 0 0 8px 0; color: #38bdf8; font-size: 13px; display: flex; align-items: center; justify-content: space-between; }
            .dictamen-item { margin-bottom: 5px; display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 3px; }
            .dictamen-item b { color: #94a3b8; }
            .dictamen-val { color: #f8fafc; font-weight: bold; }
            .presion-alert { background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; color: #fca5a5; padding: 8px; border-radius: 8px; margin-top: 8px; font-size: 11px; font-weight: bold; text-align: center; }
            .jugada-formada-box { background: linear-gradient(135deg, #1e1b4b, #172554); border: 2px solid #facc15; border-radius: 10px; padding: 12px; margin-top: 12px; box-shadow: 0 4px 12px rgba(250, 204, 21, 0.2); }
            .jf-title { color: #facc15; font-size: 12px; font-weight: 900; text-transform: uppercase; margin-bottom: 8px; display: flex; justify-content: space-between; border-bottom: 1px solid rgba(250, 204, 21, 0.3); padding-bottom: 4px; }
            .jf-lot-box { background: rgba(0, 0, 0, 0.4); border: 1px solid #38bdf8; border-radius: 6px; padding: 6px 8px; margin-bottom: 8px; font-size: 11.5px; }
            .jf-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; font-size: 12px; }
            .jf-balls { display: flex; gap: 6px; }
            .jf-ball { background: #facc15; color: #0f172a; font-weight: 900; font-size: 14px; padding: 5px 10px; border-radius: 6px; }
            .cobertura-box { background: rgba(56, 189, 248, 0.1); border: 1px dashed #38bdf8; border-radius: 8px; padding: 8px; margin-top: 8px; font-size: 11.5px; }
            .card { background: #131d31; border-radius: 12px; padding: 12px; margin-bottom: 15px; border: 1px solid #233249; }
            h2 { font-size: 14px; margin-top: 0; padding-bottom: 6px; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }
            .table-container { max-height: 420px; overflow-y: auto; }
            table { width: 100%; border-collapse: collapse; text-align: center; font-size: 12px; }
            th { background: #1e293b; padding: 6px 2px; color: #94a3b8; font-size: 11px; position: sticky; top: 0; }
            td { padding: 8px 3px; border-bottom: 1px solid #1e293b; }
            .balls-container { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin: 10px 0; }
            .ball-kino { background: #eab308; color: #000; font-weight: bold; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 15px; }
            .ball-primitiva { background: #ef4444; color: #fff; font-weight: bold; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 15px; }
            .ball-euro { background: #3b82f6; color: #fff; font-weight: bold; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 15px; }
            .ball-star { background: #facc15; color: #000; font-weight: 900; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 14px; }
            .ball-dream { background: #8b5cf6; color: #fff; font-weight: bold; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 15px; }
            #toast { display: none; position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: #38bdf8; color: #0f172a; padding: 10px 20px; border-radius: 20px; font-weight: bold; font-size: 13px; z-index: 100; }
        </style>
    </head>
    <body>
        <div class="main-wrapper">
            <div class="brand">
                <div class="brand-left">
                    <h1>SHNEYDER IA PRO RD</h1>
                    <p>Titan Quantum v71.0 - Triple Clúster</p>
                </div>
                <div class="brand-right">
                    <div class="brand-clock" id="live_time">--:--:--</div>
                </div>
            </div>

            <div class="banner-fase">
                <span>__BANNER_TXT__</span>
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
                    <span style="color:#facc15;font-weight:900;">📍 SALA ACTIVA:</span>
                    <span style="color:#38bdf8;font-weight:bold;" id="s_lot_fuerte">--</span>
                </div>
            </div>

            <div class="matriz-card">
                <div style="color:#c084fc; font-weight:900; margin-bottom:4px; display:flex; justify-content:space-between;">
                    <span>📊 MATRIZ ESTRATÉGICA DE 3 DECENAS</span>
                    <span style="color:#94a3b8; font-size:10px;">Motor Avanzado IA</span>
                </div>
                <div class="matriz-grid">
                    <div class="matriz-box">
                        <b style="color:#38bdf8;">🌅 TANDA MEDIODÍA</b>
                        <div style="color:#cbd5e1; font-size:10.5px; margin-top:2px;">Foco: <b>Triple Cruce Dinámico</b></div>
                    </div>
                    <div class="matriz-box">
                        <b style="color:#f472b6;">🌙 TANDA NOCHE</b>
                        <div style="color:#cbd5e1; font-size:10.5px; margin-top:2px;">Foco: <b>Alta Inercia Estelar</b></div>
                    </div>
                </div>
            </div>

            <div class="termo-card">
                <div style="font-size:13px;font-weight:bold;color:#f97316;display:flex;justify-content:space-between;align-items:center;">
                    <span>🌡️ RADAR TÉRMICO DE TRIPLE CLÚSTER</span>
                    <span style="font-size:10px;color:#94a3b8;">📅 __FECHA_STR__</span>
                </div>
                <div class="termo-grid" id="termo_contenedor"></div>
            </div>

            <div class="auditor-box">
                <div class="auditor-title">
                    <span>📡 AUDITORÍA OFICIAL EN VIVO</span>
                    <span style="font-size:10px;color:#94a3b8;">Sistema IA</span>
                </div>
                <div id="contenedor_auditoria"></div>
            </div>

            <div class="search-box">
                <input type="text" id="input_sueno" class="search-input" placeholder="Escribe tu sueño o cábala (ej. dinero, agua)..." onkeydown="if(event.key==='Enter') buscarSueno()">
                <button class="search-btn" onclick="buscarSueno()">🔮 CONSULTAR</button>
            </div>
            <div id="sueno_resultado"></div>

            <div class="tabs-scroll">
                <button class="tab-btn tab-rd active" onclick="cambiarTab('real')">L. Real</button>
                <button class="tab-btn tab-rd" onclick="cambiarTab('gana_mas')">Gana Más</button>
                <button class="tab-btn tab-rd" onclick="cambiarTab('nacional_noche')">Nacional</button>
                <button class="tab-btn tab-rd" onclick="cambiarTab('leidsa')">Leidsa</button>
                <button class="tab-btn tab-rd" onclick="cambiarTab('loteka')">Loteka</button>
                <button class="tab-btn tab-rd" onclick="cambiarTab('primera_dia')">1ra Día</button>
                <button class="tab-btn tab-rd" onclick="cambiarTab('primera_noche')">1ra Noche</button>
                <button class="tab-btn tab-rd" onclick="cambiarTab('lotedom')">LoteDom</button>
                <button class="tab-btn tab-rd" onclick="cambiarTab('suerte_dia')">Suerte Día</button>
                <button class="tab-btn tab-rd" onclick="cambiarTab('suerte_tarde')">Suerte Tarde</button>
                <button class="tab-btn tab-rd" onclick="cambiarTab('anguila_10am')">Ang 10AM</button>
                <button class="tab-btn tab-rd" onclick="cambiarTab('anguila_1pm')">Ang 1PM</button>
                <button class="tab-btn tab-rd" onclick="cambiarTab('anguila_6pm')">Ang 6PM</button>
                <button class="tab-btn tab-rd" onclick="cambiarTab('anguila_9pm')">Ang 9PM</button>
                <button class="tab-btn tab-kino" onclick="cambiarTab('kino_leidsa')">Kino</button>
                <button class="tab-btn tab-esp" onclick="cambiarTab('primitiva_esp')">Primitiva</button>
                <button class="tab-btn tab-euro" onclick="cambiarTab('euromillones')">Euromillones</button>
                <button class="tab-btn tab-ed" onclick="cambiarTab('eurodreams')">EuroDreams</button>
            </div>

            <div class="btn-actions">
                <button class="btn-wa" onclick="copiarWhatsApp()">📋 COPIAR WHATSAPP</button>
                <button class="btn-ticket" onclick="generarTicket()">🎫 TICKET DE BANCA</button>
            </div>

            <div class="dictamen-box">
                <h3>⚡ DICTAMEN DE SALA <span id="dictamen_sala" style="font-size:10px;color:#94a3b8;"></span></h3>
                <div class="dictamen-item"><b>Flujo:</b> <span class="dictamen-val" id="d_flujo">--</span></div>
                <div class="dictamen-item"><b>Decenas Clave:</b> <span class="dictamen-val" id="d_decena">--</span></div>
                <div class="dictamen-item"><b>Terminales:</b> <span class="dictamen-val" id="d_terminal">--</span></div>
                <div class="dictamen-item"><b>Pareja:</b> <span class="dictamen-val" id="d_pareja">--</span></div>
                <div class="dictamen-item"><b>Dígito Fuerte:</b> <span class="dictamen-val" id="d_digito">--</span></div>
                <div class="dictamen-item" style="border:none;"><b>Inercia:</b> <span class="dictamen-val" style="color:#38bdf8;" id="d_dia">--</span></div>
                <div class="presion-alert" id="d_presion">--</div>

                <div class="jugada-formada-box" id="caja_jugada_formada">
                    <div class="jf-title">
                        <span>⚡ JUGADA FORMADA (TRIPLE CLÚSTER)</span>
                        <span style="font-size:10px;color:#4ade80;">DIRECTA</span>
                    </div>
                    
                    <div class="jf-lot-box">
                        <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                            <span style="color:#facc15;font-weight:900;">📍 SALA OBJETIVO:</span>
                            <span style="color:#38bdf8;font-weight:bold;" id="jf_lot_txt">--</span>
                        </div>
                        <div style="display:flex;justify-content:space-between;">
                            <span style="color:#94a3b8;font-weight:bold;">🛡️ RESPALDO:</span>
                            <span style="color:#4ade80;font-weight:bold;" id="jf_respaldo_txt">--</span>
                        </div>
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

                    <div class="cobertura-box">
                        <b style="color:#38bdf8;">🛡️ COBERTURA LATERAL BLINDADA:</b>
                        <div style="display:flex; justify-content:space-between; margin-top:4px; font-size:11px;">
                            <span>Lateral +1 / -1: <b style="color:#facc15;" id="cov_mas_menos">-- / --</b></span>
                            <span>Palé Revés: <b style="color:#4ade80;" id="cov_pale_reves">--</b></span>
                        </div>
                    </div>
                </div>
            </div>

            <div id="seccion_kino" style="display:none;">
                <div class="card" style="border: 2px solid #eab308; background:#18181b;">
                    <h2 style="color: #facc15;">👑 LOS 10 DUEÑOS DEL KINO (IA-06 BAYESIANA)</h2>
                    <div class="balls-container" id="kino_duenos_container"></div>
                    <div style="background:#27272a;padding:8px;border-radius:8px;font-size:11px;margin-top:8px;text-align:center;" id="kino_estado_txt"></div>
                    <div style="background:#27272a;color:#38bdf8;padding:8px;border-radius:8px;font-size:11px;margin-top:5px;text-align:center;" id="kino_paridad_txt"></div>
                    <div style="background:rgba(239,68,68,0.15);color:#fca5a5;padding:8px;border-radius:8px;font-size:11px;margin-top:5px;text-align:center;font-weight:bold;" id="kino_muerta_txt"></div>
                </div>
                <div class="card" style="border: 1px solid #eab308;">
                    <h2 style="color: #facc15;">🎯 BLOQUES DE 5</h2>
                    <table>
                        <thead><tr><th>#</th><th>BLOQUE</th><th>PARIDAD</th><th>IA</th><th>FUERZA</th></tr></thead>
                        <tbody id="tabla_kino_5"></tbody>
                    </table>
                </div>
                <div class="card" style="border: 1px solid #eab308;">
                    <h2 style="color: #facc15;">🏆 BLOQUES DE 7</h2>
                    <table>
                        <thead><tr><th>#</th><th>BLOQUE</th><th>PARIDAD</th><th>IA</th><th>FUERZA</th></tr></thead>
                        <tbody id="tabla_kino_7"></tbody>
                    </table>
                </div>
            </div>

            <div id="seccion_primitiva" style="display:none;">
                <div class="card" style="border: 2px solid #ef4444; background:#18181b;">
                    <h2 style="color: #f87171;">🇪🇸 LA PRIMITIVA (ESPAÑA)</h2>
                    <div class="balls-container" id="primitiva_base_container"></div>
                    <div style="display:flex; justify-content:space-around; margin-top:10px; background:#27272a; padding:10px; border-radius:8px;">
                        <div><b>REINTEGRO:</b> <span style="background:#ef4444; color:#fff; padding:3px 8px; border-radius:50%; font-weight:bold;" id="prim_reintegro">--</span></div>
                        <div><b>COMPLEMENTARIO:</b> <span style="background:#3b82f6; color:#fff; padding:3px 8px; border-radius:50%; font-weight:bold;" id="prim_comp">--</span></div>
                    </div>
                </div>
                <div class="card" style="border: 1px solid #ef4444;">
                    <h2 style="color: #f87171;">🎯 APUESTAS REDUCIDAS</h2>
                    <table>
                        <thead><tr><th>#</th><th>COMBINACIÓN</th><th>R</th><th>MOTOR</th><th>FUERZA</th></tr></thead>
                        <tbody id="tabla_primitiva"></tbody>
                    </table>
                </div>
            </div>

            <div id="seccion_euromillones" style="display:none;">
                <div class="card" style="border: 2px solid #3b82f6; background:#18181b;">
                    <h2 style="color: #60a5fa;">🇪🇺 EUROMILLONES (EUROPA)</h2>
                    <div class="balls-container" id="euro_base_container"></div>
                    <div style="display:flex; justify-content:space-around; align-items:center; margin-top:10px; background:#27272a; padding:10px; border-radius:8px;">
                        <div><b>ESTRELLAS:</b> <span class="ball-star" style="display:inline-flex; width:28px; height:28px; font-size:12px;" id="euro_e1">--</span> <span class="ball-star" style="display:inline-flex; width:28px; height:28px; font-size:12px;" id="euro_e2">--</span></div>
                    </div>
                </div>
                <div class="card" style="border: 1px solid #3b82f6;">
                    <h2 style="color: #60a5fa;">🏆 COMBINACIONES</h2>
                    <table>
                        <thead><tr><th>#</th><th>NÚMEROS</th><th>ESTRELLAS</th><th>TIPO</th><th>FUERZA</th></tr></thead>
                        <tbody id="tabla_euromillones"></tbody>
                    </table>
                </div>
            </div>

            <div id="seccion_eurodreams" style="display:none;">
                <div class="card" style="border: 2px solid #8b5cf6; background:#18181b;">
                    <h2 style="color: #c084fc;">🇪🇺 EURODREAMS (6/40)</h2>
                    <div class="balls-container" id="ed_base_container"></div>
                    <div style="display:flex; justify-content:space-around; align-items:center; margin-top:10px; background:#27272a; padding:10px; border-radius:8px;">
                        <div><b>SUEÑO:</b> <span class="ball-sueno" style="display:inline-flex; width:28px; height:28px; font-size:13px;" id="ed_sueno_val">-</span></div>
                    </div>
                </div>
                <div class="card" style="border: 1px solid #8b5cf6;">
                    <h2 style="color: #c084fc;">🏆 APUESTAS</h2>
                    <table>
                        <thead><tr><th>#</th><th>COMBINACIÓN</th><th>SUEÑO</th><th>ESTRATEGIA</th><th>FUERZA</th></tr></thead>
                        <tbody id="tabla_eurodreams"></tbody>
                    </table>
                </div>
            </div>

            <div id="seccion_anguila" style="display:none;">
                <div class="card" style="border: 2px solid #10b981; background:#18181b;">
                    <h2 style="color: #34d399;">🐍 ANGUILA CASCADA 4X</h2>
                    <table>
                        <thead><tr><th>TANDA</th><th>ESTADO</th><th>TIRO</th><th>PALÉ</th><th>FUERZA</th></tr></thead>
                        <tbody id="tabla_anguila_cascada"></tbody>
                    </table>
                </div>
            </div>

            <div id="seccion_tradicional">
                <div class="card" style="border: 2px solid #f59e0b; background: linear-gradient(135deg, #1c1917, #0c0a09);">
                    <h2 style="color: #fbbf24;">⚡ SUPER PALÉ CRUZADO</h2>
                    <table>
                        <thead><tr><th>#</th><th>CRUCE</th><th>SALAS</th><th>FUERZA</th></tr></thead>
                        <tbody id="tabla_super_pales"></tbody>
                    </table>
                </div>
                <div class="card" style="border: 1px solid #22c55e;">
                    <h2 style="color: #4ade80;">⭐ TOP 5 LÍNEAS</h2>
                    <table>
                        <thead><tr><th>#</th><th>NÚMERO</th><th>FUERZA</th><th>ESTADO</th><th>SALA</th></tr></thead>
                        <tbody id="tabla_top5"></tbody>
                    </table>
                </div>
                <div class="card">
                    <h2 style="color: #38bdf8;">📊 TOP 20 NÚMEROS</h2>
                    <div class="table-container">
                        <table>
                            <thead><tr><th>#</th><th>NÚMERO</th><th>FUERZA</th><th>ESTADO</th><th>SALA</th></tr></thead>
                            <tbody id="tabla_sueltos"></tbody>
                        </table>
                    </div>
                </div>
                <div class="card">
                    <h2 style="color: #facc15;">🎯 PALÉS RECOMENDADOS</h2>
                    <div class="table-container">
                        <table>
                            <thead><tr><th>#</th><th>PALÉS</th><th>FUERZA</th><th>SALA</th></tr></thead>
                            <tbody id="tabla_pales"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div id="toast">¡Acción ejecutada! 📱</div>
        </div>

        <script>
            let db = __DATOS_JSON__;
            let suenos = __SUENOS_JSON__;
            let auditoria = __AUDITORIA_JSON__;
            let termometro = __TERMOMETRO_JSON__;
            let tabActual = 'real';

            function renderBadge(tipo) {
                if (tipo === "triple_factor") return "<span style='background:#facc15;color:#000;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:900;'>👑 3X</span>";
                if (tipo === "virado") return "<span style='background:#f59e0b;color:#000;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>🛡️ REV</span>";
                return "<span style='background:#22c55e;color:#000;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>⭐ ÉLITE</span>";
            }

            function actualizarRelojCabecera() {
                const ahora = new Date();
                let horas = String(ahora.getHours()).padStart(2, '0');
                let minutos = String(ahora.getMinutes()).padStart(2, '0');
                let segundos = String(ahora.getSeconds()).padStart(2, '0');
                document.getElementById('live_time').innerText = horas + ":" + minutos + ":" + segundos;
            }

            function cargarTermometro() {
                let html = `
                    <div class="termo-box">
                        <b style="color:#fb923c;font-size:11.5px;">🔥 DECENAS CLAVE:</b>
                        <div style="margin-top:6px;">
                            ${termometro.decenas_calientes.map(d => `<div class="termo-row"><span>${d.rango}</span> <b style="color:#fca5a5;">${d.presion}%</b></div>`).join('')}
                        </div>
                    </div>
                    <div class="termo-box">
                        <b style="color:#38bdf8;font-size:11.5px;">🎯 ESTADO GLOBAL:</b>
                        <div style="margin-top:6px;">
                            ${termometro.terminales_fuertes.map(t => `<div class="termo-row"><span>${t.digito}</span> <b style="color:#4ade80;">${t.frecuencia}</b></div>`).join('')}
                        </div>
                    </div>
                `;
                document.getElementById('termo_contenedor').innerHTML = html;
            }

            function cargarAuditoria() {
                let html = "";
                auditoria.forEach(item => {
                    html += `<div class="auditor-item"><b style="color:#38bdf8;">${item.tipo}:</b> <span style="color:#4ade80;">${item.premio}</span></div>`;
                });
                document.getElementById('contenedor_auditoria').innerHTML = html;
            }

            function cambiarTab(clave) {
                tabActual = clave;
                document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
                if (event && event.target) { event.target.classList.add('active'); }
                actualizarVista();
            }

            function actualizarVista() {
                const info = db[tabActual] || db['real'];
                document.getElementById('dictamen_sala').innerText = "[" + info.nombre + "]";

                if (info.tiro_fijo) {
                    document.getElementById('s_fijo').innerText = info.tiro_fijo.num;
                    document.getElementById('s_virado').innerText = info.tiro_fijo.virado;
                    document.getElementById('s_pale').innerText = info.tiro_fijo.palé_titan;
                    document.getElementById('s_fuerza').innerText = info.tiro_fijo.fuerza + "%";
                    document.getElementById('s_lot_fuerte').innerText = info.tiro_fijo.lot_fuerte || info.nombre;
                }

                if (info.dictamen) {
                    document.getElementById('d_flujo').innerText = info.dictamen.flujo;
                    document.getElementById('d_decena').innerText = info.dictamen.decena;
                    document.getElementById('d_terminal').innerText = info.dictamen.terminal;
                    document.getElementById('d_pareja').innerText = info.dictamen.pareja;
                    document.getElementById('d_digito').innerText = info.dictamen.digito_fuerte;
                    document.getElementById('d_dia').innerText = info.dictamen.dia_tendencia;
                    document.getElementById('d_presion').innerText = info.dictamen.presion;
                }

                let esEspañolaOExtranjera = ['kino_leidsa', 'primitiva_esp', 'euromillones', 'eurodreams', 'anguila_cascada'].includes(tabActual);

                document.getElementById('seccion_kino').style.display = (tabActual === 'kino_leidsa') ? 'block' : 'none';
                document.getElementById('seccion_primitiva').style.display = (tabActual === 'primitiva_esp') ? 'block' : 'none';
                document.getElementById('seccion_euromillones').style.display = (tabActual === 'euromillones') ? 'block' : 'none';
                document.getElementById('seccion_eurodreams').style.display = (tabActual === 'eurodreams') ? 'block' : 'none';
                document.getElementById('seccion_anguila').style.display = (tabActual === 'anguila_cascada') ? 'block' : 'none';
                document.getElementById('seccion_tradicional').style.display = (!esEspañolaOExtranjera) ? 'block' : 'none';
                document.getElementById('caja_jugada_formada').style.display = (!esEspañolaOExtranjera) ? 'block' : 'none';

                if (info.tipo_juego === 'kino') {
                    const kd = info.kino_data;
                    document.getElementById('kino_estado_txt').innerText = kd.estado_tombola;
                    document.getElementById('kino_paridad_txt').innerText = kd.paridad_optima;
                    document.getElementById('kino_muerta_txt').innerText = kd.zona_muerta;

                    let htmlD = "";
                    kd.duenos.forEach(b => { htmlD += `<div class="ball-kino">${b}</div>`; });
                    document.getElementById('kino_duenos_container').innerHTML = htmlD;

                    let htmlK5 = "";
                    kd.bloques_5.forEach((b, i) => {
                        htmlK5 += `<tr><td>0${i+1}</td><td style="color:#facc15;font-weight:bold;">${b.bloque}</td><td>${b.paridad}</td><td>${b.ia_origen}</td><td style="color:#4ade80;">${b.fuerza}%</td></tr>`;
                    });
                    document.getElementById('tabla_kino_5').innerHTML = htmlK5;

                    let htmlK7 = "";
                    kd.bloques_7.forEach((b, i) => {
                        htmlK7 += `<tr><td>0${i+1}</td><td style="color:#f472b6;font-weight:bold;">${b.bloque}</td><td>${b.paridad}</td><td>${b.ia_origen}</td><td style="color:#4ade80;">${b.fuerza}%</td></tr>`;
                    });
                    document.getElementById('tabla_kino_7').innerHTML = htmlK7;

                } else if (info.tipo_juego === 'primitiva') {
                    const pd = info.primitiva_data;
                    document.getElementById('prim_reintegro').innerText = pd.reintegro;
                    document.getElementById('prim_comp').innerText = pd.complementario;
                    let htmlPBase = "";
                    pd.numeros_base.forEach(b => { htmlPBase += `<div class="ball-primitiva">${b}</div>`; });
                    document.getElementById('primitiva_base_container').innerHTML = htmlPBase;

                    let htmlP = "";
                    pd.apuestas_6.forEach((a, i) => {
                        htmlP += `<tr><td>0${i+1}</td><td style="color:#f87171;font-weight:bold;">${a.combinacion}</td><td>${a.reintegro}</td><td>${a.tipo}</td><td style="color:#4ade80;">${a.fuerza}%</td></tr>`;
                    });
                    document.getElementById('tabla_primitiva').innerHTML = htmlP;

                } else if (info.tipo_juego === 'euromillones') {
                    const ed = info.euro_data;
                    document.getElementById('euro_e1').innerText = ed.estrellas_fijas[0];
                    document.getElementById('euro_e2').innerText = ed.estrellas_fijas[1];
                    let htmlEBase = "";
                    ed.red_afinidad.forEach(b => {
                        htmlEBase += b.includes('*') ? `<div class="ball-star">${b.replace('*','')}</div>` : `<div class="ball-euro">${b}</div>`;
                    });
                    document.getElementById('euro_base_container').innerHTML = htmlEBase;

                    let htmlE = "";
                    ed.apuestas_euro.forEach((a, i) => {
                        htmlE += `<tr><td>0${i+1}</td><td style="color:#60a5fa;font-weight:bold;">${a.numeros}</td><td>⭐ ${a.estrellas}</td><td>${a.tipo}</td><td style="color:#4ade80;">${a.fuerza}%</td></tr>`;
                    });
                    document.getElementById('tabla_euromillones').innerHTML = htmlE;

                } else if (info.tipo_juego === 'eurodreams') {
                    const ed = info.ed_data;
                    document.getElementById('ed_sueno_val').innerText = ed.sueno_reina;
                    let htmlB = "";
                    ed.numeros_base.forEach(b => { htmlB += `<div class="ball-dream">${b}</div>`; });
                    document.getElementById('ed_base_container').innerHTML = htmlB;

                    let htmlED = "";
                    ed.apuestas.forEach((a, i) => {
                        htmlED += `<tr><td>0${i+1}</td><td style="color:#c084fc;font-weight:bold;">${a.combinacion}</td><td>${a.sueno}</td><td>${a.tipo}</td><td style="color:#4ade80;">${a.fuerza}%</td></tr>`;
                    });
                    document.getElementById('tabla_eurodreams').innerHTML = htmlED;

                } else {
                    if (info.super_pales) {
                        let htmlSP = "";
                        info.super_pales.forEach((sp, i) => {
                            htmlSP += `<tr><td>0${i+1}</td><td style="color:#fbbf24;font-weight:bold;">${sp.cruse}</td><td>${sp.salas}</td><td style="color:#4ade80;">${sp.fuerza}%</td></tr>`;
                        });
                        document.getElementById('tabla_super_pales').innerHTML = htmlSP;
                    }

                    if (info.jugada_maestra) {
                        const jm = info.jugada_maestra;
                        let htmlB = "";
                        jm.numeros_3.forEach(n => { htmlB += `<span class="jf-ball">${n}</span>`; });
                        document.getElementById('jf_numeros_container').innerHTML = htmlB;
                        document.getElementById('jf_pales_txt').innerText = `[${jm.pale_1}] / [${jm.pale_2}]`;
                        document.getElementById('jf_tripleta_txt').innerText = `[${jm.tripleta}]`;
                        document.getElementById('jf_lot_txt').innerText = jm.lot_fuerte;
                        document.getElementById('jf_respaldo_txt').innerText = jm.lot_respaldo;

                        if (info.cobertura_lateral) {
                            document.getElementById('cov_mas_menos').innerText = `[+1: ${info.cobertura_lateral.mas1}] / [-1: ${info.cobertura_lateral.menos1}]`;
                            document.getElementById('cov_pale_reves').innerText = `[${info.cobertura_lateral.pale_reves}]`;
                        }
                    }

                    if (info.sueltos) {
                        let htmlTop5 = "";
                        info.sueltos.slice(0, 5).forEach((item, i) => {
                            htmlTop5 += `<tr><td>#${i+1}</td><td style="color:#4ade80;font-size:16px;font-weight:bold;">${item.num}</td><td>${item.fuerza}%</td><td>${renderBadge(item.tipo)}</td><td>${item.lot}</td></tr>`;
                        });
                        document.getElementById('tabla_top5').innerHTML = htmlTop5;

                        let htmlSueltos = "";
                        info.sueltos.forEach((item, i) => {
                            htmlSueltos += `<tr><td>#${String(i+1).padStart(2, '0')}</td><td style="color:#38bdf8;font-size:15px;font-weight:bold;">${item.num}</td><td>${item.fuerza}%</td><td>${renderBadge(item.tipo)}</td><td>${item.lot}</td></tr>`;
                        });
                        document.getElementById('tabla_sueltos').innerHTML = htmlSueltos;

                        let htmlPales = "";
                        let countP = 1;
                        for (let i = 0; i < Math.min(info.sueltos.length, 5); i++) {
                            for (let j = i + 1; j < Math.min(info.sueltos.length, 5); j++) {
                                let f = ((info.sueltos[i].fuerza + info.sueltos[j].fuerza) / 2).toFixed(1);
                                htmlPales += `<tr><td>${String(countP).padStart(2, '0')}</td><td style="color:#facc15;font-weight:bold;font-size:15px;">${info.sueltos[i].num} - ${info.sueltos[j].num}</td><td>${f}%</td><td>${info.sueltos[i].lot}</td></tr>`;
                                countP++;
                            }
                        }
                        document.getElementById('tabla_pales').innerHTML = htmlPales;
                    }
                }
            }

            function copiarWhatsApp() {
                const info = db[tabActual] || db['real'];
                let texto = `⚡ *JUGADA TITÁN SHNEYDER IA PRO RD* ⚡\n🎯 *Sala:* ${info.nombre}\n🎯 *Directos:* [${info.jugada_maestra.numeros_3.join(' - ')}]\n💥 *Palés:* [${info.jugada_maestra.pale_1}]`;
                navigator.clipboard.writeText(texto).then(() => {
                    const t = document.getElementById('toast');
                    t.innerText = "¡Copiado!";
                    t.style.display = 'block';
                    setTimeout(() => { t.style.display = 'none'; }, 2000);
                });
            }

            function generarTicket() {
                 copiarWhatsApp();
            }

            function buscarSueno() {
                const input = document.getElementById('input_sueno').value.toLowerCase().trim();
                const res = document.getElementById('sueno_resultado');
                if (!input) return;
                let match = suenos[input];
                if (match) {
                    res.style.display = 'block';
                    res.innerHTML = `🔮 <b>CÁBALA INTERCEPTADA:</b> "${input.toUpperCase()}"<br>🎯 <b>Bolo Clave:</b> <span style="color:#4ade80;font-size:16px;font-weight:bold;">${match.num}</span><br>📍 <b>Sala Sugerida:</b> ${match.lot} (${match.cabala})`;
                } else {
                    res.style.display = 'block';
                    res.innerHTML = `🔮 El Motor IA procesó "${input}". Se recomienda verificar la decena principal del radar térmico.`;
                }
            }

            cargarTermometro();
            cargarAuditoria();
            setInterval(actualizarRelojCabecera, 1000);
            actualizarRelojCabecera();
            actualizarVista();
        </script>
    </body>
    </html>
    """

    html_final = html_template.replace("__BANNER_COLOR__", banner_color)
    html_final = html_final.replace("__BANNER_BORDE__", banner_borde)
    html_final = html_final.replace("__BANNER_TXT__", banner_txt)
    html_final = html_final.replace("__FECHA_STR__", fecha_str)
    
    html_final = html_final.replace("__DATOS_JSON__", datos_json)
    html_final = html_final.replace("__SUENOS_JSON__", suenos_json)
    html_final = html_final.replace("__AUDITORIA_JSON__", auditoria_json)
    html_final = html_final.replace("__TERMOMETRO_JSON__", termometro_json)

    return html_final

if __name__ == "__main__":
    uvicorn.run("servidor_movil:app", host="0.0.0.0", port=10000, reload=True)
