import random


class Paper:

    def order_modify(self, **dct):
        return "order modified"

    def order_place(self, **dct):
        return "order placed"

    def ltp(self, exchsym):
        if type(exchsym) == list:
            resp = {key: {'last_price': round(
                random.uniform(10, 60), 2)} for key in exchsym}
            return resp
        else:
            return {exchsym: {"last_price": random.randint(10, 60)}}
