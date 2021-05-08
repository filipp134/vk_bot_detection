# -*- coding: utf-8 -*-
import csv
import requests
import time
from bs4 import BeautifulSoup

AUTHORIZATION_LINK = 'https://oauth.vk.com/authorize?client_id=7781918&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=offline&response_type=token&v=5.52'
BASIC_LINK = 'https://api.vk.com/method/'
ACCESS_TOKEN = '03b514fe3f199471fc77c727575320360cbd8895d5ac6fe464572df08e2d44b8a2ecb513a6f91184bc3bd'

GROUP_NAME = "ria"
FAKE_SITE = "https://gosvon.net/"
VK_UIDS = "VK_UIDS.csv"


def get_group_id(group_name):
    """Получение id группы из названия группы, указанного в ссылке по типу https://vk.com/whoinrussia"""
    method = 'utils.resolveScreenName?screen_name={screen_name}&access_token={access_token}&v={api_version}'
    payload = {'screen_name': group_name, 'access_token': ACCESS_TOKEN, 'v': '5.130'}
    response = requests.get(BASIC_LINK + method, params=payload).json()
    return response['response']['object_id']


def get_1000members_ids(group_id, offset):
    """Получение id 1000 членов группы по id группы"""
    method = 'groups.getMembers?group_id={group_id}&access_token={access_token}&v={api_version}'
    payload = {
        'group_id': group_id,
        'offset': offset,
        'sort': 'id_desc',
        'v': '5.130',
        'access_token': ACCESS_TOKEN
    }
    response = requests.get(BASIC_LINK + method, params=payload).json()
    return response['response']['items']


def get_member_uids(group_name, cnt):
    group_id = get_group_id(group_name)
    member_ids = list()
    for offset in range(0, cnt, 1000):
        member_ids.extend(get_1000members_ids(group_id, offset))
        time.sleep(5)
    return member_ids


def get_fake_uids(fake_site):
    res = requests.get(fake_site)
    soup = BeautifulSoup(res.content, "html.parser")
    vk_fake_uids = list()
    for td in soup.find_all("table")[3].find_all("tr")[1:]:
        vk_fake_uids.append(int(td.find_all("td")[3].center.input.get("value")))
    return vk_fake_uids


def write_user_info_to_csv(member_uids, vk_fake_uids, filename):
    with open(filename, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['uid', 'target'])
        writer.writeheader()
        for uid in member_uids:
            writer.writerow({'uid': uid, 'target': 0})
        for uid in vk_fake_uids:
            writer.writerow({'uid': uid, 'target': 1})


def main():
    vk_fake_uids = get_fake_uids(FAKE_SITE)
    member_uids = get_member_uids(GROUP_NAME, 10000)
    member_uids = list(set(member_uids) - set(vk_fake_uids))
    write_user_info_to_csv(member_uids, vk_fake_uids, VK_UIDS)


if __name__ == '__main__':
    main()
