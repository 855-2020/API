"""
Adquire dados do IBGE
"""
from requests import get


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
    if not isinstance(book, dict):
        book = book.to_dict()

    try:
        three = book["03"]
    except KeyError as e:
        sheets = book.keys()
        raise Exception(f"Planilha 03 não encontrada! Planilhas: {list(sheets)}") from e

    names = three[3]
    return names[3:-9]


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
