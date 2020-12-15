"""
Tests for the IBGE importer
"""
import pyexcel as p
from pytest import fixture

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
        == "0191\nAgricultura, inclusive o apoio à agricultura e a pós-colheita"
    )

    assert sectors[-1] == "9700\nServiços domésticos"


def test_build_z_matrix(book):
    z_matrix = ibge.build_z_matrix(book)

    assert z_matrix
