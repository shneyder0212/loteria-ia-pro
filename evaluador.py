from memoria import listar_predicciones_fecha,ultimo_resultado,guardar_evaluacion

def evaluar_fecha(fecha,clave=None):
    salida=[]
    for p in listar_predicciones_fecha(fecha):
        if clave and p['loteria_clave']!=clave: continue
        real=ultimo_resultado(p['loteria_clave'])
        if not real or real['fecha']!=fecha: continue
        reales={str(x).zfill(2) for x in real['resultado'].get('numeros',[])}; rank=[str(x.get('num')).zfill(2) for x in p['ranking']]
        a5=len(reales.intersection(rank[:5])); a10=len(reales.intersection(rank[:10])); a20=len(reales.intersection(rank[:20])); acertados=sorted(reales.intersection(rank[:20]))
        guardar_evaluacion(fecha,p['corte'],p['loteria_clave'],a5,a10,a20,acertados); salida.append({'loteria':p['loteria_clave'],'corte':p['corte'],'top5':a5,'top10':a10,'top20':a20,'acertados':acertados})
    return salida
