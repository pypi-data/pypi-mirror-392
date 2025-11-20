from pandas import Series

def label_bins(bins: list[int, float]) -> list[str]:
    """Return a list of labels for a list of bins.
    
    For each element of the bins, an interval is created with 
    the previous element. The first element is add as '< first_element'
    and the last element as '> last_element'.

    Parameters
    ----------
    bins : list[float, int]
        A list of bins to be labeled.

    Returns
    -------
    list[str]
        A list of labels.

    Examples
    --------
    >>> bins([1,2,3])    
    """
    return [f'< {bins[0]}', *(f'{a}-{b}' for a, b in zip(bins[:-1], bins[1:])), f'> {bins[-1]}']

def relabel_bins(column: Series):
    """Relabel a column with the bins of the column.

    Parameters
    ----------
    column : Series
        A column to be relabeled.

    Returns
    -------
    Series
        A column with the labels of the bins.
    """
    
    categories = column.cat.categories.tolist()

    for cat in categories:
        column = column.cat.rename_categories({cat: f'{cat.left} - {cat.right}'})
    
    return column
