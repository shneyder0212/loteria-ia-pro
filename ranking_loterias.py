from config import SALAS
from backtesting import medir

def _razones(reciente, largo):
    r=[]
    if reciente["top5"]["2mas"] >= largo["top5"]["2mas"]:
        r.append("Top 5 reciente estable o mejorando")
    if reciente["top10"]["2mas"] >= largo["top10"]["2mas"]:
        r.append("Top 10 reciente estable o mejorando")
    if reciente["top5"]["3"] > 0:
        r.append("registra triples en Top 5")
    elif reciente["top10"]["3"] > 0:
        r.append("registra triples en Top 10")
    if largo["muestras"] >= 150:
        r.append("muestra histórica amplia")
    return r[:3] or ["rendimiento relativo superior en backtesting"]

def ranking_mejores_loterias():
    candidatos=[]
    # Solo comparamos quinielas RD entre sí. Primitiva/Euromillones tienen reglas diferentes.
    for clave,nombre,tipo,region in SALAS:
        if tipo!="quiniela":
            continue

        reciente=medir(clave,120)
        largo=medir(clave,300)
        if reciente.get("estado")!="OK" or largo.get("estado")!="OK":
            continue

        # Favorece 2+ aciertos, luego triples, y exige que el rendimiento exista
        # tanto recientemente como en una ventana más larga.
        score_bruto=(
            reciente["top5"]["2mas"]*0.32 +
            reciente["top10"]["2mas"]*0.23 +
            largo["top5"]["2mas"]*0.18 +
            largo["top10"]["2mas"]*0.12 +
            reciente["top5"]["3"]*0.08 +
            reciente["top10"]["3"]*0.04 +
            largo["top10"]["3"]*0.03
        )
        estabilidad=max(
            0.0,
            1.0 - abs(reciente["top10"]["2mas"]-largo["top10"]["2mas"])/100.0
        )
        confianza=min(1.0, largo["muestras"]/200.0)
        score=round(score_bruto*estabilidad*confianza,2)

        candidatos.append({
            "clave":clave,
            "nombre":nombre,
            "score_estudio":score,
            "muestras":largo["muestras"],
            "reciente":reciente,
            "historico":largo,
            "razones":_razones(reciente,largo)
        })

    candidatos.sort(key=lambda x:(x["score_estudio"],x["muestras"]), reverse=True)
    return {
        "estado":"OK" if candidatos else "SIN_DATOS",
        "mejor":candidatos[0] if candidatos else None,
        "ranking":candidatos
    }
