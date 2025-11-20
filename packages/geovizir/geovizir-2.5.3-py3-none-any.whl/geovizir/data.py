import wbgapi as wb
import pandas as pd

# Fix for Python >= 3.10 until wbdata is updated
import collections
collections.Sequence = collections.abc.Sequence

def get_data(indicator: str, year: int) -> pd.DataFrame:
    """Get data from the World Bank API

    Parameters
    ----------
    indicator : str
        Indicator code
    year : int
        Year

    Returns
    -------
    pandas.DataFrame
        Dataframe with the data
    """
    data = wb.data.DataFrame(indicator, "all", year, labels=True)
    data.reset_index(inplace=True)
    data.rename(columns={indicator: "value", "Country": "country", "economy": "iso3c"}, inplace=True)
    data["date"] = year
    data["indicator"] = indicator

    return data

def get_data_most_recent(indicator: str) -> pd.DataFrame:
    """Get the data from the World Bank API 
    with the most recent year available there

    Parameters
    ----------
    indicator : str
        Indicator code

    Returns
    -------
    pandas.DataFrame
        Dataframe with the data
    """
    # Get all the years available
    data = wb.data.DataFrame(indicator, "all", labels=True)
    data.reset_index(inplace=True)

    # Pivot the columns that start with YR changing the name to the year
    data = data.melt(id_vars=["Country", "economy"], var_name="date", value_name="value")
    data["date"] = data["date"].str.extract(r"YR(\d{4})").astype(int)

    # filter out NaN values from column value
    data = data.dropna(subset=["value"])
    data.rename(columns={"Country": "country", "economy": "iso3c"}, inplace=True)

    # Group by country and keep the most recent year where value isn't NaN
    data_clean = data.sort_values("date", ascending=False).groupby("country").first().reset_index()

    return data_clean
