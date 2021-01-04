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


def load_sheet_slice(book, sheet_name, slice_, target_type="float"):
    """
    Given a loaded Pyexcel book, its sheet name and a valid
    Numpy slice, returns the data inside that slice as a
    Numpy Array

    Args:
        book (`pyexcel.Book`): A loaded `Matriz de Insumo Produto` notebook
        sheet_name (`str`): The sheet's name
        slice_ (`tuple`): A valid numpy slice, as returned by `numpy.s_`
    """
    data = load_sheet(book, sheet_name)
    data = np.array(data)

    if target_type:
        return data[slice_].astype(target_type)

    return data[slice_]


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
    return load_sheet_slice(book, "03", np.s_[5:-5, 3:-9])


def get_marketshare(book):
    """
    Returns the marketshare matrix on sheet 13.
    This matrix is also called 'matrix D'
    """
    return load_sheet_slice(book, "13", np.s_[5:-3, 2:])


def get_imports(book):
    """
    Returns the total imports for a given data. This is equal to line
    134, tab 04 of 'Matriz Insumo Produto'.

    Args:
        book (`pyexcel.Book`): A loaded `Matriz de Insumo Produto` notebook
    """
    return load_sheet_slice(book, "04", np.s_[133, 3:-9])


def get_taxes(book):
    """
    Returns the total taxes for a given data. This is equal to line
    134, tab 05 plus L134 of tab 06 of 'Matriz Insumo Produto'.

    Args:
        book (`pyexcel.Book`): A loaded `Matriz de Insumo Produto` notebook
    """
    internal_taxes = load_sheet_slice(book, "05", np.s_[133, 3:-9])
    import_taxes = load_sheet_slice(book, "06", np.s_[133, 3:-9])
    return internal_taxes + import_taxes


def get_added_value(va_book):
    operations_titles = load_sheet_slice(va_book, "VA", np.s_[5:-5, 0], target_type=str)
    return np.array([operations_titles])


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
    imports = get_imports(book)
    data.append(["Importação", *imports])

    taxes = get_taxes(book)
    data.append(["Impostos indiretos líquidos de Subsídios", *taxes])

    return data


def main():
    book = p.get_book(file_name="tests/Matriz_de_Insumo_Produto_2015_Nivel_67.ods")
    z_matrix = pd.DataFrame(build_z_matrix(book))
    z_matrix.to_excel("z_matrix.xlsx", index=False)


if __name__ == "__main__":
    main()
