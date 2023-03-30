import pandas as pd
import numpy as np
from toolkit.fileutils import Fileutils
from toolkit.utilities import Utilities
from toolkit.logger import Logger
from login_get_kite import get_kite
from typing import Dict

WORK_PATH = "../../confid/"
# logging = Logger(20, WORK_PATH + 'kite_order.log')
logging = Logger(10)
api = ""  # "" is zerodha, optional bypass
z = get_kite(api, WORK_PATH)

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
    dct_stop = MIS.get(row['symbol'][-2:], False) if \
        row['product'] == 'MIS' else NRML.get(row['symbol'][-2:], False)
    if any(dct_stop):
        return dct_stop['price']


def chek_trgr(row: pd.Series) -> float:
    dct_trgr = MIS.get(row['symbol'][-2:],  False) if \
        row['product'] == 'MIS' else NRML.get(row['symbol'][-2:], False)
    if any(dct_trgr):
        return dct_trgr['trigger']


def myround(x, prec=2, base=.05):
    if x == 0:
        return x
    return round(base * round(float(x)/base), prec)


def ordr_mgmt(dct_ordr: Dict, ops: str) -> None:
    try:
        dct_ordr.pop('average_price')
        dct_ordr.pop('last_price')
        dct_ordr.pop('dirn')
        dct_ordr.pop('sqof')
        dct_ordr.pop('status')
        price = dct_ordr.pop('pric')
        dct_ordr['price'] = myround(price)
        trgr = dct_ordr.pop('trgr')
        dct_ordr['trigger_price'] = myround(trgr)
        dct_ordr['side'] = 'SELL' if dct_ordr.get('quantity') > 0 else 'BUY'
        dct_ordr['quantity'] = abs(dct_ordr['quantity'])
        if ops == "SL" or "MARKET":
            dct_ordr['order_type'] = ops
            dct_ordr.pop('order_id')
            status = z.order_place(**dct_ordr)
            logging.info(f" order placed \n {dct_ordr} \n status {status}")
        elif ops == 'MODIFY' or 'TARGET':
            dct_ordr['order_type'] = 'MARKET'
            status = z.order_modify(**dct_ordr)
            logging.info(f" order modified \n { dct_ordr } \n status {status}")
    except Exception as e:
        print(str(e))
        return


df_null = pd.DataFrame()


def get_orders(lst_all_ords):
    df_trgt = df_stop = df_null
    if any(lst_all_ords):
        df_ords = pd.DataFrame(lst_all_ords)
        df_ords = df_ords.query("exchange=='NFO'")
        df_ords = df_ords[df_ords["status"] != 'COMPLETE']
        df_ords = df_ords[df_ords["status"] != 'CANCELED']
        df_ords['status'] = df_ords['status'].replace([None], 'UNKNOWN')
        df_ords = df_ords.filter(ordk)
        print(df_ords, "\n")
        # filter dataframes based on order types
        df_stop = df_ords.query("order_type=='SL'").copy()
        df_trgt = df_ords.query(
            "order_type=='MARKET' and status=='REJECTED'").copy()
    return df_stop, df_trgt


def get_positions(lst_all_posn):
    df_pos = df_null
    if any(lst_all_posn):
        NOT_MOD = True
        filr_pos = pd.DataFrame.from_records(
            lst_all_posn)
        filr_pos = filr_pos.query("exchange=='NFO'")
        filr_pos = filr_pos.filter(comk)
        df_pos = filr_pos.loc[filr_pos["quantity"] != 0]
        if not df_pos.empty:
            df_pos['dirn'] = np.where(df_pos.quantity > 0, 1, -1)
            df_pos['pric'] = df_pos.apply(chek_stop, axis=1)
            df_pos['pric'] = df_pos.average_price - \
                (df_pos.dirn * df_pos.pric)
            df_pos['trgr'] = df_pos.apply(chek_trgr, axis=1)
            df_pos['trgr'] = df_pos.average_price - \
                (df_pos.dirn * df_pos.trgr)
            df_pos['sqof'] = df_pos.dirn * \
                (df_pos.trgr - df_pos.last_price)
            print(df_pos)
    return df_pos


def merg_pos_stop(df_pos, df_stop):
    posn_stop = df_null
    if not df_pos.empty:
        posn_stop = df_pos.merge(df_stop, how='left', on=[
            'symbol', 'product'])
        print(posn_stop)
    return posn_stop


def is_not_order_dirty(posn_stop):
    NOT_MOD = True
    for i, o in posn_stop.iterrows():
        """
        Positions without SL contains order_type as nan
        """
        if o['order_type'] != 'SL' and o['sqof'] <= 0:
            ordr_mgmt(o, 'SL')
            logging.info(f"placed stop for symbol {o['symbol']}")
            NOT_MOD = False
        elif o['order_type'] != 'SL' and o['sqof'] > 0:
            ordr_mgmt(o, 'MARKET')
            logging.info(
                f"squaring {o['symbol']} in loss but without order")
            NOT_MOD = False
        elif o['order_type'] == 'SL' and o['sqof'] > 0:
            logging.info(
                f"modified {o['order_id']} for {o['symbol']} in loss")
            ordr_mgmt(o, 'MODIFY')
            NOT_MOD = False
    return NOT_MOD


def do_targets(posn_stop, df_trgt):
    stop = posn_stop.query("order_type=='SL'")
    stop = stop.filter(ordk).drop(["status", "order_type"], axis=1)

    posn_trgt = df_pos.merge(df_trgt, how='left', on=[
        'symbol', 'product'])
    trgt = posn_trgt.query(
        "order_type=='MARKET' and status=='REJECTED'")
    trgt = trgt.filter(comk).drop(["order_id"], axis=1)

    trgt_stop = trgt.merge(stop, how="left", on=[
        'symbol', 'product'])
    print(trgt_stop)
    for i, o in trgt_stop.iterrows():
        o["dirn"] = 1 if o['quantity'] > 0 else -1
        o['sqof'] = 0
        o['pric'] = 0
        o['trgr'] = 0
        ordr_mgmt(o, 'TARGET')
        logging.info(f"target reached for {o['symbol']}")


pd.options.mode.chained_assignment = None
while True:
    try:
        print("ORDERS \n")
        df_stop, df_trgt = get_orders(z.orders)
        print("\n POSITIONS")
        df_pos = get_positions(z.positions)
        print("\n POSITIONS and STOPS")
        posn_stop = merg_pos_stop(df_pos, df_stop)
        print("\n POSITION and TARGETS")
        if is_not_order_dirty(posn_stop):
            do_targets(posn_stop, df_trgt)
    except Exception as e:
        logging.error(f"error {e} occured")
    finally:
        Utilities().slp_til_nxt_sec()
