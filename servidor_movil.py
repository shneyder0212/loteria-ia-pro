import random
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
import uvicorn

app = FastAPI(title="Shneyder IA Pro RD - Enjambre Cuántico Definitivo")

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

def calcular_enjambre_ia():
    ahora_utc = datetime.utcnow()
    hora_rd = ahora_utc - timedelta(hours=4)
    seed_base = int(hora_rd.strftime("%Y%m%d"))
    dia_nombre = DIAS_SEMANA[hora_rd.weekday()]
    es_lunes_domingo = dia_nombre in ["Lunes", "Domingo"]
    
    rng = random.Random(seed_base + (77 if es_lunes_domingo else 33) + hora_rd.hour)

    salas_config = [
        ("anguila_10am", "Anguila Mañana (10:00 AM)", "quiniela", "La Primera Día (12:00 PM)"),
        ("primera_dia", "La Primera Día (12:00 PM)", "quiniela", "LoteDom (12:00 PM)"),
        ("lotedom", "LoteDom (12:00 PM)", "quiniela", "Lotería Real (12:55 PM)"),
        ("real", "Lotería Real (12:55 PM)", "quiniela", "Anguila Mediodía (1:00 PM)"),
        ("anguila_1pm", "Anguila Mediodía (1:00 PM)", "quiniela", "Gana Más (2:30 PM)"),
        ("gana_mas", "Gana Más (2:30 PM)", "quiniela", "Anguila Tarde (6:00 PM)"),
        ("anguila_6pm", "Anguila Tarde (6:00 PM)", "quiniela", "Loteka (7:55 PM)"),
        ("loteka", "Loteka (7:55 PM)", "quiniela", "La Primera Noche (8:00 PM)"),
        ("primera_noche", "La Primera Noche (8:00 PM)", "quiniela", "Nacional Noche (8:50 PM)"),
        ("nacional_noche", "Nacional Noche (8:50 PM)", "quiniela", "Leidsa (8:55 PM)"),
        ("leidsa", "Leidsa (8:55 PM)", "quiniela", "Anguila Noche (9:00 PM)"),
        ("anguila_9pm", "Anguila Noche (9:00 PM)", "quiniela", "Kino Leidsa TV"),
        ("kino_leidsa", "Kino Leidsa TV", "kino", "Nacional Noche (8:50 PM)"),
        ("primitiva_esp", "La Primitiva (España)", "primitiva", "Euromillones (Europa)"),
        ("euromillones", "Euromillones (Europa)", "euromillones", "La Primitiva (España)")
    ]

    resultado_final = {}

    for clave, nombre, tipo, respaldo in salas_config:
        if tipo == "quiniela":
            decenas_disponibles = [
                ("Decena [00-09]"), ("Decena [10-19]"), ("Decena [20-29]"), 
                ("Decena [30-39]"), ("Decena [40-49]"), ("Decena [50-59]"),
                ("Decena [60-69]"), ("Decena [70-79]"), ("Decena [80-89]"), ("Decena [90-99]")
            ]
            decena_foco = rng.choice(decenas_disponibles)
            pool_numeros = [f"{n:02d}" for n in range(100)]
            rng.shuffle(pool_numeros)
            
            sueltos = []
            for i in range(25):
                fuerza_val = round(99.9 - (i * 0.4), 1)
                sueltos.append({"num": pool_numeros[i], "fuerza": fuerza_val})
            
            sueltos_ord = sorted(sueltos, key=lambda x: x['fuerza'], reverse=True)
            n1, n2, n3 = sueltos_ord[0]['num'], sueltos_ord[1]['num'], sueltos_ord[2]['num']
            
            top5_pales = []
            for i in range(5):
                p_str = f"{sueltos_ord[i]['num']} - {sueltos_ord[i+1]['num']}"
                fuerza_pale = round((sueltos_ord[i]['fuerza'] + sueltos_ord[i+1]['fuerza']) / 2, 1)
                top5_pales.append(f"<tr><td>#{i+1}</td><td style='color:#38bdf8; font-weight:bold;'>{p_str}</td><td style='color:#facc15;'>{fuerza_pale}%</td></tr>")

            top5_nums = ""
            for idx, n_obj in enumerate(sueltos_ord[:5]):
                top5_nums += f"<tr><td>#{idx+1}</td><td style='color:#38bdf8; font-weight:bold; font-size:15px;'>{n_obj['num']}</td><td style='color:#4ade80;'>{n_obj['fuerza']}%</td></tr>"

            tres_nums_html = "".join([f'<span class="ball">{n}</span>' for n in [n1, n2, n3]])
            pales_str = f"[{n1} - {n2}] / [{n2} - {n3}]"
            tripleta_str = f"[{n1} - {n2} - {n3}]"

            dictamen_html = f"""
            <div class="tactical-box">
                <div style="color:#38bdf8; font-weight:bold; margin-bottom:8px; border-bottom:1px solid #38bdf8; padding-bottom:4px;">⚡ DICTAMEN DE SALA</div>
                <div class="tactical-row"><span>Flujo:</span><b style="color:#facc15;">ANCLAJE TRIPLE 3-DECENAS</b></div>
                <div class="tactical-row"><span>Decenas Clave:</span><span style="color:#fff;">{decena_foco}</span></div>
                <div class="tactical-row"><span>Terminales:</span><span style="color:#fff;">Term. {rng.randint(1,9)}, {rng.randint(0,9)}</span></div>
                <div class="tactical-row"><span>Pareja:</span><span style="color:#fff;">{rng.choice(["MÁXIMA", "MEDIA", "ALTA"])}</span></div>
                <div class="tactical-row"><span>Inercia:</span><span style="color:#4ade80;">{dia_nombre}: Vigente</span></div>
                <div style="background:#1e293b; padding:6px; border-radius:6px; text-align:center; color:#facc15; font-weight:bold; margin-top:6px;">🔥 Foco Principal: {decena_foco}</div>
            </div>

            <div class="tactical-box" style="border-color: #facc15;">
                <div style="color:#facc15; font-weight:bold; margin-bottom:8px; border-bottom:1px solid #facc15; padding-bottom:4px;">⚡ JUGADA FORMADA (MEMORIA ACTIVA)</div>
                <div class="tactical-row"><span>Sala Objetivo:</span><b style="color:#38bdf8;">{nombre}</b></div>
                <div class="tactical-row"><span>Respaldo:</span><span style="color:#4ade80;">{respaldo}</span></div>
                <div class="tactical-row"><span>3 Números:</span><div>{tres_nums_html}</div></div>
                <div class="tactical-row"><span>2 Palés:</span><b style="color:#facc15;">{pales_str}</b></div>
                <div class="tactical-row"><span>1 Tripleta:</span><b style="color:#f472b6;">{tripleta_str}</b></div>
            </div>

            <h3>⭐ TOP 5 NÚMEROS:</h3>
            <table><tr><th>#</th><th>Número</th><th>Fuerza</th></tr>{top5_nums}</table>
            
            <h3>⭐ TOP 5 PALÉS:</h3>
            <table><tr><th>#</th><th>Palé</th><th>Fuerza</th></tr>{"".join(top5_pales)}</table>
            """
            resultado_final[clave] = {"nombre": nombre, "contenido": dictamen_html}

        elif tipo == "kino":
            j_a = ", ".join(["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), 10))])
            j_b = ", ".join(["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), 10))])
            kino_html = f"""
            <h3>👑 JUGADA A (MATRIZ KINO):</h3><p style='color:#facc15; font-weight:bold; text-align:center;'>{j_a}</p>
            <h3>👑 JUGADA B (MATRIZ KINO):</h3><p style='color:#facc15; font-weight:bold; text-align:center;'>{j_b}</p>
            """
            resultado_final[clave] = {"nombre": nombre, "contenido": kino_html}

        elif tipo == "primitiva":
            p_nums = ", ".join(["{:02d}".format(n) for n in sorted(rng.sample(range(1, 50), 6))])
            prim_html = f"""
            <p style="color:#facc15; font-weight:bold;">🇪🇸 Reintegro: <span style="font-size:18px; color:#fff;">{rng.randint(0, 9)}</span></p>
            <h3>🇪🇸 MATRIZ PRIMITIVA:</h3><p style='color:#38bdf8; font-weight:bold; text-align:center;'>{p_nums}</p>
            """
            resultado_final[clave] = {"nombre": nombre, "contenido": prim_html}

        elif tipo == "euromillones":
            e_nums = ", ".join([str(n) for n in sorted(rng.sample(range(1, 51), 5))])
            e_estrellas = f"⭐ {rng.randint(1,12)} - ⭐ {rng.randint(1,12)}"
            euro_html = f"""
            <h3>🇪🇺 ESTRELLAS:</h3><p style='color:#38bdf8; font-weight:bold; text-align:center;'>{e_estrellas}</p>
            <h3>🇪🇺 NÚMEROS:</h3><p style='color:#facc15; font-weight:bold; text-align:center;'>{e_nums}</p>
            """
            resultado_final[clave] = {"nombre": nombre, "contenido": euro_html}
            
    return resultado_final

@app.get("/ping", response_class=PlainTextResponse)
def ping_salud():
    return "OK - Servidor Activo 24/7"

@app.get("/", response_class=HTMLResponse)
def index(request: Request, sala: str = None):
    datos = calcular_enjambre_ia()
    keys = list(datos.keys())
    sala_activa = sala if sala in datos else (keys[0] if keys else "")
    info_actual = datos.get(sala_activa, {"nombre": "Cargando...", "contenido": "<p>Cargando datos...</p>"})

    botones_html = ""
    for clave, datos_sala in datos.items():
        clase_activa = "active" if clave == sala_activa else ""
        botones_html += f'<button class="tab-btn {clase_activa}" onclick="location.href=\'/?sala={clave}\'">{datos_sala["nombre"]}</button>'

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8"><title>Shneyder IA Pro</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ background:#080d1a; color:#e2e8f0; font-family:sans-serif; padding:10px; margin:0; }}
            .card {{ background:#131d31; border-radius:12px; padding:15px; margin-bottom:15px; border:1px solid #233249; }}
            table {{ width:100%; border-collapse:collapse; color:#fff; }}
            th, td {{ padding:8px; border-bottom:1px solid #1e293b; text-align:center; font-size: 13px; }}
            th {{ background: #1e293b; color: #94a3b8; }}
            .tab-btn {{ background:#1f2937; color:#fff; border:none; padding:10px; margin:2px; border-radius:8px; cursor:pointer; font-weight: bold; white-space: nowrap; text-decoration: none; display: inline-block; }}
            .active {{ background:#38bdf8 !important; color:#0f172a !important; }}
            h3 {{ color: #38bdf8; font-size: 14px; margin-top: 15px; border-bottom: 1px solid #233249; padding-bottom: 4px; }}
            .ball {{ background: #facc15; color: #0f172a; font-weight: 900; border-radius: 50%; width: 32px; height: 32px; display: inline-flex; align-items: center; justify-content: center; margin: 3px; font-size: 12px; }}
            .tactical-box {{ background: #0f172a; border: 1px solid #38bdf8; border-radius: 10px; padding: 12px; margin-bottom: 15px; font-size: 13px; }}
            .tactical-row {{ display: flex; justify-content: space-between; margin-bottom: 6px; border-bottom: 1px solid #1e293b; padding-bottom: 4px; }}
        </style>
    </head>
    <body>
        <div style="max-width:800px; margin:auto;" id="panel_principal">
            <h1>SHNEYDER IA PRO RD</h1>
            <div id="contenedor_tabs" style="display:flex; gap:6px; overflow-x:auto; padding-bottom:10px;">
                {botones_html}
            </div>
            <div class="card" id="vista_general">
                <h2 id="titulo_sala" style="color: #facc15; font-size: 16px;">📊 {info_actual['nombre'].upper()} <span style='color:#4ade80; font-size:12px;'>● ACTIVA</span></h2>
                <div id="contenido_sala">
                    {info_actual['contenido']}
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

if __name__ == "__main__":
    uvicorn.run("servidor_movil:app", host="0.0.0.0", port=10000)
