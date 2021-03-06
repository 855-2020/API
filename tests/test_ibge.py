"""
Tests for the IBGE importer
"""
import pyexcel as p
from pytest import raises, fixture

from api import ibge

# pylint:disable=redefined-outer-name
@fixture(scope="session")
def book():
    return p.get_book(file_name="tests/Matriz_de_Insumo_Produto_2015_Nivel_67.ods")


@fixture(scope="session")
def va_book():
    return p.get_book(file_name="tests/68_tab2_2015.ods")


def test_acquire_data():
    assert ibge.acquire_data(year=2015)


def test_load_sectors(book):
    sectors = ibge.load_sectors(book)
    assert (
        sectors[0]
        == "0191 Agricultura, inclusive o apoio à agricultura e a pós-colheita"
    )

    assert sectors[-1] == "9700 Serviços domésticos"


def test_load_sheet(book):
    assert len(ibge.load_sheet(book, "03")) == 137

    with raises(Exception) as e:
        ibge.load_sheet(book, "potato")

    assert "potato" in str(e)


def test_get_national_supply_demand(book):
    supply_demand = ibge.get_national_supply_demand(book)

    assert supply_demand.shape == (127, 67)
    assert supply_demand[0, 0] == 166


def test_get_marketshare(book):
    market_share = ibge.get_marketshare(book)
    assert market_share.shape == (67, 127)
    assert market_share[0, 0] == 0.956052917723813
    assert market_share[-1, -1] == 1


def test_build_z_matrix(book, va_book):
    z_matrix = ibge.build_z_matrix(book, va_book)

    assert z_matrix
    assert len(z_matrix) == 84
    assert z_matrix[0][0] == "Matriz Z"
    assert z_matrix[0][-1] == "9700 Serviços domésticos"
    assert (
        z_matrix[1][0]
        == "0191 Agricultura, inclusive o apoio à agricultura e a pós-colheita"
    )
    assert int(z_matrix[1][1]) == 6512

    assert z_matrix[-17][0] == "9700 Serviços domésticos"
    assert z_matrix[-17][1] == 0

    assert z_matrix[-16][0] == "Importação"
    assert int(z_matrix[-16][1]) == 18895

    assert z_matrix[-15][0] == "Impostos indiretos líquidos de Subsídios"
    assert z_matrix[-15][1] == 11600

    assert z_matrix[-1][0] == "Fator trabalho (ocupações)"
    assert z_matrix[-1][1] == 5972110


def test_get_imports(book):
    imports = ibge.get_imports(book)
    assert imports[0] == 18895
    assert len(imports) == 67


def test_get_taxes(book):
    taxes = ibge.get_taxes(book)
    assert taxes[0] == 11600
    assert len(taxes) == 67


def test_added_value_loader(va_book):
    va_data = ibge.get_added_value(va_book)
    assert len(va_data[0]) == 68
    assert va_data[0][0] == "Valor adicionado bruto ( PIB )"
    assert va_data[0][1] == 163127
    assert va_data[0][-1] == 61996
    assert va_data[-1][1] == 5972110
    assert va_data[-1][-1] == 6381222
    assert va_data[0][41] == 685708
