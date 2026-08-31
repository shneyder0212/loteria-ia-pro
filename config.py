from zoneinfo import ZoneInfo

TZ_RD = ZoneInfo('America/Santo_Domingo')
TZ_ES = ZoneInfo('Europe/Madrid')

SALAS = [
    ('anguila_10am','Anguila Mañana (10:00 AM)','quiniela','rd'),
    ('primera_dia','La Primera Día (12:00 PM)','quiniela','rd'),
    ('lotedom','LoteDom (12:00 PM)','quiniela','rd'),
    ('real','Lotería Real (12:55 PM)','quiniela','rd'),
    ('anguila_1pm','Anguila Mediodía (1:00 PM)','quiniela','rd'),
    ('gana_mas','Gana Más (2:30 PM)','quiniela','rd'),
    ('anguila_6pm','Anguila Tarde (6:00 PM)','quiniela','rd'),
    ('loteka','Loteka (7:55 PM)','quiniela','rd'),
    ('primera_noche','La Primera Noche (8:00 PM)','quiniela','rd'),
    ('nacional_noche','Nacional Noche (8:50 PM)','quiniela','rd'),
    ('leidsa','Leidsa (8:55 PM)','quiniela','rd'),
    ('anguila_9pm','Anguila Noche (9:00 PM)','quiniela','rd'),
    ('kino_leidsa','Super Kino TV Leidsa','kino','rd'),
    ('primitiva_esp','La Primitiva','primitiva','esp'),
    ('euromillones','Euromillones','euromillones','esp'),
]

RD_NOMBRES = {
    'anguila_10am':['Anguila 10AM','Anguila 10 AM'],
    'anguila_1pm':['Anguila 1PM','Anguila 1 PM'],
    'anguila_6pm':['Anguila 6PM','Anguila 6 PM'],
    'anguila_9pm':['Anguila 9PM','Anguila 9 PM'],
    'gana_mas':['Gana Más','Gana Mas'],
    'nacional_noche':['Loteria Nacional- Noche','Lotería Nacional Noche','Quiniela Nacional'],
    'real':['Quiniela Real','Lotería Real','Loto Real'],
    'loteka':['Quiniela Loteka','Loteka'],
    'primera_dia':['Quiniela La Primera','La Primera Día','Primera Día'],
    'primera_noche':['Quiniela La Primera Noche','La Primera Noche','Primera Noche'],
    'lotedom':['Quiniela Lotedom','LoteDom'],
    'leidsa':['Quiniela Palé','Quiniela Leidsa','Leidsa'],
    'kino_leidsa':['Super Kino TV','Súper Kino TV'],
}

CONECTATE_URLS = {
    'anguila_10am':'https://loterias.conectate.com.do/anguilla/anguila-10-am/',
    'anguila_1pm':'https://loterias.conectate.com.do/anguilla/anguila-12-pm/',
    'anguila_6pm':'https://loterias.conectate.com.do/anguilla/anguila-5-pm/',
    'anguila_9pm':'https://loterias.conectate.com.do/anguilla/anguila-9-pm/',
    'gana_mas':'https://loterias.conectate.com.do/nacional/gana-mas/',
    'nacional_noche':'https://loterias.conectate.com.do/nacional/quiniela/',
    'real':'https://loterias.conectate.com.do/loto-real/quiniela/',
    'loteka':'https://loterias.conectate.com.do/loteka/quiniela-mega-decenas/',
    'primera_dia':'https://loterias.conectate.com.do/la-primera/quiniela-medio-dia/',
    'primera_noche':'https://loterias.conectate.com.do/la-primera/quiniela-noche/',
    'lotedom':'https://loterias.conectate.com.do/lotedom/quiniela/',
    'leidsa':'https://loterias.conectate.com.do/leidsa/quiniela-pale/',
    'kino_leidsa':'https://loterias.conectate.com.do/leidsa/super-kino-tv/',
}

LOTERIA_DOMINICANA_URLS = {
    'anguila_10am':'https://www.loteriadominicana.com.do/Lottery/Anguilla',
    'anguila_1pm':'https://www.loteriadominicana.com.do/Lottery/Anguilla',
    'anguila_6pm':'https://www.loteriadominicana.com.do/Lottery/Anguilla',
    'anguila_9pm':'https://www.loteriadominicana.com.do/Lottery/Anguilla',
    'leidsa':'https://www.loteriadominicana.com.do/Lottery/Leidsa',
    'kino_leidsa':'https://www.loteriadominicana.com.do/Lottery/Leidsa',
}

CORTES_RD = {
    'manana': {'hora':5,'minuto':0,'titulo':'ESTUDIO MAÑANA','salas':['anguila_10am','primera_dia','lotedom','real','anguila_1pm'],'sincronizar_antes':'ayer'},
    'tarde': {'hora':13,'minuto':15,'titulo':'REESTUDIO TARDE','salas':['gana_mas','anguila_6pm','loteka'],'sincronizar_antes':'hoy'},
    'noche': {'hora':19,'minuto':0,'titulo':'REESTUDIO NOCTURNO','salas':['primera_noche','nacional_noche','leidsa','anguila_9pm','kino_leidsa'],'sincronizar_antes':'hoy'},
}

SYNC_JOBS_RD = [
    (10,10,['anguila_10am']),
    (12,10,['primera_dia','lotedom']),
    (13,5,['real','anguila_1pm']),
    (14,40,['gana_mas']),
    (18,10,['anguila_6pm']),
    (20,5,['loteka','primera_noche']),
    (21,10,['nacional_noche','leidsa','anguila_9pm','kino_leidsa']),
    (21,30,['nacional_noche','leidsa','anguila_9pm','kino_leidsa']),
]
