"""
Adquire dados do IBGE
"""
from functools import lru_cache
import numpy as np
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
    return data[5:-5, 3:-9]


def build_z_matrix(book):
    """
    Builds the Z Matrix for a given year
    """

    sectors = load_sectors(book)
    data = [["Matriz Z", *sectors], *[[s] for s in sectors]]
    return data


def main():
    print("Hey oh")


if __name__ == "__main__":
    main()
