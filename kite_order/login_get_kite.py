from toolkit.fileutils import Fileutils
from omspy_brokers.bypass import Bypass
from omspy.brokers.zerodha import Zerodha


f = Fileutils()


def get_kite(api="", sec_dir="../../confid/"):
    kite = False
    if api == "bypass":
        print("trying login BYPASS ..")
        kite = _get_bypass(sec_dir)
    else:
        print("trying login ZERODHA ..")
        kite = _get_zerodha(sec_dir)
    return kite


def _get_bypass(sec_dir):
    try:
        fpath = sec_dir + 'bypass.yaml'
        print(f'reading credentials from {fpath}')
        lst_c = f.get_lst_fm_yml(fpath)
        tokpath = sec_dir + lst_c['userid'] + '.txt'
        enctoken = None
        if f.is_file_not_2day(tokpath) is False:
            print(f'file modified today ... reading {enctoken}')
            with open(tokpath, 'r') as tf:
                enctoken = tf.read()
                if len(enctoken) < 5:
                    enctoken = None
        print(f'enctoken to broker {enctoken}')
        bypass = Bypass(lst_c['userid'],
                        lst_c['password'],
                        lst_c['totp'],
                        tokpath,
                        enctoken)
        if bypass.authenticate():
            if not enctoken:
                enctoken = bypass.kite.enctoken
                with open(tokpath, 'w') as tw:
                    tw.write(enctoken)
    except Exception as e:
        print(f"unable to create bypass object {e}")
    else:
        return bypass


def _get_zerodha(sec_dir):
    try:
        fpath = sec_dir + 'zerodha.yaml'
        print(f'reading credentials from {fpath}')
        fdct = f.get_lst_fm_yml(fpath)
        print(fdct)
        zera = Zerodha(user_id=fdct['userid'],
                       password=fdct['password'],
                       totp=fdct['totp'],
                       api_key=fdct['api_key'],
                       secret=fdct['secret'],
                       tokpath=sec_dir + fdct['userid'] + '.txt'
                       )
        zera.authenticate()
    except Exception as e:
        print(f"exception while creating zerodha object {e}")
    finally:
        return zera


if __name__ == "__main__":
    kobj = get_kite()
    print(kobj.margins)
