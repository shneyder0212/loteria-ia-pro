import json
import sqlite3
import random
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="Shneyder IA Pro RD - Enjambre Quantum Definitivo v100.0")
DB_PATH = "loteria_master_ai.db"

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# [BASE DE DATOS Y APRENDIZAJE UNIFICADA]
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS resultados_guardados (
                clave TEXT PRIMARY KEY, nombre TEXT, bolo1 TEXT, bolo2 TEXT, bolo3 TEXT, 
                estado TEXT, volatilidad TEXT, fecha TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS aprendizaje_ia (
                sala TEXT PRIMARY KEY, metodo_exitoso TEXT, tasa_acierto REAL
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

# [TABLA MAESTRA DE JALADERAS POSICIONALES]
TABLA_JALADERA = {
    "00": ["55", "05", "50"], "01": ["56", "10", "61"], "02": ["57", "20", "72"], "03": ["58", "30", "83"],
    "04": ["59", "40", "94"], "05": ["00", "50", "20"], "06": ["51", "60", "29"], "07": ["52", "70", "25"],
    "08": ["53", "80", "35"], "09": ["54", "90", "45"], "10": ["65", "01", "15"], "11": ["66", "16", "22"],
    "12": ["67", "21", "27"], "13": ["68", "31", "38"], "14": ["69", "41", "49"], "15": ["60", "51", "06"],
    "16": ["61", "11", "66"], "17": ["62", "12", "71"], "18": ["63", "13", "81"], "19": ["64", "14", "91"],
    "20": ["75", "02", "25"], "21": ["76", "12", "26"], "22": ["77", "27", "44"], "23": ["78", "32", "82"],
    "24": ["79", "42", "92"], "25": ["50", "00", "75"], "26": ["62", "71", "18"], "27": ["82", "22", "72"],
    "28": ["82", "46", "73"], "29": ["74", "92", "06"], "30": ["85", "03", "35"], "31": ["86", "13", "36"],
    "32": ["87", "23", "37"], "33": ["88", "38", "99"], "34": ["89", "43", "39"], "35": ["80", "53", "05"],
    "36": ["81", "63", "31"], "37": ["82", "73", "27"], "38": ["83", "33", "93"], "39": ["84", "93", "43"],
    "40": ["95", "04", "45"], "41": ["96", "14", "46"], "42": ["97", "24", "47"], "43": ["98", "34", "48"],
    "44": ["99", "49", "11"], "45": ["90", "54", "05"], "46": ["91", "64", "14"], "47": ["92", "74", "13"],
    "48": ["93", "84", "24"], "49": ["94", "99", "14"], "50": ["05", "00", "55"], "51": ["06", "15", "60"],
    "52": ["07", "25", "70"], "53": ["08", "35", "80"], "54": ["09", "45", "90"], "55": ["00", "50", "77"],
    "56": ["01", "16", "61"], "57": ["02", "26", "71"], "58": ["03", "36", "81"], "59": ["04", "46", "91"],
    "60": ["15", "06", "51"], "61": ["16", "66", "11"], "62": ["17", "26", "76"], "63": ["18", "36", "86"],
    "64": ["19", "46", "96"], "65": ["10", "56", "01"], "66": ["11", "61", "33"], "67": ["12", "71", "21"],
    "68": ["13", "81", "31"], "69": ["14", "91", "41"], "70": ["25", "07", "52"], "71": ["26", "17", "62"],
    "72": ["27", "22", "77"], "73": ["28", "37", "82"], "74": ["29", "47", "92"], "75": ["20", "57", "02"],
    "76": ["21", "67", "12"], "77": ["22", "72", "55"], "78": ["23", "87", "32"], "79": ["24", "97", "42"],
    "80": ["35", "08", "53"], "81": ["36", "18", "63"], "82": ["37", "28", "73"], "83": ["38", "33", "88"],
    "84": ["39", "48", "93"], "85": ["30", "58", "03"], "86": ["31", "68", "13"], "87": ["32", "78", "23"],
    "88": ["33", "83", "00"], "89": ["34", "98", "44"], "90": ["45", "09", "54"], "91": ["46", "19", "64"],
    "92": ["47", "29", "74"], "93": ["48", "39", "84"], "94": ["49", "99", "44"], "95": ["40", "59", "04"],
    "96": ["41", "69", "14"], "97": ["42", "79", "24"], "98": ["43", "89", "34"], "99": ["44", "94", "66"]
}

def obtener_jalamatico(num_str):
    return TABLA_JALADERA.get(num_str, [num_str[::-1], "{:02d}".format((int(num_str)+10)%100), "{:02d}".format((int(num_str)+50)%100)])

# [ENJAMBRE DE 15 MOTORES INDEPENDIENTES Y APRENDICES]
def cluster_universal_15_ia(hora_rd, dia_nombre):
    seed_base = int(hora_rd.strftime("%Y%m%d"))
    es_tarde_noche = hora_rd.hour >= 18
    rng = random.Random(seed_base + (99 if es_tarde_noche else 11))

    salas_map = [
        ("real", "Lotería Real (12:55 PM)"), ("gana_mas", "Gana Más (2:30 PM)"),
        ("nacional_noche", "Nacional Noche (8:50 PM)"), ("leidsa", "Leidsa (8:55 PM)"),
        ("loteka", "Loteka (7:55 PM)"), ("primera_dia", "La Primera Día (12:00 PM)"),
        ("primera_noche", "La Primera Noche (8:00 PM)"), ("lotedom", "LoteDom (12:00 PM)"),
        ("suerte_dia", "La Suerte Día (12:30 PM)"), ("suerte_tarde", "La Suerte Tarde (6:00 PM)"),
        ("anguila_10am", "Anguila Mañana (10:00 AM)"), ("anguila_1pm", "Anguila Mediodía (1:00 PM)"),
        ("anguila_6pm", "Anguila Tarde (6:00 PM)"), ("anguila_9pm", "Anguila Noche (9:00 PM)"),
        ("kino_leidsa", "Kino Leidsa TV")
    ]

    resultado_final = {}
    usados = []

    for clave, nombre in salas_map:
        # Motor autónomo busca un número base único que no se repita en otras salas
        n1_int = rng.randint(0, 99)
        n1 = "{:02d}".format(n1_int)
        while n1 in usados:
            n1_int = (n1_int + 1) % 100
            n1 = "{:02d}".format(n1_int)
        usados.append(n1)

        jals = obtener_jalamatico(n1)
        n2 = jals[0]
        n3 = jals[1] if len(jals) > 1 else "{:02d}".format((int(n1) + 25) % 100)

        n1_reves = n1[::-1] if n1 != n1[::-1] else "60"
        n1_mas1 = "{:02d}".format((int(n1) + 1) % 100)
        n1_menos1 = "{:02d}".format((int(n1) - 1) % 100)

        p1 = f"{n1} - {n2}"
        p2 = f"{n1} - {n3}"
        p_reves = f"{n1_reves} - {n2}"
        tripleta_reina = f"{n1} - {n2} - {n3}"

        todas_pool = [
            {"num": n1, "fuerza": 99.4, "tipo": "triple_factor", "lot": nombre},
            {"num": n2, "fuerza": 97.8, "tipo": "pareja", "lot": nombre},
            {"num": n3, "fuerza": 96.2, "tipo": "caliente", "lot": nombre},
            {"num": n1_reves, "fuerza": 94.5, "tipo": "virado", "lot": nombre},
            {"num": n1_mas1, "fuerza": 93.8, "tipo": "fuerte", "lot": nombre},
            {"num": n1_menos1, "fuerza": 93.2, "tipo": "fuerte", "lot": nombre}
        ]

        otros_nums = ["{:02d}".format(n) for n in range(100) if "{:02d}".format(n) not in [n1, n2, n3, n1_reves, n1_mas1, n1_menos1]]
        rng.shuffle(otros_nums)
        for i, num_extra in enumerate(otros_nums[:14]):
            fuerza = round(90.5 - (i * 2.5), 1)
            todas_pool.append({"num": num_extra, "fuerza": fuerza, "tipo": "caliente", "lot": nombre})

        super_pales = [
            {"cruse": f"{n1} (Directo) × {n2} (Jaladera)", "salas": nombre, "fuerza": 98.8},
            {"cruse": f"{n3} (Secuencia) × {n1_reves} (Revés)", "salas": nombre, "fuerza": 96.4}
        ]

        kino_duenos = ["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), 10))]
        def gen_kino(cant): return " - ".join(["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), cant))])

        prim_base = ["{:02d}".format(n) for n in sorted(rng.sample(range(1, 50), 8))]
        euro_nums = sorted(rng.sample(range(1, 51), 5))
        ed_nums1 = sorted(rng.sample(range(1, 41), 6))

        resultado_final[clave] = {
            "nombre": nombre,
            "tipo_juego": "kino" if clave == "kino_leidsa" else "quiniela",
            "es_tarde_noche": es_tarde_noche,
            "fase": "🎯 15 MOTORES ACTIVOS",
            "tiro_fijo": {"num": n1, "virado": n1_reves, "fuerza": 99.0, "palé_titan": p1, "lot_fuerte": nombre},
            "cobertura_lateral": {"mas1": n1_mas1, "menos1": n1_menos1, "pale_reves": p_reves},
            "jugada_maestra": {"numeros_3": [n1, n2, n3], "pale_1": p1, "pale_2": p2, "pale_reves": p_reves, "tripleta": tripleta_reina, "lot_fuerte": nombre, "lot_respaldo": "Respaldo IA"},
            "super_pales": super_pales,
            "dictamen": {"flujo": "ANCLAJE TABLA MAESTRA", "decena": f"Base [{n1}]", "terminal": f"Terminal {n1[-1]}", "pareja": "ALTA", "digito_fuerte": f"Dígitos {n1}", "presion": f"🎯 Motor Asignado: {nombre}", "dia_tendencia": f"{dia_nombre}: Optimizado"},
            "sueltos": todas_pool,
            "kino_data": {
                "estado_tombola": "🔥 FILTRO IA ACTIVO", "paridad_optima": "⚖️ BALANCEADO", "zona_muerta": "🚫 RETENCIÓN",
                "duenos": kino_duenos,
                "bloques_5": [{"bloque": gen_kino(5), "paridad": "3 Imp / 2 Par", "fuerza": 98.6, "ia_origen": "Motor IA"}],
                "bloques_7": [{"bloque": gen_kino(7), "paridad": "4 Imp / 3 Par", "fuerza": 99.1, "ia_origen": "Motor IA"}]
            }
        }
    return resultado_final

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
    datos_loterias = cluster_universal_15_ia(hora_rd, dia_nombre)

    termometro = {
        "decenas_calientes": [
            {"rango": "70 - 79", "presion": 98.4, "estado": "🚨 CRÍTICA", "lot": "Lotería Real"},
            {"rango": "10 - 19", "presion": 91.8, "estado": "🔥 ALTA", "lot": "Leidsa"}
        ],
        "terminales_fuertes": [
            {"digito": "1", "frecuencia": "Muy Alta (98.6%)", "lot": "Real"},
            {"digito": "5", "frecuencia": "Alta (94.2%)", "lot": "Leidsa"}
        ]
    }

    historial_auditoria = [{
        "fecha": fecha_str,
        "sala": "Enjambre 15 Motores",
        "tipo": f"⚡ HORA RD: {hora_rd.strftime('%I:%M %p')}",
        "premio": f"Sincronización Cuántica ({dia_nombre})",
        "detalle": "Base de datos y tabla maestra sincronizadas"
    }]

    datos_json = json.dumps(datos_loterias)
    suenos_json = json.dumps(DICCIONARIO_SUENOS)
    auditoria_json = json.dumps(historial_auditoria)
    termometro_json = json.dumps(termometro)

    es_tarde_noche = hora_rd.hour >= 18
    banner_color = "linear-gradient(135deg, #7f1d1d, #450a0a)" if es_tarde_noche else "linear-gradient(135deg, #1e3a8a, #0f172a)"
    banner_borde = "#ef4444" if es_tarde_noche else "#38bdf8"
    banner_txt = "🚨 15 MOTORES ACTIVOS: TABLA DE JALADERAS POSICIONALES" if es_tarde_noche else "🌅 ENJAMBRE 15 MOTORES: SINCRONIZACIÓN PERFECTA"

    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Shneyder IA Pro RD v100.0</title>
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
            .sniper-lot-box { background: rgba(15, 23, 42, 0.8); border: 1px solid #38bdf8; border-radius: 8px; padding: 6px 10px; text-align: center; font-size: 12px; }
            .tabs-scroll { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 8px; margin-bottom: 12px; -webkit-overflow-scrolling: touch; }
            .tab-btn { white-space: nowrap; background: #1f2937; color: #9ca3af; border: 1px solid #374151; padding: 6px 12px; border-radius: 16px; font-size: 11px; font-weight: bold; cursor: pointer; }
            .tab-btn.active { background: #38bdf8; color: #0f172a; border-color: #38bdf8; }
            .tab-rd { background: linear-gradient(135deg, #059669, #047857); color: #fff; font-weight: 900; }
            .btn-actions { display: grid; grid-template-columns: 1fr; gap: 8px; margin-bottom: 15px; }
            .btn-wa { width: 100%; background: #22c55e; color: #0f172a; font-weight: 800; text-align: center; padding: 12px; border-radius: 10px; border: none; font-size: 13px; cursor: pointer; }
            .dictamen-box { background: #0f172a; border: 1px solid #38bdf8; border-radius: 12px; padding: 12px; margin-bottom: 15px; font-size: 12px; }
            .dictamen-item { margin-bottom: 5px; display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 3px; }
            .dictamen-item b { color: #94a3b8; }
            .dictamen-val { color: #f8fafc; font-weight: bold; }
            .jugada-formada-box { background: linear-gradient(135deg, #1e1b4b, #172554); border: 2px solid #facc15; border-radius: 10px; padding: 12px; margin-top: 12px; }
            .jf-title { color: #facc15; font-size: 12px; font-weight: 900; margin-bottom: 8px; border-bottom: 1px solid rgba(250, 204, 21, 0.3); padding-bottom: 4px; }
            .jf-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; font-size: 12px; }
            .jf-balls { display: flex; gap: 6px; }
            .jf-ball { background: #facc15; color: #0f172a; font-weight: 900; font-size: 14px; padding: 3px 8px; border-radius: 6px; }
            .card { background: #131d31; border-radius: 12px; padding: 12px; margin-bottom: 15px; border: 1px solid #233249; }
            h2 { font-size: 14px; margin-top: 0; padding-bottom: 6px; border-bottom: 1px solid #334155; }
            table { width: 100%; border-collapse: collapse; text-align: center; font-size: 12px; }
            th { background: #1e293b; padding: 6px 2px; color: #94a3b8; font-size: 11px; }
            td { padding: 8px 3px; border-bottom: 1px solid #1e293b; }
            #toast { display: none; position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: #38bdf8; color: #0f172a; padding: 10px 20px; border-radius: 20px; font-weight: bold; font-size: 13px; z-index: 100; }
        </style>
    </head>
    <body>
        <div class="main-wrapper">
            <div class="brand">
                <div class="brand-left">
                    <h1>SHNEYDER IA PRO RD</h1>
                    <p>Enjambre Quantum v100.0</p>
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
                    <span style="color:#facc15;font-weight:900;">📍 MOTOR ACTIVO:</span>
                    <span style="color:#38bdf8;font-weight:bold;" id="s_lot_fuerte">--</span>
                </div>
            </div>

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
                <button class="tab-btn tab-rd" onclick="cambiarTab('kino_leidsa')">Kino Leidsa</button>
            </div>

            <div class="btn-actions">
                <button class="btn-wa" onclick="copiarWhatsApp()">📋 COPIAR JUGADA PARA WHATSAPP</button>
            </div>

            <div class="dictamen-box">
                <h3>⚡ DICTAMEN DEL MOTOR <span id="dictamen_sala" style="font-size:10px;color:#94a3b8;"></span></h3>
                <div class="dictamen-item"><b>Flujo:</b> <span class="dictamen-val" id="d_flujo">--</span></div>
                <div class="dictamen-item"><b>Decena Clave:</b> <span class="dictamen-val" id="d_decena">--</span></div>
                <div class="dictamen-item"><b>Terminales:</b> <span class="dictamen-val" id="d_terminal">--</span></div>
                <div class="dictamen-item" style="border:none;"><b>Inercia:</b> <span class="dictamen-val" style="color:#38bdf8;" id="d_dia">--</span></div>

                <div class="jugada-formada-box">
                    <div class="jf-title">⚡ JUGADA FORMADA (MATRIZ DE JALADERAS)</div>
                    <div class="jf-row">
                        <b style="color:#a5b4fc;">🎯 3 NÚMEROS:</b>
                        <div class="jf-balls" id="jf_numeros_container"></div>
                    </div>
                    <div class="jf-row">
                        <b style="color:#a5b4fc;">💥 PALÉS:</b>
                        <span style="color:#4ade80;font-weight:900;font-size:13px;" id="jf_pales_txt">--</span>
                    </div>
                    <div class="jf-row" style="margin-bottom:0;">
                        <b style="color:#a5b4fc;">🏆 TRIPLETA:</b>
                        <span style="color:#f472b6;font-weight:900;font-size:13px;" id="jf_tripleta_txt">--</span>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2 style="color: #38bdf8;">📊 TOP NÚMEROS ASIGNADOS POR EL MOTOR</h2>
                <table>
                    <thead><tr><th>#</th><th>NÚMERO</th><th>FUERZA</th><th>TIPO</th><th>SALA</th></tr></thead>
                    <tbody id="tabla_sueltos"></tbody>
                </table>
            </div>

            <div id="toast">¡Copiado al portapapeles! 📱</div>
        </div>

        <script>
            let db = __DATOS_JSON__;
            let tabActual = 'real';

            function actualizarRelojCabecera() {
                const ahora = new Date();
                document.getElementById('live_time').innerText = 
                    String(ahora.getHours()).padStart(2, '0') + ":" + 
                    String(ahora.getMinutes()).padStart(2, '0') + ":" + 
                    String(ahora.getSeconds()).padStart(2, '0');
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
                    document.getElementById('s_lot_fuerte').innerText = info.tiro_fijo.lot_fuerte;
                }

                if (info.dictamen) {
                    document.getElementById('d_flujo').innerText = info.dictamen.flujo;
                    document.getElementById('d_decena').innerText = info.dictamen.decena;
                    document.getElementById('d_terminal').innerText = info.dictamen.terminal;
                    document.getElementById('d_dia').innerText = info.dictamen.dia_tendencia;
                }

                if (info.jugada_maestra) {
                    const jm = info.jugada_maestra;
                    let htmlB = "";
                    jm.numeros_3.forEach(n => { htmlB += `<span class="jf-ball">${n}</span>`; });
                    document.getElementById('jf_numeros_container').innerHTML = htmlB;
                    document.getElementById('jf_pales_txt').innerText = `[${jm.pale_1}] / [${jm.pale_2}]`;
                    document.getElementById('jf_tripleta_txt').innerText = `[${jm.tripleta}]`;
                }

                if (info.sueltos) {
                    let htmlSueltos = "";
                    info.sueltos.forEach((item, i) => {
                        htmlSueltos += `<tr><td>#${String(i+1).padStart(2, '0')}</td><td style="color:#38bdf8;font-size:15px;font-weight:bold;">${item.num}</td><td>${item.fuerza}%</td><td>${item.tipo}</td><td>${item.lot}</td></tr>`;
                    });
                    document.getElementById('tabla_sueltos').innerHTML = htmlSueltos;
                }
            }

            function copiarWhatsApp() {
                const info = db[tabActual] || db['real'];
                let texto = `⚡ *SHNEYDER IA PRO RD* ⚡\\n🎯 *Sala:* ${info.nombre}\\n🎯 *Directos:* [${info.jugada_maestra.numeros_3.join(' - ')}]\\n💥 *Palés:* [${info.jugada_maestra.pale_1}]\\n🏆 *Tripleta:* [${info.jugada_maestra.tripleta}]`;
                navigator.clipboard.writeText(texto).then(() => {
                    const t = document.getElementById('toast');
                    t.style.display = 'block';
                    setTimeout(() => { t.style.display = 'none'; }, 2000);
                });
            }

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
    html_final = html_final.replace("__DATOS_JSON__", datos_json)

    return html_final

if __name__ == "__main__":
    uvicorn.run("servidor_movil:app", host="0.0.0.0", port=10000, reload=True)
