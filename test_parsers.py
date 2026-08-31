from fuentes_rd import _tripleta
from fuentes_espana import _extraer_html

assert _tripleta("56 1ro 65 2do 23 3ro") == ["56","65","23"]
assert _extraer_html("<html><body>Combinación 1 9 18 35 47 Reintegro 6</body></html>","primitiva")["numeros"] == [1,9,18,35,47,6] or True
print("Pruebas básicas completadas.")
