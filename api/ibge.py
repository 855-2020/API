"""
Adquire dados do IBGE
"""
from functools import lru_cache
import numpy as np
import pandas as pd
import pyexcel as p
from requests import get


@lru_cache(maxsize=10)
def load_sheet(book, sheet_name):
    if not isinstance(book, dict):
        book = book.to_dict()

    try:
        sheet = book[sheet_name]
    except KeyError as e:
        sheets = book.keys()
        raise Exception(
            f"Planilha {sheet_name} não encontrada! Planilhas: {list(sheets)}"
        ) from e

    return sheet


def acquire_data(year):
    """
    Given a year, downloads the corresponding data
    """
    # pylint: disable=line-too-long
    url = f"https://ftp.ibge.gov.br/Contas_Nacionais/Matriz_de_Insumo_Produto/{year}/Matriz_de_Insumo_Produto_{year}_Nivel_67.ods"
    response = get(url)
    return response.status_code == 200


def load_sectors(book):
    """
    Given a loaded pyexcel book, returns the sectors
    """
    three = load_sheet(book, "03")

    names = three[3]
    return [name.replace("\n", " ") for name in names[3:-9]]


def get_national_supply_demand(book):
    """
    Given a loaded pyexcel book, returns the supply-demand
    indices for the local market
    """
    three = load_sheet(book, "03")

    data = np.array(three)
    return data[5:-5, 3:-9].astype("float")


def get_marketshare(book):
    """
    Returns the marketshare matrix on sheet 13.
    This matrix is also called 'matrix D'
    """
    marketshare = load_sheet(book, "13")
    marketshare = np.array(marketshare)
    return marketshare[5:-3, 2:].astype("float")


def build_z_matrix(book):
    """
    Builds the Z Matrix for a given year
    """

    sectors = load_sectors(book)
    marketshare = get_marketshare(book)
    supply_demand = get_national_supply_demand(book)
    z_matrix = marketshare @ supply_demand
    data = [
        ["Matriz Z", *sectors],
        *[[s, *z_matrix[idx]] for idx, s in enumerate(sectors)],
    ]
    return data


def main():
    book = p.get_book(file_name="tests/Matriz_de_Insumo_Produto_2015_Nivel_67.ods")
    z_matrix = pd.DataFrame(build_z_matrix(book))
    z_matrix.to_excel("z_matrix.xlsx", index=False)


if __name__ == "__main__":
    main()
