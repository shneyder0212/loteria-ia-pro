from backtesting import medir
from motor_ia import analizar_quiniela

MIN_MUESTRAS = 80
MIN_SCORE_TOP1 = 68.0
MIN_SCORE_PROM_TOP3 = 60.0
MIN_TOP10_2MAS = 8.0

def evaluar_alerta_roja(clave):
    analisis = analizar_quiniela(clave)
    if analisis.get("estado") != "OK":
        return {
            "activa": False,
            "motivo": "Memoria insuficiente",
            "muestras": analisis.get("muestras", 0),
        }

    ranking = analisis.get("ranking", [])
    if len(ranking) < 3:
        return {"activa": False, "motivo": "Ranking insuficiente"}

    bt = medir(clave, 300)
    if bt.get("estado") != "OK":
        return {
            "activa": False,
            "motivo": "Backtesting insuficiente",
            "muestras": bt.get("muestras", 0),
        }

    muestras = min(analisis.get("muestras", 0), bt.get("muestras", 0))
    top3 = ranking[:3]
    score_top1 = float(top3[0]["score"])
    score_prom = sum(float(x["score"]) for x in top3) / 3.0
    top10_2mas = float(bt["top10"]["2mas"])

    razones_unicas = set()
    for item in top3:
        for r in item.get("razones", []):
            razones_unicas.add(r)

    suficientes_senales = len(razones_unicas) >= 4
    cumple = (
        muestras >= MIN_MUESTRAS
        and score_top1 >= MIN_SCORE_TOP1
        and score_prom >= MIN_SCORE_PROM_TOP3
        and top10_2mas >= MIN_TOP10_2MAS
        and suficientes_senales
    )

    return {
        "activa": bool(cumple),
        "numeros": [x["num"] for x in top3],
        "pale": [top3[0]["num"], top3[1]["num"]],
        "tripleta": [x["num"] for x in top3],
        "score_top1": round(score_top1, 2),
        "score_prom_top3": round(score_prom, 2),
        "top10_2mas_backtest": top10_2mas,
        "muestras": muestras,
        "senales": sorted(razones_unicas)[:8],
        "motivo": (
            "Coinciden memoria, score, señales y backtesting"
            if cumple else
            "No alcanza todos los filtros de seguridad estadística"
        )
    }
