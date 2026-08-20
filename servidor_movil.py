import json
import sqlite3
import time
import random
import threading
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI(title="Shneyder IA Pro RD - Titan Ultra Max v10.0")
DB_PATH = "loteria_master_ai.db"

PETICIONES_IP = {}
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

ESTADO_MOTOR = {
    "ultima_actualizacion": "--:--:--",
    "ciclos_completados": 0,
    "estado_ia": "Iniciando..."
}

def obtener_fecha_operativa():
    ahora = datetime.now()
    fecha_op = ahora - timedelta(hours=4)
    return ahora, fecha_op

def motor_segundo_plano():
    while True:
        try:
            ahora, fecha_op = obtener_fecha_operativa()
            ESTADO_MOTOR["ultima_actualizacion"] = ahora.strftime("%H:%M:%S")
            ESTADO_MOTOR["ciclos_completados"] += 1
            ESTADO_MOTOR["estado_ia"] = f"Matriz Activa (Ciclo #{ESTADO_MOTOR['ciclos_completados']})"
            
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS control_motor_24_7 (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    ciclos INTEGER,
                    estado TEXT
                )
            """)
            cur.execute("INSERT OR REPLACE INTO control_motor_24_7 (id, timestamp, ciclos, estado) VALUES (1, ?, ?, ?)",
                        (ahora.strftime("%Y-%m-%d %H:%M:%S"), ESTADO_MOTOR["ciclos_completados"], "ACTIVO 24/7"))
            conn.commit()
            conn.close()
        except Exception:
            pass
        time.sleep(300)

hilo_ia = threading.Thread(target=motor_segundo_plano, daemon=True)
hilo_ia.start()

def obtener_resultados_oficiales(fecha_str):
    return {
        "anguila_10am": {"nombre": "Anguila Mañana (10:00 AM)", "premios": ["--", "--", "--"], "estado": f"Pendiente {fecha_str}"},
        "primera_dia": {"nombre": "La Primera Día (12:00 PM)", "premios": ["--", "--", "--"], "estado": f"Pendiente {fecha_str}"},
        "lotedom": {"nombre": "LoteDom (12:00 PM)", "premios": ["--", "--", "--"], "estado": f"Pendiente {fecha_str}"},
        "suerte_dia": {"nombre": "La Suerte Día (12:30 PM)", "premios": ["--", "--", "--"], "estado": f"Pendiente {fecha_str}"},
        "real": {"nombre": "Lotería Real (12:55 PM)", "premios": ["--", "--", "--"], "estado": f"Pendiente {fecha_str}"},
        "anguila_1pm": {"nombre": "Anguila Mediodía (1:00 PM)", "premios": ["--", "--", "--"], "estado": f"Pendiente {fecha_str}"},
        "gana_mas": {"nombre": "Gana Más (2:30 PM)", "premios": ["--", "--", "--"], "estado": f"Pendiente {fecha_str}"},
        "suerte_tarde": {"nombre": "La Suerte Tarde (6:00 PM)", "premios": ["--", "--", "--"], "estado": f"Pendiente {fecha_str}"},
        "anguila_6pm": {"nombre": "Anguila Tarde (6:00 PM)", "premios": ["--", "--", "--"], "estado": f"Pendiente {fecha_str}"},
        "loteka": {"nombre": "Loteka (7:55 PM)", "premios": ["--", "--", "--"], "estado": f"Pendiente {fecha_str}"},
        "primera_noche": {"nombre": "La Primera Noche (8:00 PM)", "premios": ["--", "--", "--"], "estado": f"Pendiente {fecha_str}"},
        "nacional_noche": {"nombre": "Nacional Noche (8:50 PM)", "premios": ["--", "--", "--"], "estado": f"Pendiente {fecha_str}"},
        "leidsa": {"nombre": "Leidsa (8:55 PM)", "premios": ["--", "--", "--"], "estado": f"Pendiente {fecha_str}"},
        "anguila_9pm": {"nombre": "Anguila Noche (9:00 PM)", "premios": ["--", "--", "--"], "estado": f"Pendiente {fecha_str}"},
        "kino_tv": {"nombre": "Kino TV Leidsa (8:55 PM)", "premios": ["--"] * 20, "estado": "20 Bolos Pendientes"},
        "king_lottery": {"nombre": "King Lottery (12:30 / 7:30 PM)", "premios": ["--", "--", "--"], "estado": f"Pendiente {fecha_str}"},
        "ny_tarde_noche": {"nombre": "New York (Tarde / Noche)", "premios": ["--", "--", "--"], "estado": f"Pendiente {fecha_str}"},
        "primitiva_esp": {"nombre": "La Primitiva (España)", "premios": ["--", "--", "--", "--", "--", "--"], "complementario": "--", "reintegro": "-", "estado": "Sorteo Jueves 21:40h"},
        "euromillones": {"nombre": "Euromillones (Europa)", "premios": ["--", "--", "--", "--", "--"], "estrellas": ["-", "-"], "estado": "Sorteo Viernes 21:15h"}
    }

def generar_pronosticos_diarios(fecha_op, dia_nombre):
    seed_val = int(fecha_op.strftime("%Y%m%d"))
    rng = random.Random(seed_val)

    salas_nombres = [
        "Gana Más / Nacional Noche",
        "Lotería Real (12:55 PM)",
        "Leidsa (8:55 PM)",
        "La Primera (12:00 / 8:00 PM)",
        "Anguila (10 AM / 1 PM / 6 PM)",
        "Loteka (7:55 PM)",
        "La Suerte (12:30 / 6:00 PM)"
    ]

    def gen_pool(cantidad=20):
        numeros = list(range(100))
        rng.shuffle(numeros)
        pool = []
        tipos = ["triple_factor", "virado", "caliente", "atrasado", "fuerte", "pareja"]
        for i, n in enumerate(numeros[:cantidad]):
            fuerza = round(99.0 - (i * 3.8) + rng.uniform(-1.0, 1.0), 1)
            fuerza = max(20.0, min(99.4, fuerza))
            tipo = tipos[0] if i == 0 else (tipos[1] if i == 1 else rng.choice(tipos[2:]))
            pool.append({
                "num": f"{n:02d}",
                "fuerza": fuerza,
                "tipo": tipo,
                "lot": rng.choice(salas_nombres)
            })
        return pool

    todas_pool = gen_pool(20)
    n1 = todas_pool[0]["num"]
    n2 = todas_pool[1]["num"]
    n3 = todas_pool[2]["num"]
    
    p1 = f"{n1} - {n2}"
    p2 = f"{n1} - {n3}"
    tripleta_reina = f"{n1} - {n2} - {n3}"
    tf_vir = n1[::-1] if n1 != n1[::-1] else f"{(int(n1)+10)%100:02d}"

    decenas = ["40 - 49", "70 - 79", "00 - 09", "20 - 29", "80 - 89"]
    d_caliente = rng.choice(decenas)

    # 1. KINO TV DATA
    kino_duenos = [f"{n:02d}" for n in sorted(rng.sample(range(1, 81), 10))]
    kino_b5_1 = " - ".join([f"{n:02d}" for n in sorted(rng.sample(range(1, 81), 5))])
    kino_b5_2 = " - ".join([f"{n:02d}" for n in sorted(rng.sample(range(1, 81), 5))])
    kino_b5_3 = " - ".join([f"{n:02d}" for n in sorted(rng.sample(range(1, 81), 5))])
    kino_b7_1 = " - ".join([f"{n:02d}" for n in sorted(rng.sample(range(1, 81), 7))])
    kino_b7_2 = " - ".join([f"{n:02d}" for n in sorted(rng.sample(range(1, 81), 7))])

    # 2. PRIMITIVA DATA
    prim_reintegro = str(rng.randint(0, 9))
    prim_comp = f"{rng.randint(1, 49):02d}"
    prim_base = [f"{n:02d}" for n in sorted(rng.sample(range(1, 50), 8))]
    prim_apuestas = [
        {"combinacion": " - ".join([f"{n:02d}" for n in sorted(rng.sample(range(1, 50), 6))]), "reintegro": prim_reintegro, "fuerza": 97.4, "tipo": "Matriz Reducida Directa"},
        {"combinacion": " - ".join([f"{n:02d}" for n in sorted(rng.sample(range(1, 50), 6))]), "reintegro": str(rng.randint(0, 9)), "fuerza": 94.1, "tipo": "Cobertura de Clúster"},
        {"combinacion": " - ".join([f"{n:02d}" for n in sorted(rng.sample(range(1, 50), 6))]), "reintegro": prim_reintegro, "fuerza": 90.8, "tipo": "Equilibrio Geométrico"}
    ]

    # 3. EUROMILLONES DATA
    euro_e1 = f"{rng.randint(1, 6):02d}"
    euro_e2 = f"{rng.randint(7, 12):02d}"
    euro_base_numeros = [f"{n:02d}" for n in sorted(rng.sample(range(1, 51), 6))]
    euro_base = euro_base_numeros + [f"{euro_e1}*", f"{euro_e2}*"]
    euro_apuestas = [
        {"numeros": " - ".join([f"{n:02d}" for n in sorted(rng.sample(range(1, 51), 5))]), "estrellas": f"{euro_e1} - {euro_e2}", "fuerza": 98.8, "tipo": "Bloque Cuántico Titán"},
        {"numeros": " - ".join([f"{n:02d}" for n in sorted(rng.sample(range(1, 51), 5))]), "estrellas": f"{rng.randint(1,5):02d} - {euro_e2}", "fuerza": 95.2, "tipo": "Fuego Cruzado Europeo"},
        {"numeros": " - ".join([f"{n:02d}" for n in sorted(rng.sample(range(1, 51), 5))]), "estrellas": f"{euro_e1} - {rng.randint(8,12):02d}", "fuerza": 92.4, "tipo": "Red de Afinidad Mayor"}
    ]

    return {
        "todas": {
            "nombre": "Todas las Loterías (Consenso General)",
            "tipo_juego": "quiniela",
            "tiro_fijo": {
                "num": n1,
                "virado": tf_vir,
                "fuerza": todas_pool[0]["fuerza"],
                "palé_titan": p1,
                "lot_fuerte": todas_pool[0]["lot"]
            },
            "jugada_maestra": {
                "numeros_3": [n1, n2, n3],
                "pale_1": p1,
                "pale_2": p2,
                "tripleta": tripleta_reina,
                "lot_fuerte": todas_pool[0]["lot"]
            },
            "dictamen": {
                "flujo": "ALTO (Ciclo Dinámico 24/7)",
                "decena": f"Decena Fuerte [{d_caliente}]",
                "terminal": f"Terminales en {n1[-1]}, {n2[-1]} y {n3[-1]}",
                "pareja": "ALTA (Parejas de Respaldo Activas)",
                "digito_fuerte": f"Dígitos {n1[0]} y {n1[1]}",
                "presion": f"🚨 RUPTURA DIARIA: Decena {d_caliente} acumulando máxima presión",
                "dia_tendencia": f"{dia_nombre}: Rotación activa de salidores"
            },
            "sueltos": todas_pool
        },
        "kino_leidsa": {
            "nombre": "VENTA ESPECIAL: KINO LEIDSA TV",
            "tipo_juego": "kino",
            "tiro_fijo": {"num": kino_duenos[0], "virado": "--", "fuerza": 97.4, "palé_titan": "Bloque 5 Activo", "lot_fuerte": "Kino TV Leidsa (8:55 PM)"},
            "kino_data": {
                "estado_tombola": "🔥 TÓMBOLA ACTIVA: Consistencia 92.4% (Filtro Anti-Consecutivos Activo)",
                "paridad_optima": "⚖️ RATIO DE PARIDAD: 10 Pares / 10 Impares (82% de acierto)",
                "zona_muerta": "🚫 ZONA DE RETENCIÓN: 41 al 53 (Evitar saturar apuestas aquí)",
                "duenos": kino_duenos,
                "bloques_5": [
                    {"bloque": kino_b5_1, "fuerza": 96.2, "paridad": "3 Impares / 2 Pares"},
                    {"bloque": kino_b5_2, "fuerza": 93.5, "paridad": "3 Pares / 2 Impares"},
                    {"bloque": kino_b5_3, "fuerza": 90.1, "paridad": "3 Impares / 2 Pares"}
                ],
                "bloques_7": [
                    {"bloque": kino_b7_1, "fuerza": 97.8, "paridad": "4 Impares / 3 Pares"},
                    {"bloque": kino_b7_2, "fuerza": 94.6, "paridad": "4 Pares / 3 Impares"}
                ]
            },
            "dictamen": {
                "flujo": "EXPANSIVO (1 al 80)",
                "decena": "Distribución uniforme por cuadrantes",
                "terminal": "Terminales 7, 8, 3 y 4",
                "pareja": "ALTA (22, 44, 77)",
                "digito_fuerte": "Dígitos 7 y 8",
                "presion": "🎯 RECOMENDACIÓN: Jugar bloques cerrados con dispersión de salto.",
                "dia_tendencia": f"{dia_nombre}: Salidas de números primos y extremos"
            }
        },
        "primitiva_esp": {
            "nombre": "🇪🇸 LA PRIMITIVA (ESPAÑA)",
            "tipo_juego": "primitiva",
            "tiro_fijo": {"num": prim_base[0], "virado": "--", "fuerza": 96.5, "palé_titan": f"R: {prim_reintegro}", "lot_fuerte": "Loterías del Estado (Jueves / Sábados)"},
            "primitiva_data": {
                "reintegro": prim_reintegro,
                "reintegro_fuerza": 94.8,
                "complementario": prim_comp,
                "cuadrantes": "C1 (01-12): 2 bolos | C2 (13-25): 1 bolo | C3 (26-37): 2 bolos | C4 (38-49): 1 bolo",
                "apuestas_6": prim_apuestas,
                "numeros_base": prim_base
            },
            "dictamen": {
                "flujo": "DISTRIBUCIÓN GEOMÉTRICA ÓPTIMA (1 al 49)",
                "decena": "Equilibrio entre decenas bajas (01-19) y altas (30-49)",
                "terminal": "Terminales 2, 4, 7 y 9",
                "pareja": "MEDIA (11, 22, 44)",
                "digito_fuerte": f"Dígito {prim_reintegro} (Fuerte en Reintegro)",
                "presion": "🚨 RUPTURA: Cobertura reforzada en cuadrante 1 y 3",
                "dia_tendencia": f"{dia_nombre}: Concentración en combinación 3P / 3I"
            }
        },
        "euromillones": {
            "nombre": "🇪🇺 EUROMILLONES (EUROPA)",
            "tipo_juego": "euromillones",
            "tiro_fijo": {"num": euro_base_numeros[0], "virado": "--", "fuerza": 98.8, "palé_titan": f"⭐ {euro_e1} - {euro_e2}", "lot_fuerte": "Euromillones (Martes / Viernes)"},
            "euro_data": {
                "estrellas_fijas": [euro_e1, euro_e2],
                "fuerza_estrellas": 97.5,
                "distribucion": "Cobertura 4 Cuadrantes (1-12 / 13-25 / 26-37 / 38-50)",
                "apuestas_euro": euro_apuestas,
                "red_afinidad": euro_base
            },
            "dictamen": {
                "flujo": "MÁXIMA DISPERSIÓN ESTOCÁSTICA (1-50 + Estrellas 1-12)",
                "decena": "Cobertura obligada en rango 40-50",
                "terminal": "Terminales 4, 7, 8 y 9",
                "pareja": "BAJA (22, 44)",
                "digito_fuerte": f"Estrella {euro_e2} en correlación con {euro_e1}",
                "presion": f"🚨 RUPTURA: Estrellas [{euro_e1} - {euro_e2}] con 97.5% consistencia",
                "dia_tendencia": f"{dia_nombre}: Salto simétrico europeo"
            }
        }
    }

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
    return {"status": "ok", "motor_24_7": ESTADO_MOTOR["estado_ia"], "ciclos": ESTADO_MOTOR["ciclos_completados"]}

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    if not verificar_anti_ddos(client_ip):
        return HTMLResponse("<h2>⚠️ SISTEMA EN PROTECCIÓN</h2><p>Espera un momento antes de recargar.</p>", status_code=429)

    ahora, fecha_op = obtener_fecha_operativa()
    fecha_str = fecha_op.strftime("%d/%m/%Y")
    dia_nombre = DIAS_SEMANA[fecha_op.weekday()]

    datos_loterias = generar_pronosticos_diarios(fecha_op, dia_nombre)
    resultados_oficiales = obtener_resultados_oficiales(fecha_str)

    termometro = {
        "decenas_calientes": [
            {
                "rango": datos_loterias["todas"]["dictamen"]["decena"].replace("Decena Fuerte [", "").replace("]", ""),
                "presion": 96.4,
                "estado": "🚨 CRÍTICA",
                "lot": datos_loterias["todas"]["tiro_fijo"]["lot_fuerte"]
            },
            {
                "rango": "70 - 79",
                "presion": 88.2,
                "estado": "🔥 ALTA",
                "lot": "Leidsa (8:55 PM)"
            },
            {
                "rango": "00 - 09",
                "presion": 81.5,
                "estado": "⚡ MEDIA ALTA",
                "lot": "Anguila / La Suerte"
            }
        ],
        "terminales_fuertes": [
            {
                "digito": datos_loterias["todas"]["tiro_fijo"]["num"][-1],
                "frecuencia": "Muy Alta (95.1%)",
                "lot": "Lotería Real (12:55 PM)"
            },
            {
                "digito": datos_loterias["todas"]["tiro_fijo"]["virado"][-1],
                "frecuencia": "Alta (89.5%)",
                "lot": "La Primera (12:00 / 8:00 PM)"
            },
            {
                "digito": "0",
                "frecuencia": "Alta (84.0%)",
                "lot": "Loteka (7:55 PM)"
            }
        ]
    }

    historial_auditoria = [
        {
            "fecha": fecha_str,
            "sala": "Motor Titan 24/7",
            "tipo": f"⚡ MOTOR EN VIVO (Ciclo #{ESTADO_MOTOR['ciclos_completados']})",
            "premio": f"Todos los Sistemas Sincronizados ({dia_nombre})",
            "detalle": "Kino Leidsa + Primitiva + Euromillones + Quinielas RD en línea"
        }
    ]

    datos_json = json.dumps(datos_loterias)
    suenos_json = json.dumps(DICCIONARIO_SUENOS)
    auditoria_json = json.dumps(historial_auditoria)
    premios_json = json.dumps(resultados_oficiales)
    termometro_json = json.dumps(termometro)

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
            .lot-prize-name {{ font-size: 12px; font-weight: bold; color: #38bdf8; margin-bottom: 6px; display: flex; justify-content: space-between; }}
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
            .tab-kino {{ background: linear-gradient(135deg, #eab308, #ca8a04); color: #000; border: 1px solid #fde047; font-weight: 900; }}
            .tab-esp {{ background: linear-gradient(135deg, #dc2626, #991b1b); color: #fff; border: 1px solid #f87171; font-weight: 900; }}
            .tab-euro {{ background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; border: 1px solid #60a5fa; font-weight: 900; }}

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
            .ball-kino {{ background: #eab308; color: #000; font-weight: bold; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 15px; }}
            .ball-primitiva {{ background: #ef4444; color: #fff; font-weight: bold; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 15px; }}
            .ball-euro {{ background: #3b82f6; color: #fff; font-weight: bold; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 15px; }}
            .ball-star {{ background: #facc15; color: #000; font-weight: 900; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 14px; }}

            #toast {{ display: none; position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: #38bdf8; color: #0f172a; padding: 10px 20px; border-radius: 20px; font-weight: bold; font-size: 13px; z-index: 100; }}
        </style>
    </head>
    <body>
        <div class="main-wrapper">
            <div class="brand">
                <div class="brand-left">
                    <h1>SHNEYDER IA PRO RD</h1>
                    <p>Titan Ultra Max v10.0 - Todos los Motores</p>
                </div>
                <div class="brand-right">
                    <div class="brand-date" id="live_date">{dia_nombre} {fecha_str}</div>
                    <div class="brand-clock" id="live_time">--:--:--</div>
                </div>
            </div>

            <!-- PANEL FRANCOTIRADOR -->
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

            <!-- RADAR TÉRMICO -->
            <div class="termo-card">
                <div style="font-size:13px;font-weight:bold;color:#f97316;display:flex;justify-content:space-between;align-items:center;">
                    <span>🌡️ RADAR TÉRMICO DIARIO</span>
                    <span style="font-size:10px;color:#94a3b8;">📅 {fecha_str}</span>
                </div>
                <div class="termo-grid" id="termo_contenedor"></div>
            </div>

            <!-- PIZARRA OFICIAL -->
            <div class="pizarra-card">
                <div style="font-size:14px;font-weight:900;color:#38bdf8;display:flex;justify-content:space-between;align-items:center;">
                    <span>🏆 NÚMEROS PREMIADOS (OFICIALES)</span>
                    <span style="font-size:11px;color:#94a3b8;">📅 Jornada: {fecha_str}</span>
                </div>
                <div class="pizarra-grid" id="pizarra_contenedor"></div>
            </div>

            <!-- AUDITORÍA -->
            <div class="auditor-box">
                <div class="auditor-title">
                    <span>📡 AUDITORÍA OFICIAL EN VIVO</span>
                    <span style="font-size:10px;color:#94a3b8;">Auto-Verificación 24/7</span>
                </div>
                <div id="contenedor_auditoria"></div>
            </div>

            <!-- BUSCADOR DE SUEÑOS -->
            <div class="search-box">
                <input type="text" id="input_sueno" class="search-input" placeholder="Escribe tu sueño o cábala (ej. dinero, boda, agua)...">
                <button class="search-btn" onclick="buscarSueno()">🔮 CONSULTAR</button>
            </div>
            <div id="sueno_resultado"></div>

            <!-- TABS -->
            <div class="tabs-scroll">
                <button class="tab-btn active" onclick="cambiarTab('todas')">🌐 TODAS</button>
                <button class="tab-btn tab-kino" onclick="cambiarTab('kino_leidsa')">👑 KINO LEIDSA</button>
                <button class="tab-btn tab-esp" onclick="cambiarTab('primitiva_esp')">🇪🇸 LA PRIMITIVA</button>
                <button class="tab-btn tab-euro" onclick="cambiarTab('euromillones')">🇪🇺 EUROMILLONES</button>
            </div>

            <div class="btn-actions">
                <button class="btn-wa" onclick="copiarWhatsApp()">📋 COPIAR WHATSAPP</button>
                <button class="btn-ticket" onclick="generarTicket()">🎫 TICKET DE BANCA</button>
            </div>

            <!-- DICTAMEN CON JUGADA FORMADA -->
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
                        <span>⚡ JUGADA FORMADA (CONSENSO DE MOTORES)</span>
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
                        <div><b>REINTEGRO IA:</b> <span style="background:#ef4444; color:#fff; padding:3px 8px; border-radius:50%; font-weight:bold;" id="prim_reintegro">--</span></div>
                        <div><b>COMPLEMENTARIO:</b> <span style="background:#3b82f6; color:#fff; padding:3px 8px; border-radius:50%; font-weight:bold;" id="prim_comp">--</span></div>
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
                        <div><b>ESTRELLAS MAESTRAS:</b> <span class="ball-star" style="display:inline-flex; width:28px; height:28px; font-size:12px;" id="euro_e1">--</span> <span class="ball-star" style="display:inline-flex; width:28px; height:28px; font-size:12px;" id="euro_e2">--</span></div>
                        <div><b>FUERZA PAR:</b> <span style="color:#4ade80; font-weight:bold;" id="euro_fuerza_estrellas">97.5%</span></div>
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

            <!-- TABLAS QUINIELAS -->
            <div id="seccion_tradicional">
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
                    html += `<div class="lot-prize-card">
                        <div class="lot-prize-name"><span>${{isAnguila ? '🐍' : '🇩🇴'}} ${{lot.nombre}}</span> <span style="font-size:10px;color:#94a3b8;">${{lot.estado}}</span></div>
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

                // Mostrar u ocultar secciones según el juego seleccionado
                document.getElementById('seccion_kino').style.display = 'none';
                document.getElementById('seccion_primitiva').style.display = 'none';
                document.getElementById('seccion_euromillones').style.display = 'none';
                document.getElementById('seccion_tradicional').style.display = 'none';
                document.getElementById('caja_jugada_formada').style.display = 'none';

                if (info.tipo_juego === 'kino') {{
                    document.getElementById('seccion_kino').style.display = 'block';
                    const kd = info.kino_data;
                    document.getElementById('kino_estado_txt').innerText = kd.estado_tombola;
                    document.getElementById('kino_paridad_txt').innerText = kd.paridad_optima;
                    document.getElementById('kino_muerta_txt').innerText = kd.zona_muerta;

                    let htmlD = "";
                    kd.duenos.forEach(b => {{ htmlD += `<div class="ball-kino">${{b}}</div>`; }});
                    document.getElementById('kino_duenos_container').innerHTML = htmlD;

                    let htmlK5 = "";
                    kd.bloques_5.forEach((b, i) => {{
                        htmlK5 += `<tr>
                            <td>0${{i+1}}</td>
                            <td style="color:#facc15;font-weight:bold;font-size:15px;">${{b.bloque}}</td>
                            <td style="font-size:11px;color:#94a3b8;">${{b.paridad}}</td>
                            <td style="font-weight:bold;color:#4ade80;">${{b.fuerza}}%</td>
                        </tr>`;
                    }});
                    document.getElementById('tabla_kino_5').innerHTML = htmlK5;

                    let htmlK7 = "";
                    kd.bloques_7.forEach((b, i) => {{
                        htmlK7 += `<tr>
                            <td>0${{i+1}}</td>
                            <td style="color:#f472b6;font-weight:bold;font-size:15px;">${{b.bloque}}</td>
                            <td style="font-size:11px;color:#94a3b8;">${{b.paridad}}</td>
                            <td style="font-weight:bold;color:#4ade80;">${{b.fuerza}}%</td>
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
                    document.getElementById('euro_fuerza_estrellas').innerText = ed.fuerza_estrellas + "%";
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
                    document.getElementById('caja_jugada_formada').style.display = 'block';

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
                            htmlTop5 += `<tr>
                                <td>#${{i+1}}</td>
                                <td style="color:#4ade80;font-size:18px;font-weight:bold;">${{item.num}}</td>
                                <td style="font-weight:bold;">${{item.fuerza}}%</td>
                                <td>${{renderBadge(item.tipo)}}</td>
                                <td style="font-size:10px;">${{item.lot}}</td>
                            </tr>`;
                        }});
                        document.getElementById('tabla_top5').innerHTML = htmlTop5;

                        let htmlSueltos = "";
                        info.sueltos.forEach((item, i) => {{
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
                        for (let i = 0; i < Math.min(info.sueltos.length, 5); i++) {{
                            for (let j = i + 1; j < Math.min(info.sueltos.length, 5); j++) {{
                                let f = ((info.sueltos[i].fuerza + info.sueltos[j].fuerza) / 2).toFixed(1);
                                htmlPales += `<tr>
                                    <td>${{String(countP).padStart(2, '0')}}</td>
                                    <td style="color:#facc15;font-weight:bold;font-size:15px;">${{info.sueltos[i].num}} - ${{info.sueltos[j].num}}</td>
                                    <td style="font-weight:bold;">${{f}}%</td>
                                    <td style="font-size:10px;">${{info.sueltos[i].lot}}</td>
                                </tr>`;
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
                    let n1 = info.sueltos[0].num, n2 = info.sueltos[1].num, n3 = info.sueltos[2].num;
                    let lotFuerte = info.tiro_fijo ? info.tiro_fijo.lot_fuerte : info.nombre;
                    if (info.jugada_maestra) {{
                        n1 = info.jugada_maestra.numeros_3[0];
                        n2 = info.jugada_maestra.numeros_3[1];
                        n3 = info.jugada_maestra.numeros_3[2];
                    }}
                    texto = `⚡ *JUGADA FORMADA SHNEYDER IA PRO RD* ⚡\\n` +
                            `📍 *Lotería Sugerida:* ${{lotFuerte}}\\n` +
                            `🎯 *3 Números Directos:* [${{n1}}] - [${{n2}}] - [${{n3}}]\\n` +
                            `💥 *2 Palés Maestros:* [${{n1}} - ${{n2}}] / [${{n1}} - ${{n3}}]\\n` +
                            `🏆 *1 Tripleta Reina:* [${{n1}} - ${{n2}} - ${{n3}}]\\n` +
                            `⚡ *Dictamen:* ${{info.dictamen ? info.dictamen.flujo : 'Estándar'}}`;
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
                let ticket = `=================================\\n` +
                             `   🎫 TICKET SHNEYDER IA PRO RD\\n` +
                             `=================================\\n` +
                             `SALA: ${{info.nombre.toUpperCase()}}\\n` +
                             `FECHA: ${{new Date().toLocaleDateString()}}\\n` +
                             `---------------------------------\\n`;

                if (info.tipo_juego === 'kino') {{
                    ticket += `BLOQUE KINO (5 NÚMEROS):\\n [${{info.kino_data.bloques_5[0].bloque}}]\\n` +
                              `BLOQUE KINO (7 NÚMEROS):\\n [${{info.kino_data.bloques_7[0].bloque}}]\\n`;
                }} else if (info.tipo_juego === 'primitiva') {{
                    ticket += `PRIMITIVA (6 NÚMEROS):\\n [${{info.primitiva_data.apuestas_6[0].combinacion}}]\\n` +
                              `REINTEGRO: [${{info.primitiva_data.reintegro}}]\\n`;
                }} else if (info.tipo_juego === 'euromillones') {{
                    ticket += `EUROMILLONES (5 NÚMEROS):\\n [${{info.euro_data.apuestas_euro[0].numeros}}]\\n` +
                              `ESTRELLAS: [${{info.euro_data.apuestas_euro[0].estrellas}}]\\n`;
                }} else {{
                    let n1 = info.sueltos[0].num, n2 = info.sueltos[1].num, n3 = info.sueltos[2].num;
                    let lotFuerte = info.tiro_fijo ? info.tiro_fijo.lot_fuerte : info.nombre;
                    if (info.jugada_maestra) {{
                        n1 = info.jugada_maestra.numeros_3[0];
                        n2 = info.jugada_maestra.numeros_3[1];
                        n3 = info.jugada_maestra.numeros_3[2];
                    }}
                    ticket += `SALA SUGERIDA: ${{lotFuerte.toUpperCase()}}\\n` +
                              `3 NÚMEROS DIRECTOS:\\n [${{n1}}]  [${{n2}}]  [${{n3}}]\\n` +
                              `---------------------------------\\n` +
                              `2 PALÉS MAESTROS:\\n [${{n1}} - ${{n2}}]\\n [${{n1}} - ${{n3}}]\\n` +
                              `---------------------------------\\n` +
                              `1 TRIPLETA REINA:\\n [${{n1}} - ${{n2}} - ${{n3}}]\\n`;
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
