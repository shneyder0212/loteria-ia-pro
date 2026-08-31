from collections import Counter
from memoria import obtener_resultados
from motor_ia import _quiniela_rank_desde_sorteos, _kino_rank_desde_sorteos

def medir(clave, limite=300):
    rows=obtener_resultados(clave, limite + 120)
    sorteos=[r["resultado"].get("numeros",[]) for r in rows]
    sorteos=[[str(x).zfill(2) for x in s[:3]] for s in sorteos if len(s)>=3]
    sorteos=list(reversed(sorteos))

    if len(sorteos)<60:
        return {"estado":"SIN_DATOS","muestras":len(sorteos)}

    dist={5:[0,0,0,0],10:[0,0,0,0],20:[0,0,0,0]}
    total=0
    # Test without cross-lottery radar to avoid lookahead leakage.
    for i in range(45,len(sorteos)):
        hist_newest=list(reversed(sorteos[max(0,i-180):i]))
        rank=[x["num"] for x in _quiniela_rank_desde_sorteos(hist_newest, radar=None)]
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

def medir_kino(clave='kino_leidsa', limite=300):
    rows=obtener_resultados(clave, limite+150)
    sorteos=[]
    for r in rows:
        vals=[]
        for x in r["resultado"].get("numeros",[]):
            try: n=int(x)
            except Exception: continue
            if 1<=n<=80 and n not in vals:
                vals.append(n)
        if len(vals)>=20:
            sorteos.append(vals[:20])
    sorteos=list(reversed(sorteos))

    if len(sorteos)<70:
        return {"estado":"SIN_DATOS","muestras":len(sorteos)}

    hits={10:[],15:[],20:[]}
    total=0
    for i in range(50,len(sorteos)):
        hist_newest=list(reversed(sorteos[max(0,i-220):i]))
        rank=[int(x["num"]) for x in _kino_rank_desde_sorteos(hist_newest)]
        real=set(sorteos[i])
        for k in (10,15,20):
            hits[k].append(len(real.intersection(rank[:k])))
        total+=1

    def avg(v): return round(sum(v)/len(v),2) if v else 0.0
    def pct_at_least(v,n): return round(100*sum(1 for x in v if x>=n)/len(v),2) if v else 0.0

    # Random baseline expectation: draw 20 from 80, select k => expected k*20/80 = k/4.
    out={"estado":"OK","muestras":total}
    for k in (10,15,20):
        v=hits[k]
        out[f"top{k}"]={
            "promedio_aciertos":avg(v),
            "esperado_azar":round(k/4,2),
            "4mas":pct_at_least(v,4),
            "5mas":pct_at_least(v,5),
            "6mas":pct_at_least(v,6),
            "8mas":pct_at_least(v,8),
        }
    return out
