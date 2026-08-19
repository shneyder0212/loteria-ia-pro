from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from datetime import datetime
from scraper_loteria import ScraperLoteriasRD
from enjambre_loteria_ai import Enjambre100AgentesLoteria

app = FastAPI()
scraper = ScraperLoteriasRD(db_path="loteria_master_ai.db")
enjambre = Enjambre100AgentesLoteria(db_path="loteria_master_ai.db")

@app.get("/", response_class=HTMLResponse)
def dashboard_movil():
    scraper.sincronizar_todo()
    rep = enjambre.ejecutar_consenso_100_agentes()
    
    if "error" in rep:
        return f"<h2>{rep['error']}</h2>"

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>IA Loterias - Shneyder</title>
        <style>
            body {{ font-family: -apple-system, Roboto, sans-serif; background: #0d1117; color: #fff; padding: 12px; margin: 0; }}
            .header {{ background: #161b22; border: 1px solid #30363d; border-left: 4px solid #238636; border-radius: 8px; padding: 12px; margin-bottom: 12px; }}
            .title {{ font-size: 15px; font-weight: bold; color: #3fb950; margin: 0; }}
            .sub {{ font-size: 12px; color: #8b949e; margin-top: 4px; }}
            .section {{ font-size: 14px; font-weight: bold; color: #58a6ff; margin: 14px 0 8px 0; text-transform: uppercase; border-bottom: 1px solid #30363d; padding-bottom: 4px; }}
            .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 8px 12px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; }}
            .badge {{ background: #238636; color: #fff; font-weight: bold; padding: 2px 8px; border-radius: 12px; font-size: 12px; }}
            .num {{ font-size: 16px; font-weight: bold; color: #f0883e; }}
            .lot {{ font-size: 11px; color: #7ee787; font-weight: 500; }}
            .btn-refresh {{ display: block; width: 100%; background: #1f6feb; color: white; border: none; padding: 12px; border-radius: 6px; font-weight: bold; font-size: 14px; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">⚡ IA SHNEYDER - PANEL MOVIL</div>
            <div class="sub">Ultimo Salidor: <b>[{rep['ultimo_salidor']}]</b> | {datetime.now().strftime('%I:%M %p')}</div>
        </div>

        <div class="section">🔥 Top 5 Lineas Fuertes</div>
    """
    for i, item in enumerate(rep["top_5_lineas_fuertes"], 1):
        html += f"""
        <div class="card">
            <div><span class="num">#{i} [{item['numero']}]</span> <div class="lot">📍 {item['loteria']}</div></div>
            <span class="badge">{item['fuerza_ia']}%</span>
        </div>
        """

    html += '<div class="section">🎯 Top 10 Pales Fuertes</div>'
    for i, p in enumerate(rep["top_20_pales"][:10], 1):
        html += f"""
        <div class="card">
            <div><span class="num">{i:02d}. [{p['pale']}]</span> <div class="lot">📍 {p['loteria']}</div></div>
            <span class="badge">{p['fuerza']}%</span>
        </div>
        """

    html += """
        <button class="btn-refresh" onclick="location.reload()">🔄 Actualizar Ahora</button>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)