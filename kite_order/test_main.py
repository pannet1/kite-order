from toolkit.utilities import Utilities
import json
from paper import Paper
from main import get_orders, get_positions, merg_pos_stop, is_not_order_dirty, do_targets, update_ltp


z = Paper()
print("ORDERS \n")
with open("tests/ords.json") as ordsjson:
    lst_all_ords = json.loads(ordsjson.read())
df_stop, df_trgt = get_orders(lst_all_ords)
print("\n POSITIONS")
with open("tests/posn.json") as posnjson:
    lst_all_posn = json.loads(posnjson.read())
df_pos = get_positions(lst_all_posn)
df_pos = update_ltp(df_pos, z)
print("\n POSITIONS and STOPS")
posn_stop = merg_pos_stop(df_pos, df_stop)
print("\n POSITION and TARGETS")
if is_not_order_dirty(posn_stop, z):
    do_targets(df_pos, posn_stop, df_trgt, z)
else:
    do_targets(df_pos, posn_stop, df_trgt, z)
Utilities().slp_til_nxt_sec()
