import json
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn

import enjambre_loteria_ai
import entrenador_cuantico_ia

app = FastAPI(title="Shneyder IA Pro RD - Enjambre Cuántico Definitivo v100.0")

@app.post("/api/guardar_manual")
def guardar_manual(loteria: str = Form(...), b1: str = Form(...), b2: str = Form(...), b3: str = Form(...)):
    entrenador_cuantico_ia.registrar_y_aprender(loteria, loteria.replace("_", " ").title(), b1, b2, b3)
    return RedirectResponse(url="/", status_code=303)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    _, fecha_str, _ = enjambre_loteria_ai.obtener_fechas_rd()
    datos_loterias = enjambre_loteria_ai.calcular_enjambre_ia()
    datos_json = json.dumps(datos_loterias)

    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Shneyder IA Pro RD v100.0</title>
        <style>
            * { box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #080d1a; color: #e2e8f0; margin: 0; padding: 10px; }
            .main-wrapper { max-width: 900px; margin: 0 auto; }
            .brand { display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 12px; padding: 12px 16px; margin-bottom: 12px; border: 1px solid #38bdf8; }
            .brand h1 { font-size: 20px; color: #38bdf8; margin: 0; font-weight: 900; }
            .banca-panel { background: linear-gradient(135deg, #064e3b, #022c22); border: 2px solid #22c55e; border-radius: 12px; padding: 12px; margin-bottom: 12px; }
            .banca-form { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; gap: 6px; margin-top: 8px; }
            .banca-input, .banca-select { background: #0f172a; border: 1px solid #22c55e; color: #fff; padding: 6px; border-radius: 6px; font-size: 12px; }
            .banca-btn { background: #22c55e; color: #000; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; font-size: 12px; }
            .tabs-scroll { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 8px; margin-bottom: 12px; }
            .tab-btn { white-space: nowrap; background: #1f2937; color: #9ca3af; border: 1px solid #374151; padding: 8px 14px; border-radius: 16px; font-size: 11px; font-weight: bold; cursor: pointer; }
            .tab-btn.active { background: #38bdf8; color: #0f172a; border-color: #38bdf8; }
            .tab-inactiva { opacity: 0.4; text-decoration: line-through; }
            .card { background: #131d31; border-radius: 12px; padding: 14px; margin-bottom: 15px; border: 1px solid #233249; }
            h2 { font-size: 14px; margin-top: 0; padding-bottom: 6px; border-bottom: 1px solid #334155; color: #38bdf8; }
            .balls-container { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin: 10px 0; }
            .ball { background: #facc15; color: #0f172a; font-weight: 900; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 14px; }
            table { width: 100%; border-collapse: collapse; text-align: center; font-size: 12px; }
            th { background: #1e293b; padding: 6px; color: #94a3b8; }
            td { padding: 8px; border-bottom: 1px solid #1e293b; }
        </style>
    </head>
    <body>
        <div class="main-wrapper">
            <div class="brand">
                <h1>SHNEYDER IA PRO RD - ENJAMBRE CUÁNTICO</h1>
                <div style="color: #facc15; font-family: monospace; font-weight: bold;" id="live_time">--:--:--</div>
            </div>

            <div class="banca-panel">
                <div style="color:#4ade80; font-weight:900; font-size:12px;">⚡ REGISTRO MANUAL (ENTRENADOR CUÁNTICO)</div>
                <form action="/api/guardar_manual" method="POST" class="banca-form">
                    <select name="loteria" class="banca-select">
                        <option value="real">Lotería Real</option>
                        <option value="gana_mas">Gana Más</option>
                        <option value="nacional_noche">Nacional Noche</option>
                        <option value="leidsa">Leidsa</option>
                        <option value="loteka">Loteka</option>
                        <option value="primera_dia">La Primera Día</option>
                    </select>
                    <input type="text" name="b1" placeholder="1ra" maxlength="2" required class="banca-input" style="text-align:center;">
                    <input type="text" name="b2" placeholder="2da" maxlength="2" required class="banca-input" style="text-align:center;">
                    <input type="text" name="b3" placeholder="3ra" maxlength="2" required class="banca-input" style="text-align:center;">
                    <button type="submit" class="banca-btn">💾 GUARDAR</button>
                </form>
            </div>

            <div class="tabs-scroll" id="contenedor_tabs"></div>

            <div class="card" id="vista_general">
                <h2 id="titulo_sala">Cargando...</h2>
                <div id="contenido_sala"></div>
            </div>
        </div>

        <script>
            let db = __DATOS_JSON__;
            let tabActual = Object.keys(db)[0];

            function construirTabs() {
                let html = "";
                for (let clave in db) {
                    let info = db[clave];
                    let claseInactiva = info.activa ? "" : " tab-inactiva";
                    let claseActiva = clave === tabActual ? " active" : "";
                    html += `<button class="tab-btn${claseActiva}${claseInactiva}" onclick="cambiarTab('${clave}')">${info.nombre}</button>`;
                }
                document.getElementById('contenedor_tabs').innerHTML = html;
            }

            function cambiarTab(clave) {
                tabActual = clave;
                construirTabs();
                actualizarVista();
            }

            function actualizarVista() {
                let info = db[tabActual];
                document.getElementById('titulo_sala').innerText = "📊 TRABAJO DE IA PARA: " + info.nombre.toUpperCase();
                
                let html = "";
                if (info.tipo_juego === 'quiniela') {
                    html += `<p><b>🎯 Tiro Directo:</b> <span style="color:#38bdf8; font-size:18px;">${info.tiro_fijo.num}</span> | <b>Revés:</b> ${info.tiro_fijo.virado}</p>`;
                    html += `<p><b>💥 Palé Titán:</b> <span style="color:#4ade80;">${info.tiro_fijo.palé_titan}</span></p>`;
                    html += `<h3>Líneas de Análisis Cuántico:</h3><table><thead><tr><th>#</th><th>Número</th><th>Fuerza</th><th>Tipo</th></tr></thead><tbody>`;
                    info.sueltos.forEach((s, i) => {
                        html += `<tr><td>0${i+1}</td><td style="color:#38bdf8; font-weight:bold;">${s.num}</td><td>${s.fuerza}%</td><td>${s.tipo}</td></tr>`;
                    });
                    html += `</tbody></table>`;
                } else if (info.tipo_juego === 'kino') {
                    html += `<p style="color:#facc15; font-weight:bold;">👑 Los 10 Dueños del Kino:</p><div class="balls-container">`;
                    info.kino_data.duenos.forEach(d => { html += `<div class="ball">${d}</div>`; });
                    html += `</div><h3>Bloques de Precisión:</h3>`;
                    info.kino_data.bloques_5.forEach(b => { html += `<p>Bloque 5: <b>${b.bloque}</b> (${b.fuerza}%)</p>`; });
                } else if (info.tipo_juego === 'primitiva') {
                    html += `<p><b>🇪🇸 Reintegro:</b> ${info.primitiva_data.reintegro} | <b>Complementario:</b> ${info.primitiva_data.complementario}</p>`;
                    html += `<div class="balls-container">`;
                    info.primitiva_data.numeros_base.forEach(n => { html += `<div class="ball">${n}</div>`; });
                    html += `</div>`;
                } else if (info.tipo_juego === 'euromillones') {
                    html += `<p><b>🇪🇺 Estrellas Fijas:</b> ⭐ ${info.euro_data.estrellas_fijas.join(' - ')}</p>`;
                    html += `<div class="balls-container">`;
                    info.euro_data.red_afinidad.forEach(n => { html += `<div class="ball">${n}</div>`; });
                    html += `</div>`;
                }
                document.getElementById('contenido_sala').innerHTML = html;
            }

            setInterval(() => {
                const ahora = new Date();
                document.getElementById('live_time').innerText = String(ahora.getHours()).padStart(2, '0') + ":" + String(ahora.getMinutes()).padStart(2, '0') + ":" + String(ahora.getSeconds()).padStart(2, '0');
            }, 1000);

            construirTabs();
            actualizarVista();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_template.replace("__DATOS_JSON__", datos_json))

if __name__ == "__main__":
    uvicorn.run("servidor_movil:app", host="0.0.0.0", port=10000, reload=True)
