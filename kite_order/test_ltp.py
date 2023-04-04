from toolkit.utilities import Utilities
import json
from login_get_kite import get_kite
from main import get_orders, get_positions, merg_pos_stop, is_not_order_dirty, do_targets, update_ltp

try:
    sec_dir = "../../confid/"
    z = get_kite("", sec_dir)
    print("\n POSITIONS")
    with open("tests/posn.json") as posnjson:
        lst_all_posn = json.loads(posnjson.read())
    df_pos = get_positions(lst_all_posn)
    df_pos = update_ltp(df_pos, z)
    Utilities().slp_til_nxt_sec()
except Exception as e:
    print(e)
