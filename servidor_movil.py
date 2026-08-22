import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
import uvicorn
import enjambre_loteria_ai

app = FastAPI(title="Shneyder IA Pro RD - Enjambre Cuántico Definitivo")

@app.get("/ping", response_class=PlainTextResponse)
def ping_salud():
    return "OK - Servidor Activo 24/7"

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    try:
        datos_loterias = enjambre_loteria_ai.calcular_enjambre_ia()
        datos_json = json.dumps(datos_loterias)
    except Exception as e:
        datos_json = "{}"

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
            .active {{ background:#38bdf8; color:#0f172a; }}
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
            <p id="texto_cargando" style="color: #94a3b8; font-size: 14px;">Calculando Dictamen y Memoria Activa...</p>
        </div>

        <div style="max-width:800px; margin:auto;" id="panel_principal">
            <h1>SHNEYDER IA PRO RD</h1>
            <div id="contenedor_tabs" style="display:flex; gap:6px; overflow-x:auto; padding-bottom:10px;"></div>
            <div class="card" id="vista_general">
                <h2 id="titulo_sala" style="color: #facc15; font-size: 16px;">Selecciona una Lotería</h2>
                <div id="contenido_sala"></div>
            </div>
        </div>

        <script>
            let db = JSON.parse('{datos_json}');
            let keys = Object.keys(db);
            let tabActual = keys.length > 0 ? keys[0] : null;

            function construirTabs() {{
                let html = "";
                if (keys.length === 0) {{
                    document.getElementById('contenedor_tabs').innerHTML = "<p style='color:#facc15;'>Cargando matrices de IA...</p>";
                    return;
                }}
                for (let clave in db) {{
                    html += `<button class="tab-btn ${{clave === tabActual ? 'active' : ''}}" onclick="cambiarTab('${{clave}}')">${{db[clave].nombre}}</button>`;
                }}
                document.getElementById('contenedor_tabs').innerHTML = html;
            }}

            function cambiarTab(clave) {{ tabActual = clave; construirTabs(); actualizarVista(); }}

            function actualizarVista() {{
                if (!tabActual || !db[tabActual]) {{
                    document.getElementById('titulo_sala').innerText = "SISTEMA ACTIVO";
                    document.getElementById('contenido_sala').innerHTML = "<p>Selecciona una pestaña superior para ver el dictamen.</p>";
                    return;
                }}
                let info = db[tabActual];
                let estadoBadge = info.activa ? "<span style='color:#4ade80; font-size:12px;'>● ABIERTA</span>" : "<span style='color:#f87171; font-size:12px;'>● CERRADA</span>";
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

            setTimeout(() => {{
                document.getElementById('pantalla_carga').style.display = 'none';
                construirTabs(); 
                actualizarVista();
            }}, 2500);

            setInterval(() => {{ location.reload(); }}, 60000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

if __name__ == "__main__":
    uvicorn.run("servidor_movil:app", host="0.0.0.0", port=10000)
