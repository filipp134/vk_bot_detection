# -*- coding: utf-8 -*-

import csv
import requests
from datetime import datetime
from time import time


AUTHORIZATION_LINK = 'https://oauth.vk.com/authorize?client_id=7781918&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=offline&response_type=token&v=5.52'
BASIC_LINK = 'https://api.vk.com/method/'
ACCESS_TOKEN = '03b514fe3f199471fc77c727575320360cbd8895d5ac6fe464572df08e2d44b8a2ecb513a6f91184bc3bd'

USER_FIELDS = [
    "has_photo", "sex", "bdate", "city", "country", "has_mobile", "contacts", "followers_count", "relatives",
    "relation", "personal", "activities", "music", "movies", "tv", "books", "about", "quotes", "counters"
]

PURE_FIELDS = [
    "has_photo", "sex", "has_mobile", "followers_count"
]

PRESENTED_FIELDS = [
    "contacts", "relatives", "relation", "personal", "activities", "music", "movies", "tv", "books", "about", "quotes"
]

COUNTER_FIELDS = [
    "albums", "audios", "followers", "friends", "pages", "photos", "subscriptions", "videos", "clips_followers"
]


def get_user_info(user_id):
    """Получение информации в виде словаря о пользователе ВКонтакте с user_id."""
    method = 'users.get?user_ids={user_ids}&fields={fields}&access_token={access_token}&v={api_version}'
    payload = {
        'user_ids': [user_id],
        'fields': ','.join(USER_FIELDS),
        'v': '5.130',
        'access_token': ACCESS_TOKEN
    }
    response = requests.get(BASIC_LINK + method, params=payload).json()
    info = response['response'][0]
    return info


def __calculate_age(bdate: str):
    bdate_list = bdate.split(".")
    if len(bdate_list) != 3:
        return None
    bday, bmonth, byear = bdate
    today = datetime.today()
    return today.year - int(byear) - ((today.month, today.day) < (int(bmonth), int(bday)))


def transform_user_info(user_info):
    transformed_user_info = {
        "uid": user_info['id']
    }
    for user_field in PURE_FIELDS:
        transformed_user_info[user_field] = user_info.get(user_field, None)
    for user_field in PRESENTED_FIELDS:
        transformed_user_info[user_field] = int(user_field in user_info)
    for user_field in COUNTER_FIELDS:
        transformed_user_info[user_field] = user_info["counters"][user_field]

    transformed_user_info["age"] = __calculate_age(user_info["bdate"]) if "bdate" in user_info else None

    transformed_user_info["city"] = user_info["city"]["id"] if "city" in user_info else None

    transformed_user_info["country"] = user_info["country"]["id"] if "country" in user_info else None

    return transformed_user_info




def write_user_info_to_csv(user_info, filename):
    with open(filename, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=user_info[0].keys())
        writer.writeheader()
        for user in user_info:
            writer.writerow(user)


def main():
    users = []
    with open('VK_UIDS.csv') as file:
        for line in file:
            pl = line.find(',')
            uid = int(line[:pl]) if line[:pl] != 'uid' else 'uids'
            users.append(uid)
    user_info = [transform_user_info(get_user_info(x)) for x in users]
    write_user_info_to_csv(user_info, "VK_profiles_info.csv")


if __name__ == '__main__':
    main()
