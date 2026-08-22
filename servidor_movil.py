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
    hora_esp = ahora_utc + timedelta(hours=2)
    
    seed_base = int(hora_rd.strftime("%Y%m%d"))
    dia_nombre = DIAS_SEMANA[hora_rd.weekday()]
    es_lunes_domingo = dia_nombre in ["Lunes", "Domingo"]
    
    rng = random.Random(seed_base + (77 if es_lunes_domingo else 33) + hora_rd.hour)

    salas_config = [
        ("anguila_10am", "Anguila Mañana (10:00 AM)", 10, 0, "quiniela", "rd", "La Primera Día (12:00 PM)"),
        ("primera_dia", "La Primera Día (12:00 PM)", 12, 0, "quiniela", "rd", "LoteDom (12:00 PM)"),
        ("lotedom", "LoteDom (12:00 PM)", 12, 0, "quiniela", "rd", "Lotería Real (12:55 PM)"),
        ("real", "Lotería Real (12:55 PM)", 12, 55, "quiniela", "rd", "Anguila Mediodía (1:00 PM)"),
        ("anguila_1pm", "Anguila Mediodía (1:00 PM)", 13, 0, "quiniela", "rd", "Gana Más (2:30 PM)"),
        ("gana_mas", "Gana Más (2:30 PM)", 14, 30, "quiniela", "rd", "Anguila Tarde (6:00 PM)"),
        ("anguila_6pm", "Anguila Tarde (6:00 PM)", 18, 0, "quiniela", "rd", "Loteka (7:55 PM)"),
        ("loteka", "Loteka (7:55 PM)", 19, 55, "quiniela", "rd", "La Primera Noche (8:00 PM)"),
        ("primera_noche", "La Primera Noche (8:00 PM)", 20, 0, "quiniela", "rd", "Nacional Noche (8:50 PM)"),
        ("nacional_noche", "Nacional Noche (8:50 PM)", 20, 50, "quiniela", "rd", "Leidsa (8:55 PM)"),
        ("leidsa", "Leidsa (8:55 PM)", 20, 55, "quiniela", "rd", "Anguila Noche (9:00 PM)"),
        ("anguila_9pm", "Anguila Noche (9:00 PM)", 21, 0, "quiniela", "rd", "Kino Leidsa TV"),
        ("kino_leidsa", "Kino Leidsa TV", 20, 55, "kino", "rd", "Nacional Noche (8:50 PM)"),
        ("primitiva_esp", "La Primitiva (España)", 21, 0, "primitiva", "esp", "Euromillones (Europa)"),
        ("euromillones", "Euromillones (Europa)", 21, 0, "euromillones", "esp", "La Primitiva (España)")
    ]

    minutos_actuales_rd = hora_rd.hour * 60 + hora_rd.minute
    minutos_actuales_esp = hora_esp.hour * 60 + hora_esp.minute

    resultado_final = {}

    for clave, nombre, h_cierre, m_cierre, tipo, region, respaldo in salas_config:
        cierre_minutos = h_cierre * 60 + m_cierre
        minutos_actuales = minutos_actuales_esp if region == "esp" else minutos_actuales_rd
        
        juega_hoy = True
        if tipo == "primitiva":
            juega_hoy = dia_nombre in ["Lunes", "Jueves", "Sábado"]
        elif tipo == "euromillones":
            juega_hoy = dia_nombre in ["Martes", "Viernes"]

        activa = juega_hoy and (minutos_actuales <= cierre_minutos)

        if tipo == "quiniela":
            pool_numeros = [f"{n:02d}" for n in range(100)]
            rng.shuffle(pool_numeros)
            
            sueltos = []
            for i in range(30):
                fuerza_val = round(99.9 - (i * 0.3), 1)
                sueltos.append({"num": pool_numeros[i], "fuerza": fuerza_val})
            
            sueltos_ord = sorted(sueltos, key=lambda x: x['fuerza'], reverse=True)
            n1, n2, n3 = sueltos_ord[0]['num'], sueltos_ord[1]['num'], sueltos_ord[2]['num']
            n4, n5 = sueltos_ord[3]['num'], sueltos_ord[4]['num']
            
            # Asignación de salas objetivo sugeridas para los palés y tripleta
            sala_sugerida_1 = nombre
            sala_sugerida_2 = respaldo
            sala_sugerida_3 = "Lotería Nacional / Leidsa"

            super_pale_1 = f"[{n1} - {n2}] <span style='font-size:11px; color:#38bdf8;'>({sala_sugerida_1})</span>"
            super_pale_2 = f"[{n1} - {n3}] <span style='font-size:11px; color:#38bdf8;'>({sala_sugerida_2})</span>"
            super_pale_3 = f"[{n2} - {n4}] <span style='font-size:11px; color:#38bdf8;'>({sala_sugerida_1})</span>"
            tripleta_caliente = f"[{n1} - {n2} - {n3}] <span style='font-size:11px; color:#f472b6;'>({sala_sugerida_1} + {sala_sugerida_2})</span>"

            decenas_extraidas = set()
            for obj in sueltos_ord[:10]:
                decena_num = (int(obj['num']) // 10) * 10
                decenas_extraidas.add(f"[{decena_num:02d}-{decena_num+9:02d}]")
            lista_decenas = list(decenas_extraidas)[:3]
            while len(lista_decenas) < 3:
                lista_decenas.append("[00-09]")
            decenas_clave_str = ", ".join(lista_decenas)

            terminales_extraidos = set([n['num'][1] for n in sueltos_ord[:10]])
            digitos_extraidos = set([n['num'][0] for n in sueltos_ord[:10]])

            top20_pales = []
            for i in range(20):
                p_str = f"{sueltos_ord[i]['num']} - {sueltos_ord[i+1]['num']}"
                fuerza_pale = round((sueltos_ord[i]['fuerza'] + sueltos_ord[i+1]['fuerza']) / 2, 1)
                top20_pales.append(f"<tr><td>#{i+1}</td><td style='color:#38bdf8; font-weight:bold;'>{p_str}</td><td style='color:#facc15;'>{fuerza_pale}%</td></tr>")

            top20_nums = ""
            for idx, n_obj in enumerate(sueltos_ord[:20]):
                top20_nums += f"<tr><td>#{idx+1}</td><td style='color:#38bdf8; font-weight:bold; font-size:15px;'>{n_obj['num']}</td><td style='color:#4ade80;'>{n_obj['fuerza']}%</td></tr>"

            tres_nums_html = "".join([f'<span class="ball">{n}</span>' for n in [n1, n2, n3]])

            dictamen_html = f"""
            <div class="tactical-box">
                <div style="color:#38bdf8; font-weight:bold; margin-bottom:8px; border-bottom:1px solid #38bdf8; padding-bottom:4px;">⚡ DICTAMEN DE SALA (MOTOR IA CUÁNTICO)</div>
                <div class="tactical-row"><span>Flujo:</span><b style="color:#facc15;">ANCLAJE TRIPLE 3-DECENAS (CALIBRADO)</b></div>
                <div class="tactical-row"><span>Decenas Clave (IA):</span><span style="color:#fff;">{decenas_clave_str}</span></div>
                <div class="tactical-row"><span>Terminales (IA):</span><span style="color:#fff;">Term. {", ".join(list(terminales_extraidos)[:3])}</span></div>
                <div class="tactical-row"><span>Dígitos Fuertes (IA):</span><span style="color:#fff;">{", ".join(list(digitos_extraidos)[:3])}</span></div>
                <div class="tactical-row"><span>Inercia:</span><span style="color:#4ade80;">{dia_nombre}: Vigente</span></div>
            </div>

            <div class="tactical-box" style="border-color: #facc15;">
                <div style="color:#facc15; font-weight:bold; margin-bottom:8px; border-bottom:1px solid #facc15; padding-bottom:4px;">🔥 JUGADA MAESTRA CON SALA OBJETIVO</div>
                <div class="tactical-row"><span>Sala Objetivo Principal:</span><b style="color:#38bdf8;">{nombre}</b></div>
                <div class="tactical-row"><span>Respaldo Sugerido:</span><span style="color:#4ade80;">{respaldo}</span></div>
                <div class="tactical-row"><span>3 Números Base:</span><div>{tres_nums_html}</div></div>
                <div class="tactical-row"><span>Súper Palés + Sala:</span><div style="text-align:right;"><b style="color:#facc15;">{super_pale_1}</b><br><b style="color:#facc15;">{super_pale_2}</b></div></div>
                <div class="tactical-row"><span>Tripleta + Salas:</span><b style="color:#f472b6;">{tripleta_caliente}</b></div>
            </div>

            <h3>⭐ TOP 20 NÚMEROS:</h3>
            <div style="max-height: 250px; overflow-y: auto;">
                <table><tr><th>#</th><th>Número</th><th>Fuerza</th></tr>{top20_nums}</table>
            </div>
            
            <h3>⭐ TOP 20 PALÉS:</h3>
            <div style="max-height: 250px; overflow-y: auto;">
                <table><tr><th>#</th><th>Palé</th><th>Fuerza</th></tr>{"".join(top20_pales)}</table>
            </div>
            """
            resultado_final[clave] = {"nombre": nombre, "activa": activa, "contenido": dictamen_html}

        elif tipo == "kino":
            j_a = ", ".join(["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), 10))])
            j_b = ", ".join(["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), 10))])
            kino_html = f"""
            <h3>👑 JUGADA A (MATRIZ KINO):</h3><p style='color:#facc15; font-weight:bold; text-align:center;'>{j_a}</p>
            <h3>👑 JUGADA B (MATRIZ KINO):</h3><p style='color:#facc15; font-weight:bold; text-align:center;'>{j_b}</p>
            """
            resultado_final[clave] = {"nombre": nombre, "activa": activa, "contenido": kino_html}

        elif tipo == "primitiva":
            p_nums = ", ".join(["{:02d}".format(n) for n in sorted(rng.sample(range(1, 50), 6))])
            prim_html = f"""
            <p style="color:#facc15; font-weight:bold;">🇪🇸 Reintegro: <span style="font-size:18px; color:#fff;">{rng.randint(0, 9)}</span></p>
            <h3>🇪🇸 MATRIZ PRIMITIVA:</h3><p style='color:#38bdf8; font-weight:bold; text-align:center;'>{p_nums}</p>
            """
            resultado_final[clave] = {"nombre": nombre, "activa": activa, "contenido": prim_html}

        elif tipo == "euromillones":
            e_nums = ", ".join([str(n) for n in sorted(rng.sample(range(1, 51), 5))])
            e_estrellas = f"⭐ {rng.randint(1,12)} - ⭐ {rng.randint(1,12)}"
            euro_html = f"""
            <h3>🇪🇺 ESTRELLAS:</h3><p style='color:#38bdf8; font-weight:bold; text-align:center;'>{e_estrellas}</p>
            <h3>🇪🇺 NÚMEROS:</h3><p style='color:#facc15; font-weight:bold; text-align:center;'>{e_nums}</p>
            """
            resultado_final[clave] = {"nombre": nombre, "activa": activa, "contenido": euro_html}
            
    return resultado_final

@app.get("/ping", response_class=PlainTextResponse)
def ping_salud():
    return "OK - Servidor Activo 24/7"

@app.get("/", response_class=HTMLResponse)
def index(request: Request, sala: str = None):
    datos = calcular_enjambre_ia()
    keys = list(datos.keys())
    sala_activa = sala if sala in datos else (keys[0] if keys else "")
    info_actual = datos.get(sala_activa, {"nombre": "Cargando...", "activa": True, "contenido": "<p>Cargando datos...</p>"})

    estado_badge = "<span style='color:#4ade80; font-size:12px;'>● ABIERTA</span>" if info_actual.get("activa", True) else "<span style='color:#f87171; font-size:12px;'>● CERRADA</span>"

    botones_html = ""
    for clave, datos_sala in datos.items():
        clase_activa = "active" if clave == sala_activa else ""
        indicador = "🟢" if datos_sala.get("activa", True) else "🔴"
        botones_html += f'<button class="tab-btn {clase_activa}" onclick="location.href=\'/?sala={clave}\'">{indicador} {datos_sala["nombre"]}</button>'

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
            th, td {{ padding:6px; border-bottom:1px solid #1e293b; text-align:center; font-size: 13px; }}
            th {{ background: #1e293b; color: #94a3b8; position: sticky; top: 0; }}
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
                <h2 id="titulo_sala" style="color: #facc15; font-size: 16px;">📊 {info_actual['nombre'].upper()} {estado_badge}</h2>
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
