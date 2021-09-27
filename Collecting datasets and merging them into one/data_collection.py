# -*- coding: utf-8 -*-
#All libraries needed are imported.
import csv
import requests
from datetime import datetime
from time import time


BASIC_LINK = 'https://api.vk.com/method/'
ACCESS_TOKEN = ''

#Names of different user fields are given in general in USER_FIELDS list and split into 3 lists separately.
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
    """Dict with info about VK user with user_id for USER_FIELDS is received."""
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


def calculate_age(bdate: str):
    '''Function for calculating age for birthday date in format 'day.month.year(4 digits)'   '''
    #Birthday date is split to day, month, and year.
    bdate_list = bdate.split(".")
    if len(bdate_list) != 3:
        return None
    bday, bmonth, byear = bdate_list
    today = datetime.today() 
    return today.year - int(byear) - ((today.month, today.day) < (int(bmonth), int(bday)))


def transform_user_info(user_info):
    '''Function transforms user info.'''
    transformed_user_info = {
        "uid": user_info['id']
    }
    for user_field in PURE_FIELDS:
        transformed_user_info[user_field] = user_info.get(user_field, None)
    for user_field in PRESENTED_FIELDS:
        #This line checks if any info is on profile.
        transformed_user_info[user_field] = int(user_field in user_info)
    for user_field in COUNTER_FIELDS:
        transformed_user_info[user_field] = user_info["counters"][user_field]

    transformed_user_info["age"] = calculate_age(user_info["bdate"]) if "bdate" in user_info else None

    transformed_user_info["city"] = user_info["city"]["id"] if "city" in user_info else None

    transformed_user_info["country"] = user_info["country"]["id"] if "country" in user_info else None

    return transformed_user_info




def write_user_info_to_csv(user_info, filename):
    '''This function takes all user info for all users and makes a csv-file with it.'''
    with open(filename, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=user_info[0].keys())
        writer.writeheader()
        for user in user_info:
            writer.writerow(user)


def main():
    #All user_ids from VK_UIDS.csv are extracted and put to the list users.
    users = []
    with open('VK_UIDS.csv') as file:
        for line in file:
            pl = line.find(',')
            uid = int(line[:pl]) if line[:pl] != 'uid' else 'uids'
            users.append(uid)
    #User info is first received, transformed, and then put to user_info list 
    user_info = [transform_user_info(get_user_info(x)) for x in users]
    write_user_info_to_csv(user_info, "VK_profiles_info.csv")


if __name__ == '__main__':
    main()
