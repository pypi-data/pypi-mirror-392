import pandas as pd
import numpy as np
from dataclasses import dataclass

@dataclass
class Deal:
    index: int
    price: float
    size: float
    closed: bool
    dir: bool  # True - long, False - short


@dataclass
class Position:
    size: float
    dir: bool  # True - long, False - short
    average_price: float
    deals: list
    pnl: float
    pnl_money: float
    parts: int
    draw_down: float
    draw_up: float


@dataclass
class Depo:
    start_balance: float
    actual_balance: float
    actual_balance_list: list
    pnl: float
    money_in_position: float
    money_in_position_list: list
    free_balance: float
    load_perc: float
    depo_load_perc_list: list
    position: Position
    average_position_price: list
    positions: list
    enter_size_abs: float
    # enter_perc: float


def OpenPosition(depo, deal):
    # print('op', deal.index)
    pos = Position(size=deal.size, dir=deal.dir, average_price=deal.price, deals=[deal], pnl=0.0, pnl_money=0, parts=1,
                   drawdown=0, drawup=0)
    # pos.pnl -= 0#pos.average_price * pos.size * 0.00012
    depo.positions.append(pos)
    depo.position = pos
    depo.enter_size_abs = abs(deal.size)


def ClosePosition(depo, deal):
    # print('cp', deal.index)
    depo.position.pnl = (
                                    deal.price - depo.position.average_price) * depo.position.size / 10  # - abs(depo.position.size * depo.position.average_price * 0.0004 / 10)
    depo.pnl += depo.position.pnl
    # print(depo.position.pnl)
    depo.position.deals.append(deal)
    depo.position = None
    # depo.enter_size = depo.actual_balance * depo.enter_perc / 100 / current_price


def GetPositionPnl(depo, price):
    return (price - depo.position.average_price) * depo.position.size / 10


def UpdateDepo(depo, price):
    # print(depo.actual_balance)
    cur_pnl = 0
    mip = 0
    if depo.position != None:
        cur_pnl = GetPositionPnl(depo, price)
        depo.average_position_price.append(depo.position.average_price)
        # print(depo.position.average_price, depo.position.size)
        mip = depo.position.average_price * depo.position.size

    depo.actual_balance = depo.start_balance + depo.pnl + cur_pnl
    depo.actual_balance_list.append(depo.actual_balance)
    depo.money_in_position = mip
    depo.money_in_position_list.append(mip)
    depo.free_balance = depo.actual_balance - mip

    # depo.free_money = depo.actual_balance - depo.position.size
    # depo.enter_size = depo.free_money * depo.enter_size_perc / 100
    # print(depo.enter_size)
    # depo.enter_size = depo.actual_balance * 3 / 100
    # print(depo.enter_size)


def UpdatePosition(depo, deal):
    # print('up', deal)
    if depo.position == None or deal == None:
        print('upd_pos_ERROR')
    pos = depo.position
    if pos.dir == deal.dir:
        pos.parts += 1
    else:
        pos.parts -= 1
    if pos.parts == 0:
        # print('pars == 0')
        ClosePosition(depo, deal)
        return
    if pos.size + deal.size == 0:
        print('WTF')
        print(pos, deal)
    pos.average_price = (pos.average_price * pos.size + deal.price * deal.size) / (pos.size + deal.size)
    pos.size += deal.size
    pos.size_money = pos.average_price * pos.size
    pos.pnl = (deal.price - depo.position.average_price) * depo.position.size
    pos.deals.append(deal)
    return


def UpdatePositionDrawDown(position: Position, high, low):
    if position.dir:
        position.drawdown = max(position.drawdown, position.average_price - low)
        position.drawup = max(position.drawup, high - position.average_price)
    else:
        position.drawdown = max(position.drawdown, high - position.average_price)
        position.drawup = max(position.drawup, position.average_price - low)


def MakeDeal(depo, deal):
    # print('md',depo.enter_size_abs, deal.index)
    pos = depo.position
    if pos == None:
        OpenPosition(depo, deal)
        return
    # if deal.index == 114222:
    #     print('pos', depo.position.size, depo.position.average_price, depo.position.deals[0].index)
    #     print(len(depo.position.deals))
    position = depo.position
    # print((depo.free_balance + deal.size*deal.price))
    # VREMENNO

    if depo.position.size + deal.size == 0:
        # print('cp')
        ClosePosition(depo, deal)
        return
    UpdatePosition(depo, deal)

    # if position.dir == deal.dir and abs(depo.money_in_position + deal.size*deal.price) / depo.actual_balance > depo.load_perc:
    #     #print('rekt')
    #     return
    # UpdatePosition(depo, deal)
    # #depo.position.deals.append(deal)
    # return

    # if position.size > 0 and deal.size < 0:
    #     #dif = position.size + deal.size
    #     if dif == 0:
    #         print('cp', deal.index)
    #         ClosePosition(depo, deal)
    #         return
    #     if dif > 0:
    #         print('up', deal.index)
    #         UpdatePosition(depo, deal)
    #         position.deals.append(deal)
    #         return
    #     if dif < 0:
    #         print('cpp', deal)
    #         # deal_size = deal.size + position.size
    #         # deal.size = -position.size
    #         ClosePosition(depo, deal)
    #         # deal.size = deal.size
    #         # deal.closed = False
    #         # OpenPosition(depo, deal)
    #         return
    # if position.size < 0 and deal.size > 0:
    #     dif = position.size + deal.size
    #     if dif == 0:
    #         print('cp', deal.index)
    #         ClosePosition(depo, deal)
    #         return
    #     if dif < 0:
    #         print('up', deal.index)
    #         UpdatePosition(depo, deal)
    #         position.deals.append(deal)
    #         return
    #     if dif > 0:
    #         print('cpp', deal)
    #         # deal_size = deal.size + position.size
    #         # deal.size = -position.size
    #         ClosePosition(depo, deal)
    #         # deal.size = deal.size
    #         # deal.closed = False
    #         # OpenPosition(depo, deal)
    #         return


def Simulate(df, X, long_proba_treshold=0.07, short_proba_treshold=0.07, quit_proba=0.07, quit_wstd=1, enter_perc=10,
             load_perc=0.8, min_length_between_enters=20, min_price_perc_change_between_enters=0.4
             , wstdc=1, take_perc=1.5, stop_perc=1.5, long_proba=any, short_proba=any, streak_size=0,
             plot_start_index=-1, plot_end_index=-1):
    depo = Depo(start_balance=100, actual_balance=100, actual_balance_list=[], money_in_position=0,
                money_in_position_list=[],
                load_perc=load_perc, depo_load_perc_list=[], position=None, average_position_price=[], pnl=0,
                positions=[], free_balance=100, enter_size_abs=0)

    high = np.array(np.exp(df.High))
    low = np.array(np.exp(df.Low))
    typical = np.array(np.exp(df.Typical))
    wstd = np.array(df.WSTD)
    # wstd = np.array(df.STD500)
    close = np.array(np.exp(df.Close))
    n = 0
    # maxs = np.array(df.maxs50)
    # mins = np.array(df.mins50)
    long_enters_history = []
    long_quits_history = []
    short_enters_history = []
    actual_long_enters = []
    actual_short_enters = []
    last_enter = Deal(-min_length_between_enters, 0, 0, False, True)
    last_quit = Deal(-min_length_between_enters, 0, 0, False, False)
    ds = 0
    dpa = 0
    short_signals_streak = 0
    long_signals_streak = 0
    for i in range(len(high)):
        # print(i)
        current_price = typical[i]
        current_high = high[i]
        current_low = low[i]
        current_wstd = wstd[i]
        enter_size = depo.actual_balance * enter_perc / 100 / current_price

        # if depo.position != None and long_proba[i] < long_proba_treshold:
        #     UpdateDepo(depo, current_price)
        #     continue
        # if i == 5:
        #     MakeDeal(depo, Deal(i, current_price, 0.003, False, True))
        # if i == len(high) - 1:
        #     MakeDeal(depo, Deal(i, current_price, -0.003, False, False))
        if i < 3:
            UpdateDepo(depo, current_price)
            continue
        ### PERC STOP
        # if depo.position != None:
        #     price_change = (depo.position.average_price - current_price) / depo.position.average_price * 100
        #     if depo.position.dir:
        #         if price_change > take_perc:
        #             #print(depo.position.average_price, current_price)
        #             take_deal = Deal(i, low[i], -depo.position.size, False, not depo.position.dir)
        #             MakeDeal(depo, take_deal)
        #             last_enter = take_deal
        #             #print('long take',i)

        #         else:
        #             if price_change < -stop_perc:
        #                 #print(price_change)
        #                 take_deal = Deal(i, high[i], -depo.position.size, False, not depo.position.dir)
        #                 MakeDeal(depo, take_deal)
        #                 last_enter = take_deal
        #                 #print('long stop',i)
        #     else:
        #         if price_change < -take_perc:
        #             take_deal = Deal(i, current_price, -depo.position.size, False, not depo.position.dir)
        #             MakeDeal(depo, take_deal)
        #             last_enter = take_deal
        #             #print('short take')
        #         else:
        #             if price_change > stop_perc:
        #                 take_deal = Deal(i, current_price, -depo.position.size, False, not depo.position.dir)
        #                 MakeDeal(depo, take_deal)
        #                 last_enter = take_deal
        #                 #print('short stop')

        ##WSTD STOP
        if depo.position != None:
            if depo.position:
                price_change = current_high - depo.position.average_price
                if price_change > current_wstd * quit_wstd:
                    take_deal = Deal(i, current_price, -depo.position.size, False, not depo.position.dir)
                    MakeDeal(depo, take_deal)
                    last_enter = take_deal
                    # print('long take')
                else:
                    if price_change < -current_wstd * quit_wstd:
                        take_deal = Deal(i, current_price, -depo.position.size, False, not depo.position.dir)
                        MakeDeal(depo, take_deal)
                        last_enter = take_deal
                        # print('long stop')
            else:
                price_change = depo.position.average_price - current_low
                if price_change > current_wstd * quit_wstd:
                    take_deal = Deal(i, current_price, -depo.position.size, False, not depo.position.dir)
                    MakeDeal(depo, take_deal)
                    last_enter = take_deal
                    # print('short take')
                else:
                    if price_change < -current_wstd:
                        take_deal = Deal(i, current_price, -depo.position.size, False, not depo.position.dir)
                        MakeDeal(depo, take_deal)
                        last_enter = take_deal
                        # print('short stop')

            # if abs((current_price - depo.position.average_price) * depo.position.size / depo.actual_balance) * 100 > take_perc:
            # if abs(depo.position.average_price - current_price) / depo.position.average_price * 100 > take_perc:
            #     take_deal = Deal(i, current_price, -depo.position.size, False, not depo.position.dir)
            #     MakeDeal(depo, take_deal)
            #     last_enter = take_deal
            #     print('take')
            # else:
            #     if abs(depo.position.average_price - current_price) / depo.position.average_price * 100> stop_perc:
            #         stop_deal = Deal(i, current_price, -depo.position.size, False, not depo.position.dir)
            #         MakeDeal(depo, stop_deal)
            #         last_enter = stop_deal
            #         print('stop')

        # if depo.position != None:
        #     #len_cond = i - last_enter.index > min_length_between_enters
        #     len_cond = True
        #     if depo.position.dir and short_proba[i] > quit_proba  and abs(current_price - depo.position.average_price) > min(quit_wstd*current_wstd, 3000) and len_cond:
        #         quit_deal = Deal(i, current_price, -depo.position.size, False, not depo.position.dir)
        #         MakeDeal(depo, quit_deal)
        #         last_enter = quit_deal
        #         UpdateDepo(depo, current_price)
        #         #print('ql')
        #         continue
        #     if not depo.position.dir and long_proba[i] > quit_proba and abs(depo.position.average_price - current_price) > min(quit_wstd*current_wstd, 3000) and len_cond:
        #         quit_deal = Deal(i, current_price, -depo.position.size, False, not depo.position.dir)
        #         MakeDeal(depo, quit_deal)
        #         last_enter = quit_deal
        #         UpdateDepo(depo, current_price)
        #         #print('qs')
        #         continue

        # if streak_size != 0:
        #     if depo.position != None:
        #         if depo.position.dir and short_proba[i] > quit_proba:
        #             if short_signals_streak < streak_size:
        #                 short_signals_streak += 1
        #                 UpdateDepo(depo, current_price)
        #                 continue
        #             short_signals_streak = 0
        #             quit_deal = Deal(i, current_price, -depo.position.size, False, not depo.position.dir)
        #             MakeDeal(depo, quit_deal)
        #             last_enter = quit_deal
        #             UpdateDepo(depo, current_price)
        #             #print('ql')
        #             continue
        #         else:
        #             short_signals_streak = 0
        #         if not depo.position.dir and long_proba[i] > quit_proba:
        #             if long_signals_streak < streak_size:
        #                 long_signals_streak += 1
        #                 UpdateDepo(depo, current_price)
        #                 continue
        #             long_signals_streak = 0
        #             quit_deal = Deal(i, current_price, -depo.position.size, False, not depo.position.dir)
        #             MakeDeal(depo, quit_deal)
        #             last_enter = quit_deal
        #             UpdateDepo(depo, current_price)
        #             #print('qs')
        #             continue
        #         else:
        #             long_signals_streak = 0
        # and short_proba[i] < proba_for_enter_short
        if depo.position == None and long_proba[i] < long_proba_treshold and long_proba[
            i - 1] < long_proba_treshold:  # and long_proba[i - 2] < long_proba_treshold:

            # enter strategy
            len_cond = i - last_enter.index > min_length_between_enters
            # price_cond = abs(current_price - last_enter.price) / current_price * 100 > min_price_perc_change_between_enters
            # price_cond = abs(current_price - last_enter.price)  > wstdc*current_wstd
            if depo.position != None:
                if depo.position.dir == False:
                    price_cond = True
                    len_cond = True
                    n += 1
                else:  # УБРАТЬ ДЛЯ МНОЖЕСТВЕННЫХ ВХОДОВ
                    UpdateDepo(depo, current_price)
                    continue
            if len_cond:  # and price_cond:
                # print('l', i)
                size = 0
                if depo.position == None:
                    size = 0.003  # 0.003#enter_perc * depo.actual_balance / 100 / current_price
                else:
                    size = depo.enter_size_abs  # 0.003#depo.enter_size_abs
                enter = Deal(i, high[i], size, False, True)

                MakeDeal(depo, enter)
                # print(i, close[i])
                last_enter = enter
                # long_enters_history.append(enter)
        # №and long_proba[i] < proba_for_enter_long
        # if short_proba[i] > upper_proba and short_proba[i - 1] > upper_proba and short_proba[i - 2] > upper_proba and long_proba[i] < lower_proba and long_proba[i - 1] < lower_proba and long_proba[i-2] < lower_proba:
        #     #enter strategy

        #     len_cond = i - last_enter.index > min_length_between_enters
        #     #price_cond = abs(current_price - last_enter.price) / current_price * 100 > min_price_perc_change_between_enters
        #     price_cond = abs(current_price - last_enter.price)  > wstdc*current_wstd
        #     if depo.position != None:
        #         if depo.position.dir == True:
        #             price_cond = True
        #             len_cond = True
        #             n+=1
        #         else:
        #             UpdateDepo(depo, current_price)
        #             continue
        #     if len_cond and price_cond:
        #         #print('s', i)
        #         size = 0
        #         if depo.position == None:
        #             size = -0.003#-0.003#enter_perc * depo.actual_balance / 100 / current_price
        #         else:
        #             size = depo.enter_size_abs#-0.003#depo.enter_size_abs
        #         enter = Deal(i, close[i], size, False, False)
        #         MakeDeal(depo, enter)

        #         last_enter = enter
        #         #short_enters_history.append(enter)

        # if depo.position != None:
        #     for d in depo.position.deals:
        #         if d.closed:
        #             continue
        #         len_cond = i - last_enter.index > min_length_between_enters
        #         price_cond = abs(current_price - last_enter.price) / current_price * 100 > min_price_perc_change_between_enters
        #         #len_cond = True
        #         #price_cond=True

        #         if current_price - d.price > 1*current_wstd and depo.position.dir == True and d.dir == True and len_cond and price_cond:
        #             quit_part = Deal(i, current_price, -depo.enter_size_abs, True, False)
        #             #print('long prt')
        #             d.closed=True
        #             MakeDeal(depo, quit_part)
        #             last_enter = quit_part
        #             break
        #             #short_enters_history.append(quit_part)
        #         else:
        #             if d.price - current_price > 1*current_wstd and depo.position.dir == False and d.dir == False and len_cond and price_cond :
        #                 quit_part = Deal(i, current_price, depo.enter_size_abs, True, True)
        #                 #print('short prt')
        #                 d.closed=True
        #                 MakeDeal(depo, quit_part)
        #                 last_enter = quit_part
        #                 break
        #                 long_enters_history.append(quit_part)
        UpdateDepo(depo, current_price)
        # if i > 0 and i < 1500:
        #     print(i)
        #     print(depo.position)
        # # if depo.position != None:
        # #     ds = depo.position.size
        # #     dpa = depo.position.average_price
        # # print(depo.actual_balance, ds, dpa)

    print(n)
    r1 = 0
    r2 = len(high)  # len(high)
    r3 = plot_start_index
    r4 = plot_end_index
    # r3 = r2
    long_enter_index = []
    long_enter_price = []

    for enter in long_enters_history:
        long_enter_index.append(enter.index)
        long_enter_price.append(enter.price)
    short_enter_index = []
    short_enter_price = []
    for enter in short_enters_history:
        short_enter_index.append(enter.index)
        short_enter_price.append(enter.price)

    for pos in depo.positions:
        for deal in pos.deals:
            if deal.dir:
                long_enter_index.append(deal.index)
                long_enter_price.append(deal.price)
            else:
                short_enter_index.append(deal.index)
                short_enter_price.append(deal.price)

    long_df = pd.DataFrame({'idx': long_enter_index, 'value': long_enter_price})
    long_df = long_df[(long_df.idx > r3) & (long_df.idx < r4)]
    short_df = pd.DataFrame({'idx': short_enter_index, 'value': short_enter_price})
    short_df = short_df[(short_df.idx > r3) & (short_df.idx < r4)]
    plt.figure(figsize=(12, 6))
    plt.plot(long_df.idx, long_df.value, 'o', alpha=0.5)
    plt.plot(short_df.idx, short_df.value, 'o', alpha=0.5)
    pd.Series(typical)[r3:r4].plot(alpha=0.2)
    # pd.Series(long_proba[r3:r4]).plot(secondary_y=True,alpha=0.2)
    # pd.Series(-short_proba[r3:r4]).plot(secondary_y=True,alpha=0.2)
    pd.Series(depo.actual_balance_list[r3:r4], index=range(r3, r4)).plot(secondary_y=True)

    plt.show()
    plt.figure(figsize=(12, 6))
    plt.ticklabel_format(useOffset=False)
    pd.Series(depo.actual_balance_list[r1:r2], index=range(r1, r2)).plot()
    pd.Series(typical)[r1:r2].plot(secondary_y=True)
    plt.show()
    # (pd.Series(depo.money_in_position_list[r1:r2])).plot()

    return depo

