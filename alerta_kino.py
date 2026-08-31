from motor_ia import analizar_kino
from backtesting import medir_kino

def evaluar_alerta_kino(clave='kino_leidsa'):
    a=analizar_kino(clave)
    if a.get('estado')!='OK':
        return {'activa':False,'motivo':'Memoria Kino insuficiente','muestras':a.get('muestras',0)}
    bt=medir_kino(clave,300)
    if bt.get('estado')!='OK':
        return {'activa':False,'motivo':'Backtesting Kino insuficiente','muestras':bt.get('muestras',0)}

    t10=bt['top10']
    # Require evidence above the random expected hit count, not just a high internal score.
    ventaja=t10['promedio_aciertos']-t10['esperado_azar']
    top=a['ranking'][:10]
    señales=len({r for x in top[:5] for r in x.get('razones',[])})
    activa=(
        bt['muestras']>=100 and
        ventaja>=0.30 and
        t10['5mas']>=8.0 and
        señales>=3
    )
    return {
        'activa':activa,
        'nucleo_5':a.get('nucleo_5',[]),
        'jugada_10':a.get('jugada_10',[]),
        'muestras':bt['muestras'],
        'promedio_top10':t10['promedio_aciertos'],
        'esperado_azar':t10['esperado_azar'],
        'ventaja_media':round(ventaja,2),
        '5mas_pct':t10['5mas'],
        'senales':señales,
        'motivo':'Ventaja histórica medida sobre referencia aleatoria' if activa else 'No supera todos los filtros Kino'
    }
