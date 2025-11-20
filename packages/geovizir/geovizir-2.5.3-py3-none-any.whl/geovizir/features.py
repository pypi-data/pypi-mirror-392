from geopandas import read_file, GeoDataFrame
from pathlib import Path

def load_data(folder, filepath):
    # Construct the full path to the shapefile
    full_path = Path(__file__).parent / 'resources' / folder / filepath
    
    # Ensure the file exists
    if not full_path.exists():
        raise FileNotFoundError(f"File not found: {full_path}")

    # Read the shapefile using geopandas
    return read_file(str(full_path))

def ne_countries(scale: int = 10) -> GeoDataFrame:
    """Return a GeoDataFrame of the world countries.
    
    Download the world countries shapefile from Natural Earth and
    return a GeoDataFrame of the countries.

    Parameters
    ----------
    scale : int, optional
        The scale of the shapefile, by default 10. The allowed values are
        10, 50 and 110.

    Returns
    -------
    GeoDataFrame
        A table of the world countries.
    """
    # Check if scale is one of the allowed values (10, 50, 110)
    if scale not in [10, 50, 110]:
        raise ValueError('Scale must be one of 10, 50, 110')

    folder = "ne_" + str(scale) + "m_admin_0_countries"
    filepath = "ne_" + str(scale) + "m_admin_0_countries.shp"

    # Read the shapefile using geopandas
    return load_data(folder, filepath)

def ne_states(state: str, scale: int = 10) -> GeoDataFrame:
    """Return a GeoDataFrame of the stats of a country.
    
    Download the counties shapefile from Natural Earth and
    return a GeoDataFrame of the countries.

    Parameters
    ----------
    state : str
        The country ISO3 code.

    scale : int, optional
        The scale of the shapefile, by default 10. The allowed values are
        10, 50 and 110.

    Returns
    -------
    GeoDataFrame
        A table of the world countries.
    """
    # Check if scale is one of the allowed values (10, 50, 110)
    if scale not in [10, 50, 110]:
        raise ValueError('Scale must be one of 10, 50, 110')

    folder = "ne_" + str(scale) + "m_admin_1_states_provinces"
    filepath = "ne_" + str(scale) + "m_admin_1_states_provinces.shp"
    shpfilename = load_data(folder, filepath)

    states = shpfilename[shpfilename['adm0_a3'] == state]

    # Read the shapefile using geopandas
    return states
