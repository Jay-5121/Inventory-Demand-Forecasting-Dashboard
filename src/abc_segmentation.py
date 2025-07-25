import pandas as pd

def abc_segmentation(df, value_column, item_column, thresholds=(0.8, 0.95)):
    """
    Perform ABC segmentation on the DataFrame.
    Args:
        df: pandas DataFrame containing the data
        value_column: column name to use for value (e.g., 'TotalValue')
        item_column: column name for item identifier (e.g., 'StockCode')
        thresholds: tuple for A and B category cutoffs (default: (0.8, 0.95))
    Returns:
        DataFrame with an added 'ABC_Category' column
    """
    grouped = df.groupby(item_column)[value_column].sum().reset_index()
    grouped = grouped.sort_values(by=value_column, ascending=False)
    grouped['CumulativeSum'] = grouped[value_column].cumsum()
    grouped['CumulativePerc'] = grouped['CumulativeSum'] / grouped[value_column].sum()
    def get_category(cum_perc):
        if cum_perc <= thresholds[0]:
            return 'A'
        elif cum_perc <= thresholds[1]:
            return 'B'
        else:
            return 'C'
    grouped['ABC_Category'] = grouped['CumulativePerc'].apply(get_category)
    return grouped 