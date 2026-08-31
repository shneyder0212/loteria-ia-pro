import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from config import SALAS
from memoria import inicializar_db, contar
from verificador import verificar_sala, sincronizar_todas
from motor_ia import analizar_quiniela
from backtesting import medir
from ranking_loterias import ranking_mejores_loterias
from estudios_diarios import ejecutar_corte, corte_actual, fecha_rd
from memoria import listar_predicciones_fecha
from scheduler_app import iniciar_scheduler
from alerta_maestra import evaluar_alerta_roja

app=FastAPI(title="Shneyder IA Pro - Memoria Verificada")
inicializar_db()
iniciar_scheduler()
MAPA={x[0]:x for x in SALAS}

@app.get("/ping",response_class=PlainTextResponse)
def ping():
    return "OK - Memoria Verificada"

@app.get("/api/verificar/{clave}",response_class=JSONResponse)
def api_verificar(clave:str, fecha:str|None=None):
    return verificar_sala(clave,fecha)

@app.get("/api/sincronizar",response_class=JSONResponse)
def api_sync():
    return sincronizar_todas()

@app.get("/api/memoria/{clave}",response_class=JSONResponse)
def api_memoria(clave:str):
    return {"loteria":clave,"resultados_verificados":contar(clave)}

def panel(clave,tipo):
    if tipo!="quiniela":
        return "<div class='box'>Resultados oficiales/verificados se almacenan en memoria. El analizador específico de este juego se puede ampliar sin mezclar reglas de quiniela.</div>"
    d=analizar_quiniela(clave)
    if d.get("estado")!="OK":
        return f"<div class='box warn'><b>Memoria insuficiente:</b> {d.get('mensaje','')}<br>Muestras: {d.get('muestras',0)}</div>"

    alerta=evaluar_alerta_roja(clave)
    alerta_html=""
    if alerta.get("activa"):
        nums=" - ".join(alerta["numeros"])
        pale=" - ".join(alerta["pale"])
        senales=" · ".join(alerta.get("senales",[]))
        alerta_html=f"""<div class='alerta-roja'>
        <div class='alerta-titulo'>🚨 ALERTA ROJA — JUGADA MAESTRA</div>
        <div class='alerta-sub'>Solo aparece cuando todos los filtros estadísticos están activos.</div>
        <div class='maestra'>{nums}</div>
        <div><b>Palé:</b> {pale}</div>
        <div><b>Tripleta:</b> {nums}</div>
        <div><b>Score Top 1:</b> {alerta["score_top1"]}</div>
        <div><b>Promedio Top 3:</b> {alerta["score_prom_top3"]}</div>
        <div><b>Backtest Top 10 con 2+:</b> {alerta["top10_2mas_backtest"]}%</div>
        <div><b>Muestras:</b> {alerta["muestras"]}</div>
        <div><b>Señales:</b> {senales}</div>
        <div class='alerta-aviso'>No es una garantía de premio; es la señal más fuerte detectada por el sistema.</div>
        </div>"""
    bt=medir(clave)
    b=""
    if bt.get("estado")=="OK":
        b=f'''<div class="box"><b>Backtesting:</b> {bt["muestras"]} sorteos<br>
        Top 5: 2+ = {bt["top5"]["2mas"]}% | 3 = {bt["top5"]["3"]}%<br>
        Top 10: 2+ = {bt["top10"]["2mas"]}% | 3 = {bt["top10"]["3"]}%<br>
        Top 20: 2+ = {bt["top20"]["2mas"]}% | 3 = {bt["top20"]["3"]}%</div>'''
    rows="".join(f"<tr><td>#{i}</td><td class='num'>{x['num']}</td><td>{x['score']}</td><td>{', '.join(x['razones']) or 'estadística'}</td></tr>" for i,x in enumerate(d["ranking"],1))
    return f"{alerta_html}<div class='box'><b>Memoria verificada:</b> {d['muestras']} sorteos</div>{b}<table><tr><th>#</th><th>Número</th><th>Score</th><th>Razones</th></tr>{rows}</table>"




@app.get("/api/alerta-roja/{clave}",response_class=JSONResponse)
def api_alerta_roja(clave:str):
    return evaluar_alerta_roja(clave)

@app.get("/api/corte/{nombre}",response_class=JSONResponse)
def api_corte(nombre:str):
    return ejecutar_corte(nombre)

@app.get("/api/estudios-hoy",response_class=JSONResponse)
def api_estudios_hoy():
    fecha=fecha_rd()
    return {"fecha":fecha,"corte_actual":corte_actual(),"predicciones":listar_predicciones_fecha(fecha)}

@app.get("/api/mejor-loteria",response_class=JSONResponse)
def api_mejor_loteria():
    return ranking_mejores_loterias()

@app.get("/",response_class=HTMLResponse)
def index(sala:str|None=None):
    clave=sala if sala in MAPA else SALAS[0][0]
    _,nombre,tipo,region=MAPA[clave]
    tabs="".join(f"<a class='tab {'active' if s[0]==clave else ''}' href='/?sala={s[0]}'>{s[1]}</a>" for s in SALAS)
    body=panel(clave,tipo)
    estudio=ranking_mejores_loterias()
    if estudio.get("mejor"):
        mejor=estudio["mejor"]
        razones=" · ".join(mejor.get("razones",[]))
        mejor_html=f"""<div class='box'>
        <b>🎯 Lotería con mejor rendimiento medido:</b> {mejor["nombre"]}<br>
        Score de estudio: {mejor["score_estudio"]} | Muestras: {mejor["muestras"]}<br>
        Top 5 (2+): {mejor["reciente"]["top5"]["2mas"]}% |
        Top 10 (2+): {mejor["reciente"]["top10"]["2mas"]}%<br>
        <small>Por qué: {razones}</small>
        </div>"""
    else:
        mejor_html="<div class='box warn'><b>🎯 Mejor lotería:</b> aún no hay suficiente historial verificado para compararlas.</div>"
    html=f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Shneyder IA Pro</title><style>
    body{{background:#080d1a;color:#e2e8f0;font-family:Arial;margin:0;padding:12px}} .wrap{{max-width:980px;margin:auto}}
    .tabs{{display:flex;overflow-x:auto;gap:6px;padding-bottom:10px}} .tab{{background:#1f2937;color:#fff;padding:9px;border-radius:8px;text-decoration:none;white-space:nowrap}}
    .active{{background:#38bdf8;color:#0f172a}} .card{{background:#131d31;border:1px solid #233249;border-radius:12px;padding:15px}}
    .box{{background:#0f172a;border:1px solid #38bdf8;border-radius:8px;padding:10px;margin:10px 0;line-height:1.6}} .warn{{border-color:#facc15}}
    table{{width:100%;border-collapse:collapse}} th,td{{padding:8px;border-bottom:1px solid #233249;text-align:center}} .num{{color:#38bdf8;font-weight:900}}
    .alerta-roja{{background:#3f0a0a;border:3px solid #ef4444;border-radius:12px;padding:14px;margin:12px 0;box-shadow:0 0 18px rgba(239,68,68,.35)}}
    .alerta-titulo{{color:#fecaca;font-size:19px;font-weight:900;text-align:center;letter-spacing:.4px}}
    .alerta-sub{{color:#fca5a5;text-align:center;font-size:12px;margin:5px 0 12px}}
    .maestra{{font-size:27px;font-weight:900;color:#fff;text-align:center;margin:10px 0}}
    .alerta-aviso{{margin-top:10px;color:#fecaca;font-size:11px}}
    button,a.btn{{display:inline-block;background:#10b981;color:#04130e;padding:9px 12px;border-radius:8px;text-decoration:none;font-weight:bold}}
    </style></head><body><div class="wrap"><h1>SHNEYDER IA PRO — MEMORIA VERIFICADA</h1>
    <div class="tabs">{tabs}</div>
    <div class="box"><b>🕒 Cortes automáticos RD:</b> 05:00 mañana · 13:15 tarde · 19:00 noche<br>
    <small>Las jugadas quedan congeladas al publicarse para poder medir sus aciertos.</small></div>
    {mejor_html}<div class="card"><h2>{nombre}</h2>
    <p><a class="btn" href="/api/verificar/{clave}">Verificar resultado de hoy</a></p>{body}</div></div></body></html>'''
    return HTMLResponse(html)

if __name__=="__main__":
    import uvicorn
    uvicorn.run("servidor_movil:app",host="0.0.0.0",port=int(os.getenv("PORT","10000")))
