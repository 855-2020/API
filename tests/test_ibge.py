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


def test_build_z_matrix(book):
    z_matrix = ibge.build_z_matrix(book)

    assert z_matrix
    assert len(z_matrix) == 68
    assert z_matrix[0][0] == "Matriz Z"
    assert z_matrix[0][-1] == "9700 Serviços domésticos"
    assert (
        z_matrix[1][0]
        == "0191 Agricultura, inclusive o apoio à agricultura e a pós-colheita"
    )
    assert z_matrix[-1][0] == "9700 Serviços domésticos"
