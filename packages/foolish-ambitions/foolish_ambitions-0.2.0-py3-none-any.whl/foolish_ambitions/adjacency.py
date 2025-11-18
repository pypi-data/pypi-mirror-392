from ts2vg import NaturalVG

def get_highest_visible_var(df_high, am=None):
    if am is None:
        g = NaturalVG(directed=None).build(df_high)
        row = (g.adjacency_matrix()[len(df_high) - 1] * df_high)
        return [row.idxmax(), row.max()]

    row = (am[:len(df_high)] * df_high)
    return row.idxmax()

def get_lowest_visible_var(df_low, am=None):
    if am is None:
        g = NaturalVG(directed=None).build(-df_low)
        row = (g.adjacency_matrix()[len(df_low) - 1] * df_low)
        row = row[row != 0]
        return [row.idxmin(), row.min()]

    row = (am[:len(df_low)][-1] * df_low)
    row = row[row != 0]
    if len(row) == 0:
        return 0
    return row.idxmin()

def numerical_adjacency(adj_matr):
    return sum(adj_matr, axis=1)