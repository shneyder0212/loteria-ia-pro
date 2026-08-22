import json
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
import enjambre_loteria_ai
import entrenador_cuantico_ia

app = FastAPI(title="Shneyder IA Pro RD - Enjambre Cuántico Definitivo")

@app.post("/api/guardar_manual")
def guardar_manual(loteria: str = Form(...), b1: str = Form(...), b2: str = Form(...), b3: str = Form(...)):
    entrenador_cuantico_ia.registrar_y_aprender(loteria, loteria.replace("_", " ").title(), b1, b2, b3)
    return RedirectResponse(url="/", status_code=303)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    datos_loterias = enjambre_loteria_ai.calcular_enjambre_ia()
    datos_json = json.dumps(datos_loterias)

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8"><title>Shneyder IA Pro</title>
        <style>
            body {{ background:#080d1a; color:#e2e8f0; font-family:sans-serif; padding:10px; }}
            .card {{ background:#131d31; border-radius:12px; padding:15px; margin-bottom:15px; border:1px solid #233249; }}
            table {{ width:100%; border-collapse:collapse; color:#fff; }}
            th, td {{ padding:8px; border-bottom:1px solid #1e293b; text-align:center; font-size: 13px; }}
            th {{ background: #1e293b; color: #94a3b8; }}
            .tab-btn {{ background:#1f2937; color:#fff; border:none; padding:10px; margin:2px; border-radius:8px; cursor:pointer; font-weight: bold; }}
            .active {{ background:#38bdf8; color:#0f172a; }}
            h3 {{ color: #38bdf8; font-size: 14px; margin-top: 15px; border-bottom: 1px solid #233249; padding-bottom: 4px; }}
            .ball {{ background: #facc15; color: #0f172a; font-weight: 900; border-radius: 50%; width: 34px; height: 34px; display: inline-flex; align-items: center; justify-content: center; margin: 3px; font-size: 13px; }}
        </style>
    </head>
    <body>
        <div style="max-width:800px; margin:auto;">
            <h1>SHNEYDER IA PRO RD</h1>
            <div id="contenedor_tabs" style="display:flex; gap:6px; overflow-x:auto; padding-bottom:8px;"></div>
            <div class="card" id="vista_general">
                <h2 id="titulo_sala" style="color: #facc15; font-size: 16px;">Selecciona una Lotería</h2>
                <div id="contenido_sala"></div>
            </div>
        </div>
        <script>
            let db = {datos_json};
            let tabActual = Object.keys(db)[0];

            function construirTabs() {{
                let html = "";
                for (let clave in db) {{
                    html += `<button class="tab-btn ${{clave === tabActual ? 'active' : ''}}" onclick="cambiarTab('${{clave}}')">${{db[clave].nombre}}</button>`;
                }}
                document.getElementById('contenedor_tabs').innerHTML = html;
            }}

            function cambiarTab(clave) {{ 
                tabActual = clave; 
                construirTabs(); 
                actualizarVista(); 
            }}

            function actualizarVista() {{
                let info = db[tabActual];
                document.getElementById('titulo_sala').innerText = "📊 TRABAJO DE IA: " + info.nombre.toUpperCase();
                let html = "";
                
                if (info.tipo_juego === 'quiniela' && info.rankings) {{
                    html += "<h3>⭐ TOP 5 NÚMEROS DE ALTA PRECISIÓN:</h3><table><tr><th>#</th><th>Número</th><th>Fuerza</th></tr>";
                    info.rankings.top5_nums.forEach((n, i) => {{ 
                        html += `<tr><td>#${{i+1}}</td><td style="color:#38bdf8; font-weight:bold; font-size:15px;">${{n.num}}</td><td style="color:#4ade80;">${{n.fuerza}}%</td></tr>`; 
                    }});
                    html += "</table>";

                    html += "<h3>💥 TOP 5 PALÉS MAESTROS:</h3>";
                    info.rankings.top5_pales.forEach((p, i) => {{ 
                        html += `<p style="margin:6px 0; font-size:13px; display:flex; justify-content:space-between; align-items:center;"><span>#${{i+1}}: <b style="color:#facc15; font-size:14px;">${{p.pale}}</b></span> <span style="color:#4ade80; font-weight:bold;">${{p.fuerza}}%</span></p>`; 
                    }});

                    html += "<h3>🏆 TRIPLETA RECOMENDADA:</h3>";
                    html += `<p style="font-size:15px; color:#f472b6; font-weight:bold;">[${{info.rankings.top5_tripletas[0]}}]</p>`;

                    html += "<h3>📊 TOP 20 GENERAL (COBERTURA TOTAL):</h3>";
                    html += "<div style='max-height:180px; overflow-y:auto; border:1px solid #1e293b; border-radius:6px;'><table>";
                    info.rankings.top20.forEach((n, i) => {{ 
                        html += `<tr><td>#${{i+1}}</td><td>${{n.num}}</td><td>${{n.fuerza}}%</td></tr>`; 
                    }});
                    html += "</table></div>";
                }} 
                else if (info.tipo_juego === 'kino') {{
                    html += "<h3>👑 MATRIZ DE 10 NÚMEROS DUEÑOS (KINO):</h3><div style='text-align:center; margin:15px 0;'>";
                    info.kino_data.duenos.forEach(d => {{ html += `<span class="ball">${{d}}</span>`; }});
                    html += "</div>";
                }}
                else if (info.tipo_juego === 'primitiva') {{
                    html += `<p style="color:#facc15; font-weight:bold;">🇪🇸 Reintegro Sugerido: <span style="font-size:18px; color:#fff;">${{info.primitiva_data.reintegro}}</span></p>`;
                    html += "<h3>🇪🇸 MATRIZ DE NÚMEROS (LA PRIMITIVA):</h3><div style='text-align:center; margin:15px 0;'>";
                    info.primitiva_data.numeros_base.forEach(n => {{ html += `<span class="ball">${{n}}</span>`; }});
                    html += "</div>";
                }}
                else if (info.tipo_juego === 'euromillones') {{
                    html += "<h3>🇪🇺 ESTRELLAS FIJAS:</h3><div style='text-align:center; margin:10px 0;'>";
                    info.euro_data.estrellas.forEach(e => {{ html += `<span class="ball" style="background:#38bdf8; color:#0f172a;">⭐${{e}}</span>`; }});
                    html += "</div><h3>🇪🇺 NÚMEROS DE AFINIDAD (EUROMILLONES):</h3><div style='text-align:center; margin:15px 0;'>";
                    info.euro_data.numeros.forEach(n => {{ html += `<span class="ball">${{n}}</span>`; }});
                    html += "</div>";
                }}
                
                document.getElementById('contenido_sala').innerHTML = html;
            }}

            construirTabs(); 
            actualizarVista();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

if __name__ == "__main__":
    uvicorn.run("servidor_movil:app", host="0.0.0.0", port=10000)
