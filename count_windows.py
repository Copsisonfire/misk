import requests
import datetime

from .config import *

class APIClient:

    def __init__(self):
        pass

    def get_json(self, url, shop_id=None, chat=None, offset=0, limit=100,
                 updated_at__gt=None, created_at__gte=None, created_at__lt=None):
        try:
            resp = requests.get(url, headers={"Authorization": AUTH_TOKEN},
                                params={"shop_id": shop_id, "chat": chat, "limit": limit,
                                        "offset": offset, "updated_at__gt": updated_at__gt,
                                        "created_at__gte": created_at__gte, "created_at__lt": created_at__lt})
            if resp.status_code != 200:
                raise Exception('Not expected answer', {'code': resp.status_code})
            res_json = resp.json()
            if res_json.get("status", None) != "ok":
                raise Exception("Json is not ok")
            return res_json
        except Exception as e:
            print(e)
            raise Exception("Can't get json")

    def get_shop_list(self):
        shop_list = []
        count = self.get_json(url="https://app.hightouch.ai/api/shop/shops/", limit=1).get("result", {}).get("count")
        num = count // 100
        for i in range(num + 1):
            r = self.get_json(url="https://app.hightouch.ai/api/shop/shops/", offset=i * 100)
            results = r.get("result", {}).get("results")
            shop_ids = [x.get("id") for x in results]
            shop_list.extend(shop_ids)
        if len(shop_list) == count:
            return shop_list
        else:
            raise Exception("Not all shop_ids are in shop_list")

    def get_waba_bot_list(self, shop_id):
        waba_bot_list = []
        count = self.get_json(url="https://app.hightouch.ai/api/bot/bots/",
                              shop_id=shop_id, limit=1).get("result", {}).get("count")
        num = count // 100
        for i in range(num + 1):
            r = self.get_json(url="https://app.hightouch.ai/api/bot/bots/",
                              shop_id=shop_id,
                              offset=i * 100)
            if r.get("result", {}).get("count") != count and r.get("result", {}).get("count") > 100:
                raise Exception("The count has been increased by 1, please retry")
            results = r.get("result", {}).get("results")
            waba_bot_ids = [x.get("id") for x in results if x.get("waba_phone_number") != None]
            waba_bot_list.extend(waba_bot_ids)
        return waba_bot_list

    def get_waba_chats_list(self, shop_id, bot_id):
        waba_chats_list = []
        count = self.get_json(url="https://app.hightouch.ai/api/bot/chats/",
                              shop_id=shop_id, limit=1).get("result", {}).get("count")
        num = count // 100
        for i in range(num+1):
            r = self.get_json(url="https://app.hightouch.ai/api/bot/chats/",
                              shop_id=shop_id,
                              offset=i * 100)
            if r.get("result", {}).get("count") != count and r.get("result", {}).get("count") > 100:
                raise Exception("The count has been increased by 1, please retry")
            results: list = r.get("result", {}).get("results")
            waba_chats_ids = [x.get("id") for x in results if x.get("bot", {}).get("id") == bot_id]
            waba_chats_list.extend(waba_chats_ids)
        return waba_chats_list

    def get_active_users(self, shop_id):
        active_users = []
        timestamp_ago = datetime.datetime.now().timestamp() - 24 * 60 * 60
        count = self.get_json(url="https://app.hightouch.ai/api/bot/chats/",
                              shop_id=shop_id, limit=1, updated_at__gt=timestamp_ago).get("result", {}).get("count")
        num = count // 100
        for i in range(num+1):
            r = self.get_json(url="https://app.hightouch.ai/api/bot/chats/",
                              shop_id=shop_id, offset=i * 100, updated_at__gt=timestamp_ago)
            if r.get("result", {}).get("count") != count and r.get("result", {}).get("count") > 100:
                raise Exception("The count has been increased by 1, please retry")
            results: list = r.get("result", {}).get("results")
            users = [x.get("bot_user", {}).get("id") for x in results]
            active_users.extend(users)
        return active_users

    def get_waba_active_users(self, shop_id):
        active_waba_users = []
        timestamp_ago = datetime.datetime.now().timestamp() - 24 * 60 * 60
        count = self.get_json(url="https://app.hightouch.ai/api/bot/chats/",
                              shop_id=shop_id, limit=1, updated_at__gt=timestamp_ago).get("result", {}).get("count")
        num = count // 100
        for i in range(num+1):
            r = self.get_json(url="https://app.hightouch.ai/api/bot/chats/",
                              shop_id=shop_id, offset=i * 100, updated_at__gt=timestamp_ago)
            if r.get("result", {}).get("count") != count and r.get("result", {}).get("count") > 100:
                raise Exception("The count has been increased by 1, please retry")
            results: list = r.get("result", {}).get("results")
            users = [x.get("bot_user", {}).get("id") for x in results
                     if x.get("bot", {}).get("waba_phone_number") != None]
            active_waba_users.extend(users)
        return active_waba_users

    def get_messages_timestamp_list(self, shop_id, chat, start_date, end_date):  #datetime.datetime(2022,2,1).timestamp()
        messages_timestamp_list = []
        count = self.get_json(url="https://app.hightouch.ai/api/bot/messages/",
                              shop_id=shop_id, chat=chat, limit=1, created_at__gte=start_date,
                              created_at__lt=end_date).get("result", {}).get("count")
        num = count // 100
        for i in range(num+1):
            r = self.get_json(url="https://app.hightouch.ai/api/bot/messages/",
                              shop_id=shop_id, chat=chat, created_at__gte=start_date,
                              created_at__lt=end_date, offset=i * 100)
            if r.get("result", {}).get("count") != count and r.get("result", {}).get("count") > 100:
                raise Exception("The count has been increased by 1, please retry")
            results: list = r.get("result", {}).get("results")
            messages_timestamps = [x.get("created_at") for x in results if x.get("direction") in (1, 2)]
            messages_timestamp_list.extend(messages_timestamps)
        return messages_timestamp_list

    def get_user_messages_timestamp_list(self, shop_id, chat, start_date, end_date):  #datetime.datetime(2022,2,1).timestamp()
        user_messages_timestamp_list = []
        count = self.get_json(url="https://app.hightouch.ai/api/bot/messages/",
                              shop_id=shop_id, chat=chat, limit=1, created_at__gte=start_date,
                              created_at__lt=end_date).get("result", {}).get("count")
        num = count // 100
        for i in range(num+1):
            r = self.get_json(url="https://app.hightouch.ai/api/bot/messages/",
                              shop_id=shop_id, chat=chat, created_at__gte=start_date,
                              created_at__lt=end_date, offset=i * 100)
            if r.get("result", {}).get("count") != count and r.get("result", {}).get("count") > 100:
                raise Exception("The count has been increased by 1, please retry")
            results: list = r.get("result", {}).get("results")
            user_messages_timestamps = [x.get("created_at") for x in results if x.get("direction") == 1]
            user_messages_timestamp_list.extend(user_messages_timestamps)
        return user_messages_timestamp_list
    def count_windows(self, shop_id, chat, start_date, end_date):
        timestamps_list: list = self.get_messages_timestamp_list(shop_id=shop_id, chat=chat,
                                                           start_date=start_date, end_date=end_date)
        if timestamps_list:
            count = 1
            window_sec = 24 * 60 * 60
            # current = timestamps_list[-1]
            for n in range(1, len(timestamps_list)):
                if (timestamps_list[-n - 1] - timestamps_list[-n]) >= window_sec:
                    count += 1
        else:
            count = 0
        return count