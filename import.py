from io import BytesIO
from os.path import isfile
from zipfile import ZipFile

import requests

from api import models
from api.database import *
from api.ibge import *

year = 2015


def download(file):
    name = file.split('/')[-1]
    if isfile(name):
        return
    req = requests.get(file, stream=True)
    with open(name, 'wb') as fh:
        for chunk in req.iter_content(chunk_size=1024):
            fh.write(chunk)


def download_and_extract(container, file):
    name = file.split('/')[-1]
    if isfile(name):
        return
    req = requests.get(container, stream=True)
    with ZipFile(BytesIO(req.content)) as zf:
        with zf.open(file, 'r') as fr:
            with open(name, 'wb') as fw:
                fw.write(fr.read())


download(
    f"https://ftp.ibge.gov.br/Contas_Nacionais/Matriz_de_Insumo_Produto/{year}/Matriz_de_Insumo_Produto_{year}_Nivel_67.ods")
download_and_extract(
    f"https://ftp.ibge.gov.br/Contas_Nacionais/Sistema_de_Contas_Nacionais/{year}/tabelas_ods/tabelas_de_recursos_e_usos/nivel_68_2010_{year}_ods.zip",
    f"nivel68_2010_2015_ods/68_tab2_{year}.ods")

book = p.get_book(file_name=f"Matriz_de_Insumo_Produto_{year}_Nivel_67.ods")
va_book = p.get_book(file_name=f"68_tab2_{year}.ods")

db = SessionLocal()

sectors = load_sectors(book)
added_value = get_added_value(va_book)
marketshare = get_marketshare(book)
supply_demand = get_national_supply_demand(book)
taxes = get_taxes(book)
imports = get_imports(book)

z_matrix = marketshare @ supply_demand
sectors = list(zip(sectors, added_value[len(added_value) - 2][1:]))
I = np.eye(z_matrix.shape[0])
va = np.repeat(np.array([added_value[-2][1:]]), z_matrix.shape[0], axis=0)
a_matrix = z_matrix / va
l_matrix = np.linalg.inv(I - a_matrix)

cats = ["Importação", "Impostos indiretos líquidos de Subsídios"] + list(map(lambda a: a[0].strip(), added_value))
cats_val = np.array([imports.tolist(), taxes.tolist()] + list(map(lambda a: a[1:], added_value)))
cats_val /= np.repeat(np.array([added_value[-2][1:]]), len(cats), axis=0)

nmodel = models.Model(name=f"IBGE {year}", economic_matrix=a_matrix, leontief_matrix=l_matrix, catimpct_matrix=cats_val)
# noinspection PyUnresolvedReferences
nmodel.sectors.extend(models.Sector(name=x[1][0], pos=x[0], value_added=x[1][1]) for x in enumerate(sectors))
# noinspection PyUnresolvedReferences
nmodel.categories.extend(models.Category(name=x[1], pos=x[0], description=x[1], unit='none') for x in enumerate(cats))

db.add(nmodel)
db.commit()
db.flush()
