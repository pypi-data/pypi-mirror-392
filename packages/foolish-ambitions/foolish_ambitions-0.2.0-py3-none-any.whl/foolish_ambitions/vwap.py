import numpy as np
import pandas as pd
import enum


class Vertical(enum.Enum):
    up = True
    down = False


class Horizontal(enum.Enum):
    left = False
    right = True


def VwapNumpy(price):
    dif = np.diff(price)
    vol = dif * dif
    cv = vol.cumsum()
    pv = vol * price[1:]
    cpv = pv.cumsum()
    anc = cpv / cv
    anc = np.insert(anc, 0, price[0])


def line(data, dir, is_back=False, coef=None):
    tmp = pd.DataFrame()
    start_bar = data.iloc[0] if not is_back else data.iloc[-1]
    start_price = start_bar.Low if dir else start_bar.High

    if is_back:
        data = data.iloc[::-1]
    price_series = data.High if dir else data.Low

    tmp['vol'] = data.Vol
    start_vol = abs(start_price - (data.iloc[0].Close if is_back else data.iloc[0].Open))
    tmp.iloc[0, tmp.columns.get_loc('vol')] = start_vol
    tmp['cum_vol'] = tmp.vol.cumsum()
    tmp['price'] = price_series - start_price
    sign = 1 if dir else -1
    tmp.iloc[0, tmp.columns.get_loc('price')] = start_vol * sign
    tmp['w'] = tmp.vol * tmp.price

    tmp['cum_w'] = tmp.w.cumsum()
    tmp['anc'] = tmp.cum_w / tmp.cum_vol + start_price

    # tmp['coef'] = tmp.price / (tmp.anc - start_price)
    # tmp['coef'] = tmp.coef.cummax()

    coef_val = coef if coef else tmp.coef
    tmp['target_line'] = (tmp.anc - start_price) * coef_val + start_price
    return tmp.target_line


def count_coef(start_price, end_price, line_value):
    return abs((end_price - start_price) / (line_value - start_price))


def get_coef(data, line, direction, is_back):
    start_idx = 0 if not is_back else -1
    end_idx = -1 if not is_back else 0
    start_price = data.Low.iloc[start_idx] if direction else data.High.iloc[start_idx]
    end_price = data.Low.iloc[end_idx] if not direction else data.High.iloc[end_idx]
    line_value = line.iloc[end_idx] if not is_back else line.iloc[end_idx]

    return count_coef(start_price, end_price, line_value)


def apply_coef(data, line, coef, direction, is_back):
    idx = 0 if not is_back else -1
    start_price = data.Low.iloc[idx] if direction else data.High.iloc[idx]

    return (line - start_price) * coef + start_price


def fractal(df, direction):
    tl = line(df, direction, coef=1, is_back=False)
    bl = line(df, not direction, coef=1, is_back=True)
    return pd.DataFrame({'target_line': tl, 'back_line': bl})