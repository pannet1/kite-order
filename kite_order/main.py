import pandas as pd
import numpy as np
from time import sleep
from toolkit.fileutils import Fileutils
from toolkit.logger import Logger
from login_get_kite import get_kite
from typing import Dict


api = ""  # "" is zerodha, optional bypass
WORK_PATH = "../../confid/"
logging = Logger(20, WORK_PATH + 'kite_order.log')
# toolkit modules
f = Fileutils()
z = get_kite(api, WORK_PATH)
TESTING = False
if TESTING:
    from tests.orders import test_orders as orders
    from tests.small import test_trades as small

f = Fileutils()
MIS = f.get_lst_fm_yml('MIS.yaml')
NRML = f.get_lst_fm_yml('NRML.yaml')

comk = ['exchange',
        'symbol',
        'product',
        'quantity',
        'side',
        'status',
        'trigger_price',
        'price',
        'order_id',
        'order_type',
        'average_price',
        'last_price']


ordk = ['symbol',
        'product',
        'order_id',
        'order_type',
        'status']


def chek_stop(row: pd.Series) -> float:
    dct_stop = MIS.get(row.symbol[-2:],  False) if row.product == 'MIS' else \
        NRML.get(row.symbol[-2:], False)
    if any(dct_stop):
        return dct_stop['price']
    return 0


def chek_trgr(row: pd.Series) -> float:
    dct_trgr = MIS.get(row.symbol[-2:],  False) if row.product == 'MIS' else \
        NRML.get(row.symbol[-2:], False)
    if any(dct_trgr):
        return dct_trgr['trigger']
    return 0


def ordr_mgmt(dct_ordr: Dict, ops: str) -> None:
    dct_ordr.pop('average_price')
    dct_ordr.pop('last_price')
    dct_ordr.pop('dirn')
    dct_ordr.pop('sqof')
    dct_ordr.pop('status')
    dct_ordr['price'] = dct_ordr.pop('pric')
    dct_ordr['trigger_price'] = dct_ordr.pop('trgr')
    dct_ordr['side'] = 'SELL' if dct_ordr.get('quantity') > 0 else 'BUY'
    dct_ordr['quantity'] = abs(dct_ordr['quantity'])
    if ops == "SL" or "MARKET":
        dct_ordr['order_type'] = ops
        dct_ordr.pop('order_id')
        status = z.order_place(**dct_ordr)
    elif ops == 'MODIFY' or 'TARGET':
        dct_ordr['order_type'] = 'MARKET'
        status = z.order_modify(**dct_ordr)
    return status


pd.options.mode.chained_assignment = None
while True:
    lst_all_ords = orders if TESTING else z.orders
    if any(lst_all_ords):
        print("ORDERS")
        df_ords = pd.DataFrame(lst_all_ords)
        print(df_ords.columns.values)
        df_ords = df_ords.filter(comk)
        df_ords = df_ords[df_ords['status'] != 'COMPLETE']
        df_ords['status'] = df_ords['status'].replace([None], 'UNKNOWN')
        print(df_ords, "\n")
        df_ords = df_ords.filter(ordk)

        # filter dataframes based on order types
        df_stop = df_ords.query("order_type=='SL'").copy()
        df_trgt = df_ords.query("order_type=='MARKET'").copy()
    print("sleeping for 1 sec")
    sleep(1)
    lst_all_posn = small if TESTING else z.positions
    if any(lst_all_posn):
        filr_pos = pd.DataFrame.from_records(
            lst_all_posn)
        filr_pos = filr_pos.filter(comk)
        df_pos = filr_pos.loc[filr_pos["quantity"] != 0]
        if not df_pos.empty:
            print("\n POSITIONS")
            df_pos['dirn'] = np.where(df_pos.quantity > 0, 1, -1)
            df_pos['pric'] = df_pos.apply(chek_stop, axis=1)
            df_pos['pric'] = df_pos.average_price - (df_pos.dirn * df_pos.pric)
            df_pos['trgr'] = df_pos.apply(chek_trgr, axis=1)
            df_pos['trgr'] = df_pos.average_price - (df_pos.dirn * df_pos.trgr)
            df_pos['sqof'] = df_pos.dirn * (df_pos.trgr - df_pos.last_price)
            print(df_pos)
            print("\n POSITIONS and STOPS")
            posn_stop = df_pos.merge(df_stop, how='left', on=[
                'symbol', 'product'])
            print(posn_stop)
            for i, o in posn_stop.iterrows():
                """
                Positions without SL contains order_type as nan
                """
                if o['order_type'] != 'SL' and o['sqof'] <= 0:
                    if not TESTING:
                        ordr_mgmt(o, 'SL')
                    logging.info(f"placing stop for symbol {o['symbol']}")
                elif o['order_type'] != 'SL' and o['sqof'] > 0:
                    if not TESTING:
                        ordr_mgmt(o, 'MARKET')
                    logging.info(
                        f"squaring {o['symbol']} in loss but without order")
                    continue
                elif o['order_type'] == 'SL' and o['sqof'] > 0:
                    if not TESTING:
                        ordr_mgmt(o, 'MODIFY')
                    logging.info(
                        f"modifying {o['order_id']} for {o['symbol']} in loss")
                    continue
                # positon without stoploss but no stop order yet
            posn_trgt = df_pos.merge(
                df_trgt, how='left', on=['symbol', 'product'])
            print("\n POSITION and TARGETS")
            print(posn_trgt)
            for i, o in posn_trgt.iterrows():
                if o['order_type'] == 'MARKET' and o['status'] == 'REJECTED':
                    if not TESTING:
                        ordr_mgmt(o, 'TARGET')
                    logging.info(f"target reached for {o['symbol']}")
    print("sleeping for 1 sec")
    sleep(1)
