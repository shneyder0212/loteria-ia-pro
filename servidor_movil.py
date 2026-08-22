import json
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
        ("lotedom", "La Primera Día (12:00 PM)", "quiniela", "Lotería Real (12:55 PM)"),
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
                ("[00-09]", "Decena [00-09]"), ("[10-19]", "Decena [10-19]"),
                ("[20-29]", "Decena [20-29]"), ("[30-39]", "Decena [30-39]"),
                ("[40-49]", "Decena [40-49]"), ("[50-59]", "Decena [50-59]"),
                ("[60-69]", "Decena [60-69]"), ("[70-79]", "Decena [70-79]"),
                ("[80-89]", "Decena [80-89]"), ("[90-99]", "Decena [90-99]")
            ]
            decenas_elegidas = rng.sample(decenas_disponibles, 3)
            pool_numeros = [f"{n:02d}" for n in range(100)]
            rng.shuffle(pool_numeros)
            
            sueltos = []
            for i in range(25):
                fuerza_val = round(99.9 - (i * 0.4), 1)
                sueltos.append({"num": pool_numeros[i], "fuerza": fuerza_val})
            
            sueltos_ord = sorted(sueltos, key=lambda x: x['fuerza'], reverse=True)
            n1, n2, n3 = sueltos_ord[0]['num'], sueltos_ord[1]['num'], sueltos_ord[2]['num']
            
            top5_pales_con_fuerza = []
            for i in range(5):
                p_str = f"{sueltos_ord[i]['num']} - {sueltos_ord[i+1]['num']}"
                fuerza_pale = round((sueltos_ord[i]['fuerza'] + sueltos_ord[i+1]['fuerza']) / 2, 1)
                top5_pales_con_fuerza.append({"pale": p_str, "fuerza": fuerza_pale})

            tripleta_str = f"{n1} - {n2} - {n3}"
            num_base_int = int(n1)
            plus_one = f"{ (num_base_int + 1) % 100:02d }"
            minus_one = f"{ (num_base_int - 1) % 100:02d }"

            dictamen = {
                "flujo": "ANCLAJE TRIPLE 3-DECENAS",
                "decenas_clave": f"{decenas_elegidas[0][1]}, {decenas_elegidas[1][1]}, {decenas_elegidas[2][1]}",
                "terminales": f"Term. {rng.randint(1,9)}, {rng.randint(0,9)}",
                "pareja": rng.choice(["MÁXIMA", "MEDIA", "ALTA"]),
                "digito_fuerte": f"Dígitos {rng.randint(1,5)}, {rng.randint(6,9)}",
                "inercia": f"{dia_nombre}: Vigente",
                "foco_principal": decenas_elegidas[0][1],
                "sala_objetivo": nombre,
                "respaldo": respaldo,
                "tres_numeros": [n1, n2, n3],
                "dos_pales": [f"[{n1} - {n2}]", f"[{n2} - {n3}]"],
                "tripleta": tripleta_str,
                "cobertura": f"Lateral +1 / -1: [[+1: {plus_one}] / [-1: {minus_one}]]",
                "pale_reves": f"Palé Revés: [{n2[1]}{n2[0]} - {n1}]"
            }

            resultado_final[clave] = {
                "nombre": nombre, "activa": True, "tipo_juego": "quiniela",
                "dictamen": dictamen,
                "rankings": {"top5_nums": sueltos_ord[:5], "top5_pales": top5_pales_con_fuerza}
            }
        elif tipo == "kino":
            jugada_a = ["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), 10))]
            jugada_b = ["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), 10))]
            resultado_final[clave] = {
                "nombre": nombre, "activa": True, "tipo_juego": "kino",
                "kino_data": {"jugada_a": jugada_a, "jugada_b": jugada_b}
            }
        elif tipo == "primitiva":
            prim_base = ["{:02d}".format(n) for n in sorted(rng.sample(range(1, 50), 6))]
            resultado_final[clave] = {
                "nombre": nombre, "activa": True, "tipo_juego": "primitiva",
                "primitiva_data": {"reintegro": str(rng.randint(0, 9)), "numeros_base": prim_base}
            }
        elif tipo == "euromillones":
            euro_nums = sorted(rng.sample(range(1, 51), 5))
            e1, e2 = "{:02d}".format(rng.randint(1, 12)), "{:02d}".format(rng.randint(1, 12))
            resultado_final[clave] = {
                "nombre": nombre, "activa": True, "tipo_juego": "euromillones",
                "euro_data": {"estrellas": [e1, e2], "numeros": euro_nums}
            }
            
    return resultado_final

@app.get("/ping", response_class=PlainTextResponse)
def ping_salud():
    return "OK - Servidor Activo 24/7"

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    datos_loterias = calcular_enjambre_ia()
    datos_json = json.dumps(datos_loterias)

    botones_html = ""
    primero = True
    for clave, info in datos_loterias.items():
        nombre_sala = info.get("nombre", clave)
        clase_activa = "active" if primero else ""
        botones_html += f'<button class="tab-btn {clase_activa}" onclick="mostrarSala(\'{clave}\', this)">{nombre_sala}</button>'
        primero = False

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
            .tab-btn {{ background:#1f2937; color:#fff; border:none; padding:10px; margin:2px; border-radius:8px; cursor:pointer; font-weight: bold; white-space: nowrap; }}
            .active {{ background:#38bdf8 !important; color:#0f172a !important; }}
            h3 {{ color: #38bdf8; font-size: 14px; margin-top: 15px; border-bottom: 1px solid #233249; padding-bottom: 4px; }}
            .ball {{ background: #facc15; color: #0f172a; font-weight: 900; border-radius: 50%; width: 34px; height: 34px; display: inline-flex; align-items: center; justify-content: center; margin: 3px; font-size: 13px; }}
            .tactical-box {{ background: #0f172a; border: 1px solid #38bdf8; border-radius: 10px; padding: 12px; margin-bottom: 15px; font-size: 13px; }}
            .tactical-row {{ display: flex; justify-content: space-between; margin-bottom: 6px; border-bottom: 1px solid #1e293b; padding-bottom: 4px; }}
            #pantalla_carga {{ position: fixed; top:0; left:0; width:100%; height:100%; background:#080d1a; display:flex; flex-direction:column; justify-content:center; align-items:center; z-index:9999; color:#38bdf8; font-family:sans-serif; }}
            .spinner {{ border: 4px solid #1e293b; border-top: 4px solid #38bdf8; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin-bottom: 15px; }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        </style>
    </head>
    <body>
        <div id="pantalla_carga">
            <div class="spinner"></div>
            <h2 style="color: #facc15; font-size: 18px; margin: 5px;">SHNEYDER IA PRO RD</h2>
            <p id="texto_cargando" style="color: #94a3b8; font-size: 14px;">Iniciando Sistema Táctico...</p>
        </div>

        <div style="max-width:800px; margin:auto;" id="panel_principal">
            <h1>SHNEYDER IA PRO RD</h1>
            <div id="contenedor_tabs" style="display:flex; gap:6px; overflow-x:auto; padding-bottom:10px;">
                {botones_html}
            </div>
            <div class="card" id="vista_general">
                <h2 id="titulo_sala" style="color: #facc15; font-size: 16px;">Selecciona una Lotería</h2>
                <div id="contenido_sala"></div>
            </div>
        </div>

        <script>
            let db = JSON.parse('{datos_json}');

            function mostrarSala(clave, elemento) {{
                let botones = document.querySelectorAll('.tab-btn');
                botones.forEach(b => b.classList.remove('active'));
                if (elemento) {{
                    elemento.classList.add('active');
                }} else {{
                    let primerBtn = document.querySelector('.tab-btn');
                    if(primerBtn) primerBtn.classList.add('active');
                }}

                let info = db[clave];
                if (!info) return;

                let estadoBadge = "<span style='color:#4ade80; font-size:12px;'>● ACTIVA</span>";
                document.getElementById('titulo_sala').innerHTML = "📊 " + info.nombre.toUpperCase() + " " + estadoBadge;
                let html = "";
                
                if (info.tipo_juego === 'quiniela' && info.dictamen) {{
                    let d = info.dictamen;
                    
                    html += `<div class="tactical-box">`;
                    html += `<div style="color:#38bdf8; font-weight:bold; margin-bottom:8px; border-bottom:1px solid #38bdf8; padding-bottom:4px;">⚡ DICTAMEN DE SALA</div>`;
                    html += `<div class="tactical-row"><span>Flujo:</span><b style="color:#facc15;">${{d.flujo}}</b></div>`;
                    html += `<div class="tactical-row"><span>Decenas Clave:</span><span style="color:#fff;">${{d.decenas_clave}}</span></div>`;
                    html += `<div class="tactical-row"><span>Terminales:</span><span style="color:#fff;">${{d.terminales}}</span></div>`;
                    html += `<div class="tactical-row"><span>Pareja:</span><span style="color:#fff;">${{d.pareja}}</span></div>`;
                    html += `<div class="tactical-row"><span>Dígito Fuerte:</span><span style="color:#fff;">${{d.digito_fuerte}}</span></div>`;
                    html += `<div class="tactical-row"><span>Inercia:</span><span style="color:#4ade80;">${{d.inercia}}</span></div>`;
                    html += `<div style="background:#1e293b; padding:6px; border-radius:6px; text-align:center; color:#facc15; font-weight:bold; margin-top:6px;">🔥 Foco Principal: ${{d.foco_principal}}</div>`;
                    html += `</div>`;

                    html += `<div class="tactical-box" style="border-color: #facc15;">`;
                    html += `<div style="color:#facc15; font-weight:bold; margin-bottom:8px; border-bottom:1px solid #facc15; padding-bottom:4px;">⚡ JUGADA FORMADA (MEMORIA ACTIVA)</div>`;
                    html += `<div class="tactical-row"><span>Sala Objetivo:</span><b style="color:#38bdf8;">${{d.sala_objetivo}}</b></div>`;
                    html += `<div class="tactical-row"><span>Respaldo:</span><span style="color:#4ade80;">${{d.respaldo}}</span></div>`;
                    html += `<div class="tactical-row"><span>3 Números:</span><div>`;
                    d.tres_numeros.forEach(num => {{ html += `<span class="ball" style="width:28px; height:28px; font-size:11px;">${{num}}</span>`; }});
                    html += `</div></div>`;
                    html += `<div class="tactical-row"><span>2 Palés:</span><b style="color:#facc15;">${{d.dos_pales.join(' / ')}}</b></div>`;
                    html += `<div class="tactical-row"><span>1 Tripleta:</span><b style="color:#f472b6;">[${{d.tripleta}}]</b></div>`;
                    html += `<div style="font-size:11px; color:#94a3b8; margin-top:6px;"><b>COBERTURA LATERAL BLINDADA:</b><br>${{d.cobertura}}<br><span style="color:#facc15;">${{d.pale_reves}}</span></div>`;
                    html += `</div>`;

                    html += "<h3>⭐ TOP 5 NÚMEROS:</h3><table><tr><th>#</th><th>Número</th><th>Fuerza</th></tr>";
                    info.rankings.top5_nums.forEach((n, i) => {{ 
                        html += `<tr><td>#${{i+1}}</td><td style="color:#38bdf8; font-weight:bold; font-size:15px;">${{n.num}}</td><td style="color:#4ade80;">${{n.fuerza}}%</td></tr>`; 
                    }});
                    html += "</table>";
                }} 
                else if (info.tipo_juego === 'kino') {{
                    html += "<h3>👑 JUGADA A (MATRIZ KINO):</h3><div style='text-align:center; margin:10px 0;'>";
                    info.kino_data.jugada_a.forEach(d => {{ html += `<span class='ball'>${{d}}</span>`; }});
                    html += "</div><h3>👑 JUGADA B (MATRIZ KINO):</h3><div style='text-align:center; margin:10px 0;'>";
                    info.kino_data.jugada_b.forEach(d => {{ html += `<span class='ball'>${{d}}</span>`; }});
                    html += "</div>";
                }}
                else if (info.tipo_juego === 'primitiva') {{
                    html += `<p style="color:#facc15; font-weight:bold;">🇪🇸 Reintegro: <span style="font-size:18px; color:#fff;">${{info.primitiva_data.reintegro}}</span></p><h3>🇪🇸 MATRIZ PRIMITIVA:</h3><div style='text-align:center; margin:15px 0;'>`;
                    info.primitiva_data.numeros_base.forEach(n => {{ html += `<span class='ball'>${{n}}</span>`; }});
                    html += "</div>";
                }}
                else if (info.tipo_juego === 'euromillones') {{
                    html += "<h3>🇪🇺 ESTRELLAS:</h3><div style='text-align:center; margin:10px 0;'>";
                    info.euro_data.estrellas.forEach(e => {{ html += `<span class='ball' style='background:#38bdf8; color:#0f172a;'>⭐${{e}}</span>`; }});
                    html += "</div><h3>🇪🇺 NÚMEROS:</h3><div style='text-align:center; margin:15px 0;'>";
                    info.euro_data.numeros.forEach(n => {{ html += `<span class='ball'>${{n}}</span>`; }});
                    html += "</div>";
                }}
                document.getElementById('contenido_sala').innerHTML = html;
            }}

            window.onload = function() {{
                setTimeout(() => {{
                    document.getElementById('pantalla_carga').style.display = 'none';
                    let primerBoton = document.querySelector('.tab-btn');
                    if(primerBoton) {{
                        let keys = Object.keys(db);
                        if(keys.length > 0) mostrarSala(keys[0], primerBoton);
                    }}
                }}, 400);
            }};
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

if __name__ == "__main__":
    uvicorn.run("servidor_movil:app", host="0.0.0.0", port=10000)
