from collections import Counter, defaultdict
from memoria import obtener_resultados

def reves(n):
    s=str(n).zfill(2)
    return s[::-1]

def analizar_quiniela(clave):
    rows=obtener_resultados(clave,3000)
    sorteos=[r["resultado"].get("numeros",[]) for r in rows]
    sorteos=[[str(x).zfill(2) for x in s[:3]] for s in sorteos if len(s)>=3]

    if len(sorteos)<20:
        return {"estado":"SIN_DATOS","muestras":len(sorteos),
                "mensaje":"Se necesitan al menos 20 resultados verificados."}

    cron=list(reversed(sorteos))
    freq30=Counter(x for s in sorteos[:30] for x in s)
    freq90=Counter(x for s in sorteos[:90] for x in s)
    freq=Counter(x for s in sorteos for x in s)
    trans=defaultdict(Counter)
    co=defaultdict(Counter)
    ultima={f"{i:02d}":None for i in range(100)}

    for i,s in enumerate(cron):
        for x in s: ultima[x]=i
        for a in s:
            for b in s:
                if a!=b: co[a][b]+=1
        if i:
            for a in cron[i-1]:
                for b in s: trans[a][b]+=1

    ultimo=sorteos[0]
    max30=max(freq30.values()) if freq30 else 1
    max90=max(freq90.values()) if freq90 else 1
    maxf=max(freq.values()) if freq else 1
    lastidx=len(cron)-1
    ranking=[]

    for i in range(100):
        n=f"{i:02d}"
        score=(freq30[n]/max30)*25 + (freq90[n]/max90)*15 + (freq[n]/maxf)*8
        razones=[]

        atraso=len(cron) if ultima[n] is None else lastidx-ultima[n]
        score+=min(atraso/20,1)*10
        if atraso>=10: razones.append(f"atraso {atraso}")

        rv=reves(n)
        if rv in ultimo and rv!=n:
            score+=12; razones.append(f"revés de {rv}")

        tc=sum(trans[b][n] for b in ultimo)
        tt=sum(sum(trans[b].values()) for b in ultimo) or 1
        bonus=min(20,(tc/tt)*250)
        score+=bonus
        if bonus>=5: razones.append("atracción temporal")

        cc=sum(co[b][n] for b in ultimo)
        bco=min(8,cc/4)
        score+=bco
        if bco>=2: razones.append("coaparición")

        if any(x[-1]==n[-1] for x in ultimo):
            score+=5; razones.append(f"terminal {n[-1]}")
        if any(x[0]==n[0] for x in ultimo):
            score+=4; razones.append(f"decena {n[0]}0-{n[0]}9")

        ranking.append({"num":n,"score":round(score,2),"razones":razones[:5]})

    ranking.sort(key=lambda x:x["score"],reverse=True)
    return {"estado":"OK","muestras":len(sorteos),"ultimo":ultimo,"ranking":ranking[:20]}
