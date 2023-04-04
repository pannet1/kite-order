from pprint import pprint
import random


class Paper:

    def order_modify(self, **dct):
        return "order modified"

    def order_place(self, **dct):
        return "order placed"

    def ltp(self, exchsym):
        if type(exchsym) == list:
            return [{k: {"last_price": random.randint(10, 60)}} for k in exchsym]
        else:
            return {exchsym: {"last_price": random.randint(10, 60)}}
