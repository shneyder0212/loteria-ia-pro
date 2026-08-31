from collections import Counter, defaultdict
from memoria import obtener_resultados
from radar_global import radar_rd

def reves(n):
    return str(n).zfill(2)[::-1]

def _normal(v,m):
    return (v/m) if m else 0.0

def _quiniela_rank_desde_sorteos(sorteos, radar=None):
    # sorteos newest -> oldest, each 3 two-digit strings
    nums=[f'{i:02d}' for i in range(100)]
    cron=list(reversed(sorteos))
    ventanas={}
    for w in (7,15,30,60,90):
        ventanas[w]=Counter(x for s in sorteos[:w] for x in s)
    total=Counter(x for s in sorteos for x in s)

    pos=[Counter(),Counter(),Counter()]
    for s in sorteos:
        for i,x in enumerate(s[:3]):
            pos[i][x]+=1

    trans1=defaultdict(Counter)
    trans2=defaultdict(Counter)
    co=defaultdict(Counter)
    ultima={n:None for n in nums}

    for i,s in enumerate(cron):
        for x in s:
            ultima[x]=i
        for a in s:
            for b in s:
                if a!=b:
                    co[a][b]+=1
        if i>=1:
            for a in cron[i-1]:
                for b in s:
                    trans1[a][b]+=1
        if i>=2:
            for a in cron[i-2]:
                for b in s:
                    trans2[a][b]+=1

    ultimo=sorteos[0]
    penultimo=sorteos[1] if len(sorteos)>1 else []
    last=len(cron)-1
    maxima={w:(max(c.values()) if c else 1) for w,c in ventanas.items()}
    max_total=max(total.values()) if total else 1
    max_pos=[max(c.values()) if c else 1 for c in pos]

    ranking=[]
    for n in nums:
        score=0.0
        razones=[]

        # Recent windows: recent data matters more, but historical stability remains.
        contributions = [
            (7,14),(15,13),(30,12),(60,8),(90,6)
        ]
        for w,peso in contributions:
            s=_normal(ventanas[w][n],maxima[w])*peso
            score+=s
            if w in (7,15) and s >= peso*0.72:
                razones.append(f"fuerte {w} sorteos")

        hist=_normal(total[n],max_total)*5
        score+=hist

        # Position behavior across 1st/2nd/3rd.
        pvals=[_normal(pos[i][n],max_pos[i]) for i in range(3)]
        pos_bonus=max(pvals)*8
        score+=pos_bonus
        if pos_bonus>=5.8:
            razones.append(f"posición {pvals.index(max(pvals))+1} fuerte")

        atraso=len(cron) if ultima[n] is None else last-ultima[n]
        atraso_bonus=min(atraso/25,1)*8
        score+=atraso_bonus
        if atraso>=12:
            razones.append(f"atraso {atraso}")

        rv=reves(n)
        if rv in ultimo and rv!=n:
            score+=10
            razones.append(f"revés de {rv}")

        # One- and two-step transitions from latest results.
        tc1=sum(trans1[b][n] for b in ultimo)
        tt1=sum(sum(trans1[b].values()) for b in ultimo) or 1
        b1=min(14,(tc1/tt1)*230)
        score+=b1
        if b1>=4.5:
            razones.append("atracción 1 paso")

        tc2=sum(trans2[b][n] for b in penultimo)
        tt2=sum(sum(trans2[b].values()) for b in penultimo) or 1
        b2=min(8,(tc2/tt2)*180)
        score+=b2
        if b2>=3.5:
            razones.append("atracción 2 pasos")

        cc=sum(co[b][n] for b in ultimo)
        co_bonus=min(7,cc/4.0)
        score+=co_bonus
        if co_bonus>=2.5:
            razones.append("coaparición")

        if any(x[-1]==n[-1] for x in ultimo):
            score+=4
            razones.append(f"terminal {n[-1]}")
        if any(x[0]==n[0] for x in ultimo):
            score+=3
            razones.append(f"decena {n[0]}0-{n[0]}9")

        # Digit relations: sum and mirrored digits, weak signal only.
        dsum=int(n[0])+int(n[1])
        if any((int(x[0])+int(x[1]))==dsum for x in ultimo):
            score+=1.8
            razones.append("suma de dígitos activa")

        if radar and radar.get('estado')=='OK':
            rp=float(radar.get('puntos',{}).get(n,0))
            if rp:
                score+=rp*7
                if rp>=0.45:
                    razones.append("radar entre loterías")

        ranking.append({
            'num':n,
            'score':round(score,2),
            'razones':list(dict.fromkeys(razones))[:7],
            'atraso':atraso,
            'f7':ventanas[7][n],
            'f15':ventanas[15][n],
            'f30':ventanas[30][n],
        })

    ranking.sort(key=lambda x:(x['score'],x['f7'],x['f15'],x['f30']), reverse=True)
    return ranking

def analizar_quiniela(clave):
    rows=obtener_resultados(clave,3000)
    sorteos=[]
    for r in rows:
        s=r['resultado'].get('numeros',[])
        if len(s)>=3:
            sorteos.append([str(x).zfill(2) for x in s[:3]])
    if len(sorteos)==0:
        return {'estado':'SIN_DATOS','muestras':0,'mensaje':'Todavía no hay resultados verificados.'}

    radar=radar_rd(excluir_clave=clave)
    ranking=_quiniela_rank_desde_sorteos(sorteos,radar)

    if len(sorteos) < 5:
        modo='MEMORIA_MINIMA'
        confianza='MUY BAJA'
    elif len(sorteos) < 25:
        modo='PROVISIONAL'
        confianza='BAJA'
    elif len(sorteos) < 80:
        modo='COMPLETO'
        confianza='MEDIA'
    else:
        modo='MADURO'
        confianza='ALTA'

    return {
        'estado':'OK',
        'modo':modo,
        'confianza':confianza,
        'muestras':len(sorteos),
        'ultimo':sorteos[0],
        'ranking':ranking[:30],
        'radar_global':radar.get('muestras',0) if radar else 0
    }

def _kino_rank_desde_sorteos(sorteos):
    # sorteos newest -> oldest, 20 numbers each
    universe=range(1,81)
    f10=Counter(x for s in sorteos[:10] for x in s)
    f20=Counter(x for s in sorteos[:20] for x in s)
    f50=Counter(x for s in sorteos[:50] for x in s)
    f100=Counter(x for s in sorteos[:100] for x in s)
    ft=Counter(x for s in sorteos for x in s)

    last_seen={n:None for n in universe}
    cron=list(reversed(sorteos))
    pair=defaultdict(Counter)
    trans=defaultdict(Counter)
    repeat=Counter()

    for i,s in enumerate(cron):
        ss=set(s)
        for n in ss:
            last_seen[n]=i
        for a in ss:
            for b in ss:
                if a!=b:
                    pair[a][b]+=1
        if i:
            prev=set(cron[i-1])
            for a in prev:
                for b in ss:
                    trans[a][b]+=1
            for n in ss.intersection(prev):
                repeat[n]+=1

    maxima=[
        max(f10.values()) if f10 else 1,
        max(f20.values()) if f20 else 1,
        max(f50.values()) if f50 else 1,
        max(f100.values()) if f100 else 1,
        max(ft.values()) if ft else 1,
        max(repeat.values()) if repeat else 1,
    ]
    ultimo=sorteos[0]
    lastidx=len(cron)-1
    rank=[]

    for n in universe:
        score=(
            _normal(f10[n],maxima[0])*22 +
            _normal(f20[n],maxima[1])*18 +
            _normal(f50[n],maxima[2])*14 +
            _normal(f100[n],maxima[3])*8 +
            _normal(ft[n],maxima[4])*5
        )
        razones=[]
        if _normal(f10[n],maxima[0])>=0.78:
            razones.append("fuerte últimos 10")
        if _normal(f20[n],maxima[1])>=0.78:
            razones.append("fuerte últimos 20")

        atraso=len(cron) if last_seen[n] is None else lastidx-last_seen[n]
        # In Kino, huge "delay" shouldn't dominate because 20/80 are drawn each event.
        score+=min(atraso/8,1)*5
        if atraso>=4:
            razones.append(f"atraso {atraso}")

        rep=_normal(repeat[n],maxima[5])*7
        score+=rep
        if rep>=4.5:
            razones.append("repetidor histórico")

        # companions with latest draw
        pc=sum(pair[a][n] for a in ultimo if a!=n)
        pair_bonus=min(12,pc/18.0)
        score+=pair_bonus
        if pair_bonus>=4:
            razones.append("compañeros fuertes")

        tc=sum(trans[a][n] for a in ultimo)
        tt=sum(sum(trans[a].values()) for a in ultimo) or 1
        tr_bonus=min(9,(tc/tt)*900)
        score+=tr_bonus
        if tr_bonus>=3:
            razones.append("transición activa")

        # range balance signal is weak: encourage ranges represented recently.
        tramo=(n-1)//10
        tramo_count=sum(1 for x in ultimo if (x-1)//10==tramo)
        if tramo_count>=2:
            score+=2
            razones.append(f"tramo {tramo*10+1:02d}-{tramo*10+10:02d}")

        rank.append({
            'num':f'{n:02d}',
            'score':round(score,2),
            'razones':list(dict.fromkeys(razones))[:6],
            'atraso':atraso,
            'f10':f10[n],
            'f20':f20[n]
        })

    rank.sort(key=lambda x:(x['score'],x['f10'],x['f20']), reverse=True)
    return rank

def analizar_kino(clave='kino_leidsa'):
    rows=obtener_resultados(clave,2500)
    sorteos=[]
    for r in rows:
        vals=[]
        for x in r['resultado'].get('numeros',[]):
            try:
                n=int(x)
            except Exception:
                continue
            if 1<=n<=80 and n not in vals:
                vals.append(n)
        if len(vals)>=20:
            sorteos.append(vals[:20])

    if len(sorteos)==0:
        return {'estado':'SIN_DATOS','muestras':0,'mensaje':'Todavía no hay resultados de Kino verificados.'}

    if len(sorteos) < 10:
        modo='MEMORIA_MINIMA'
        confianza='MUY BAJA'
    elif len(sorteos) < 30:
        modo='PROVISIONAL'
        confianza='BAJA'
    elif len(sorteos) < 100:
        modo='COMPLETO'
        confianza='MEDIA'
    else:
        modo='MADURO'
        confianza='ALTA'

    rank=_kino_rank_desde_sorteos(sorteos)
    top10=[x['num'] for x in rank[:10]]
    top15=[x['num'] for x in rank[:15]]
    top20=[x['num'] for x in rank[:20]]

    # Build a "nucleus" and a diversified 10-number card across ranges.
    nucleo=top10[:5]
    seleccion=[]
    used_ranges=Counter()
    for item in rank:
        n=int(item['num'])
        rg=(n-1)//10
        if used_ranges[rg] < 2:
            seleccion.append(item['num'])
            used_ranges[rg]+=1
        if len(seleccion)==10:
            break
    if len(seleccion)<10:
        for n in top10:
            if n not in seleccion:
                seleccion.append(n)
            if len(seleccion)==10:
                break

    return {
        'estado':'OK',
        'modo':modo,
        'confianza':confianza,
        'muestras':len(sorteos),
        'ranking':rank[:30],
        'nucleo_5':nucleo,
        'jugada_10':seleccion,
        'top15':top15,
        'top20':top20,
        'ultimo':[f'{x:02d}' for x in sorteos[0]]
    }

def analizar_bolas(clave,max_num,cantidad):
    rows=obtener_resultados(clave,2000)
    sorteos=[]
    for r in rows:
        vals=[]
        for x in r['resultado'].get('numeros',[]):
            try:
                n=int(x)
            except Exception:
                continue
            if 1<=n<=max_num and n not in vals:
                vals.append(n)
        if len(vals)>=cantidad:
            sorteos.append(vals[:cantidad])
    if len(sorteos)==0:
        return {'estado':'SIN_DATOS','muestras':0,'mensaje':'Todavía no hay sorteos verificados.'}
    f15=Counter(x for s in sorteos[:15] for x in s)
    f30=Counter(x for s in sorteos[:30] for x in s)
    f90=Counter(x for s in sorteos[:90] for x in s)
    ft=Counter(x for s in sorteos for x in s)
    m15=max(f15.values()) if f15 else 1
    m30=max(f30.values()) if f30 else 1
    m90=max(f90.values()) if f90 else 1
    mf=max(ft.values()) if ft else 1
    rank=[]
    for n in range(1,max_num+1):
        score=(_normal(f15[n],m15)*35+_normal(f30[n],m30)*30+_normal(f90[n],m90)*20+_normal(ft[n],mf)*15)
        reasons=[]
        if _normal(f15[n],m15)>.75: reasons.append("fuerte 15 sorteos")
        if _normal(f30[n],m30)>.75: reasons.append("fuerte 30 sorteos")
        rank.append({'num':f'{n:02d}','score':round(score,2),'razones':reasons or ['frecuencia multi-ventana']})
    rank.sort(key=lambda x:x['score'],reverse=True)
    if len(sorteos) < 5:
        modo='MEMORIA_MINIMA'; confianza='MUY BAJA'
    elif len(sorteos) < 20:
        modo='PROVISIONAL'; confianza='BAJA'
    elif len(sorteos) < 60:
        modo='COMPLETO'; confianza='MEDIA'
    else:
        modo='MADURO'; confianza='ALTA'
    return {'estado':'OK','modo':modo,'confianza':confianza,'muestras':len(sorteos),'ranking':rank[:30],'seleccion':[x['num'] for x in rank[:cantidad]]}
