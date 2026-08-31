from collections import Counter
from memoria import obtener_resultados

def medir(clave, limite=300):
    rows=obtener_resultados(clave, limite + 100)
    sorteos=[r["resultado"].get("numeros",[]) for r in rows]
    sorteos=[[str(x).zfill(2) for x in s[:3]] for s in sorteos if len(s)>=3]
    sorteos=list(reversed(sorteos))

    if len(sorteos)<40:
        return {"estado":"SIN_DATOS","muestras":len(sorteos)}

    dist={5:[0,0,0,0],10:[0,0,0,0],20:[0,0,0,0]}
    total=0
    for i in range(30,len(sorteos)):
        hist=sorteos[max(0,i-90):i]
        f=Counter(x for s in hist for x in s)
        rank=[n for n,_ in f.most_common(20)]
        real=set(sorteos[i])
        for k in (5,10,20):
            a=min(3,len(real.intersection(rank[:k])))
            dist[k][a]+=1
        total+=1

    def pct(x): return round(100*x/total,2) if total else 0.0
    return {
        "estado":"OK","muestras":total,
        "top5":{"2mas":pct(dist[5][2]+dist[5][3]),"3":pct(dist[5][3])},
        "top10":{"2mas":pct(dist[10][2]+dist[10][3]),"3":pct(dist[10][3])},
        "top20":{"2mas":pct(dist[20][2]+dist[20][3]),"3":pct(dist[20][3])}
    }
