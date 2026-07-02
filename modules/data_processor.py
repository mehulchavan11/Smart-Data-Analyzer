def generate_report(df, group_col, value_col, agg_func):
    # Perform groupby
    result = df.groupby(group_col)[value_col].agg(agg_func).reset_index()

    # Sort descending
    result = result.sort_values(by=value_col, ascending=False)

    return result