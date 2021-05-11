# -*- coding: utf-8 -*-
#All libraries needed are imported.
import csv
import requests
import time
from bs4 import BeautifulSoup

#AUTHORIZATION_LINK is just for usage if new ACCESS_TOKEN needed.
AUTHORIZATION_LINK = 'https://oauth.vk.com/authorize?client_id=7781918&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=offline&response_type=token&v=5.52'
BASIC_LINK = 'https://api.vk.com/method/'
ACCESS_TOKEN = '03b514fe3f199471fc77c727575320360cbd8895d5ac6fe464572df08e2d44b8a2ecb513a6f91184bc3bd'

#GROUP_NAME is the 'ria' since I will be receiving approx. 1000 real users from it.
GROUP_NAME = "ria"

#FAKE_SITE is the site where ids of detected VK bots are given.
FAKE_SITE = "https://gosvon.net/"

VK_UIDS = "VK_UIDS.csv"


def get_group_id(group_name):
    """Receiving group id by the name of it given in a link like this https://vk.com/whoinrussia"""
    method = 'utils.resolveScreenName?screen_name={screen_name}&access_token={access_token}&v={api_version}'
    payload = {'screen_name': group_name, 'access_token': ACCESS_TOKEN, 'v': '5.130'}
    response = requests.get(BASIC_LINK + method, params=payload).json()
    return response['response']['object_id']


def get_1000members_ids(group_id, offset):
    """Receiving 1000 ids of members of the group with group_id and offset."""
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
    '''Returning list with member ids of a group with group_name. The number of these ids are given by cnt.'''
    group_id = get_group_id(group_name)
    member_ids = list()
    for offset in range(0, cnt, 1000):
        member_ids.extend(get_1000members_ids(group_id, offset))
        time.sleep(5)
    return member_ids


def get_fake_uids(fake_site):
    '''The website with detected bots is parsed using Beatiful Soup and all fake ids are returned in a list.'''
    res = requests.get(fake_site)
    soup = BeautifulSoup(res.content, "html.parser")
    vk_fake_uids = list()
    for td in soup.find_all("table")[3].find_all("tr")[1:]:
        vk_fake_uids.append(int(td.find_all("td")[3].center.input.get("value")))
    return vk_fake_uids


def write_user_info_to_csv(member_uids, vk_fake_uids, filename):
    '''Uids of real users and bots are written into csv file with targets 0 and 1 respectively.'''
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
    #Bots are excluded from the list of real users.
    member_uids = list(set(member_uids) - set(vk_fake_uids))
    write_user_info_to_csv(member_uids, vk_fake_uids, VK_UIDS)


if __name__ == '__main__':
    main() 
