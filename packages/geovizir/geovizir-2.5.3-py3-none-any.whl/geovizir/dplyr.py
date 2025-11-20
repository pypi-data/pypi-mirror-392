from pandas import DataFrame

def glimpse(df: DataFrame, max_width: int = 76):
    """Print a pandas DataFrame by columns.
    
    Print the dimensions, column names, dtypes and first few values of a
    pandas DataFrame by columns.

    Parameters
    ----------
    df : DataFrame
        The pandas DataFrame to print.

    max_width : int, optional
        The maximum width of the output, by default 76.
    """

    # find the max string lengths of the column names and dtypes for formatting
    _max_len = max([len(col) for col in df])
    _max_dtype_label_len = max([len(str(df[col].dtype)) for col in df])

    # print the dimensions of the dataframe
    print(f"{type(df)}:  {df.shape[0]} rows of {df.shape[1]} columns")

    # print the name, dtype and first few values of each column
    for _column in df:

        _col_vals = df[_column].head(max_width).to_list()
        _col_type = str(df[_column].dtype)

        output_col = f"{_column}:".ljust(_max_len+1, ' ')
        output_dtype = f" {_col_type}".ljust(_max_dtype_label_len+3, ' ')

        output_combined = f"{output_col} {output_dtype} {_col_vals}"

        # trim the output if too long
        if len(output_combined) > max_width:
            output_combined = output_combined[0:(max_width-4)] + " ..."

        print(output_combined)