from collections import Counter
from memoria import obtener_ultimos_rd

def reves(n):
    return str(n).zfill(2)[::-1]

def radar_rd(excluir_clave=None, limite=40):
    rows=obtener_ultimos_rd(limite)
    recientes=[]
    for r in rows:
        if excluir_clave and r.get('loteria_clave')==excluir_clave:
            continue
        nums=[str(x).zfill(2) for x in r.get('resultado',{}).get('numeros',[])[:3]]
        if nums:
            recientes.append({
                'loteria':r.get('loteria_clave'),
                'fecha':r.get('fecha'),
                'numeros':nums
            })

    if not recientes:
        return {'estado':'SIN_DATOS','puntos':{},'razones':{}}

    # Weights decay by capture order. This is a radar, not a probability.
    puntos=Counter()
    razones={}
    for idx,item in enumerate(recientes[:20]):
        peso=max(0.5, 4.0-(idx*0.15))
        for n in item['numeros']:
            puntos[n]+=peso
            razones.setdefault(n,[]).append(f"visto en {item['loteria']}")
            rv=reves(n)
            if rv!=n:
                puntos[rv]+=peso*0.55
                razones.setdefault(rv,[]).append(f"revés de {n} visto en {item['loteria']}")
            # same terminal, weaker contribution
            for d in range(10):
                cand=f"{d}{n[-1]}"
                if cand!=n:
                    puntos[cand]+=peso*0.08

    maxp=max(puntos.values()) if puntos else 1.0
    norm={n:round(v/maxp,4) for n,v in puntos.items()}
    return {'estado':'OK','puntos':norm,'razones':razones,'muestras':len(recientes)}
