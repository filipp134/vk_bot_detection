# -*- coding: utf-8 -*-

import json
import pandas as pd
from threading import Thread

import requests
from time import time, sleep


BASIC_LINK = 'https://api.vk.com/method/'
ACCESS_TOKEN = '03b514fe3f199471fc77c727575320360cbd8895d5ac6fe464572df08e2d44b8a2ecb513a6f91184bc3bd'
VK_UIDS = "VK_UIDS.csv"
START_UID = 0


def get_friends_ids(user_id, uid2friends):
    """Addition of friends ids to dictionary uid2friends"""

    method = 'friends.get?user_id={user_id}&count={count}&offset={offset}&access_token={access_token}&v={api_version}'
    payload = {
        'user_id': user_id,
        'count': 500,
        'offset': 1,
        'order': 'random',
        'v': '5.130',
        'access_token': ACCESS_TOKEN
    }
    response = requests.get(BASIC_LINK + method, params=payload).json()
    #Check for any errors occuring
    if 'response' in response:
        uid2friends[user_id] = response['response']['items']
    else:
        print(response['error']['error_msg'])
        uid2friends[user_id] = []


def make_graph(user_id_1, uid2friends):
    """Dict with list of friends is created."""
    #List of friends is added to dictionary uid2friends.
    if user_id_1 not in uid2friends:
        get_friends_ids(user_id_1, uid2friends)
        sleep(0.3)

    friends_ids = set(uid2friends[user_id_1])
    for uid in friends_ids:
        #Check if list if friends for uid hadn't been received.
        if uid in uid2friends:
            continue
        get_friends_ids(uid, uid2friends)
        sleep(0.3)


def main():
    vk_uids_df = pd.read_csv(VK_UIDS)
    vk_uids = list(map(int, vk_uids_df['uid']))
    uid2friends = dict()
    for i, uid in enumerate(vk_uids):
        if i < START_UID:
            continue
        make_graph(uid, uid2friends)
        #Json file with all existing graph info is created after receiving info for every 100th user. 
        if i % 100 == 99:
            with open('graph_bump_{}.json'.format(i), 'w') as f:
                json.dump(uid2friends, f)

    with open('graph_final.json'.format(), 'w') as f:
        json.dump(uid2friends, f)


if __name__ == '__main__':
    main()
