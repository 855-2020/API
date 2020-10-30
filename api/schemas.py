"""
Pydantic schemas
"""
# pylint: disable=no-name-in-module
from pydantic import BaseModel


class Activity(BaseModel):
    """
    Activity models an economic activity

    Attributes
    ----------

    gdp : float
          The percentage of the Gross Domestic Product this
          activity is responsible for

    jobs : float
           Average number of jobs employed by this activity

    energy : float
             Amount of energy used, in Terajoules

    co2eq : float
            Amount of CO2Equivalent this activity generates

    land_usage : float
                 Area of land used by this activity, in 1000ha

    blue_water : float
                 Volume of blue water used by this activity, in 1000m³

    green_water : float
                 Volume of green water used by this activity, in 1000m³

    gray_water : float
                 Volume of gray water used by this activity, in 1000m³
    """

    gdp: float = 0
    jobs: float = 0
    energy: float = 0
    co2eq: float = 0
    land_usage: float = 0
    blue_water: float = 0
    green_water: float = 0
    gray_water: float = 0
