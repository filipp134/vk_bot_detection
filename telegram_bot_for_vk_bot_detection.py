from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext, \
    ConversationHandler
import requests
from datetime import datetime
from time import time, sleep
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import json
import networkx as nx
import csv
from statistics import *

BASIC_LINK = 'https://api.vk.com/method/'
ACCESS_TOKEN = ''
TOKEN = ''

USER_FIELDS = [
    "has_photo", "sex", "bdate", "city", "country", "has_mobile", "counters"
]

PURE_FIELDS = [
    "has_photo", "sex", "has_mobile"
]

COUNTER_FIELDS = [
    "albums", "audios", "followers", "friends", "pages", "photos", "subscriptions", "videos", "clips_followers"
]
LIST_OF_FEATURES = [
    'avg_cl', 'trans', 'average_neighbor_degree', 'average_degree_connectivity', 'degree_centrality',
    'closeness_centrality', 'betweenness_centrality', 'diameter']
WELCOME_TEXT = '''I'm a bot, please talk to me!
If you give me the id of a VKontakte user, you will receive my prediction of whether 
the user is a bot or not. You can take the user id from the profile webpage of the user.
For example: the link to the profile webpage is https://vk.com/id123123123
Here, the user id is 123123123.
Sometimes the user id can be letters, but don't worry, I can process it.
I give the predictions of the nature of the user by analyzing the 37 feautures of the
user's profile and friend network using the machine learning model with the accuracy of 
98%. You can know more about the models and the features,
by going through this link: https://github.com/filipp134/vk_bot_detection'''
vk_prof_df = pd.read_csv("VK_profiles_info.csv")
#graph_final_file = open("graph_final.json")
#graph = dict((int(k), v)for k, v in json.load(graph_final_file).items())
#graph_final_file.close()

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
        print(user_id, type(user_id))
        uid2friends[user_id] = response['response']['items']
    else:
        print(response['error']['error_msg'])
        uid2friends[user_id] = []



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
    transformed_user_info = {}
    for user_field in PURE_FIELDS:
        transformed_user_info[user_field] = user_info.get(user_field, None)
    for user_field in COUNTER_FIELDS:
        try:
            transformed_user_info[user_field] = user_info["counters"][user_field]
        except:
            transformed_user_info[user_field] = None
    transformed_user_info["age"] = calculate_age(user_info["bdate"]) if "bdate" in user_info else None
    transformed_user_info["city"] = user_info["city"]["id"] if "city" in user_info else None
    transformed_user_info["country"] = user_info["country"]["id"] if "country" in user_info else None
    return transformed_user_info


def make_graph_for_user(user_id_1, uid2friends):
    graph = nx.Graph()
    graph.add_node(user_id_1)
    friends_ids = set(uid2friends[user_id_1])
    for friend_id in friends_ids:
        graph.add_edge(user_id_1, friend_id)
        friends_ids_2nd_gen = uid2friends[friend_id]
        for friend_id_2nd_gen in friends_ids_2nd_gen:
            if friend_id_2nd_gen in friends_ids:
                graph.add_edge(friend_id_2nd_gen, friend_id)
    return graph

def get_graph_features(graph_1): 
    avg_cl = nx.average_clustering(graph_1)
    trans = nx.transitivity(graph_1)
    try: 
        average_neighbor_degree = mean(nx.average_neighbor_degree(graph_1))
    except:
        average_neighbor_degree = None
    try:
        average_degree_connectivity = mean(nx.average_degree_connectivity(graph_1).values())
    except:
        average_degree_connectivity = None
    degree_centrality = mean(nx.degree_centrality(graph_1).values())
    closeness_centrality = mean(nx.closeness_centrality(graph_1).values())
    betweenness_centrality = mean(nx.betweenness_centrality(graph_1).values())
    diameter = nx.diameter(graph_1)
    features = [avg_cl, trans, average_neighbor_degree, average_degree_connectivity,
           degree_centrality, closeness_centrality, betweenness_centrality,  diameter]
    graph_info = dict()
    i = 0
    for feature in LIST_OF_FEATURES:
        graph_info[feature] = features[i]
        i += 1
    return graph_info

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=WELCOME_TEXT)
    return ConversationHandler.END

def go(update, context):
    msg = context.bot.send_message(chat_id=update.effective_chat.id, text='-' * 20)
    for i in range(1, 21):
        context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text="*" * i + '-' * (20 - i))
        sleep(0.3)
    return ConversationHandler.END
    
def make_prediction(person_df):
    model = joblib.load('model.pkl')
    prediction = model.predict(person_df)[0]
    pred_proba = model.predict_proba(person_df)[:,1][0]
    return (prediction, pred_proba)

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

def transform_user_info(user_info):
    '''Function transforms user info.'''
    transformed_user_info = {}
    for user_field in PURE_FIELDS:
        transformed_user_info[user_field] = user_info.get(user_field, None)
    for user_field in COUNTER_FIELDS:
        try:
            transformed_user_info[user_field] = user_info["counters"][user_field]
        except:
            transformed_user_info[user_field] = None
    transformed_user_info["age"] = calculate_age(user_info["bdate"]) if "bdate" in user_info else None
    transformed_user_info["city"] = user_info["city"]["id"] if "city" in user_info else None
    transformed_user_info["country"] = user_info["country"]["id"] if "country" in user_info else None
    return transformed_user_info

def make_graph(update, context, user_id_1, uid2friends):
    """Dict with list of friends is created."""
    get_friends_ids(user_id_1, uid2friends)
    sleep(0.3)

    friends_ids = set(uid2friends[user_id_1])
    n = len(friends_ids)
    cur = 0
    t = "Processed: "
    last_updated = 0
    msg = context.bot.send_message(chat_id=update.effective_chat.id, text=t+'0%')
    for uid in friends_ids:
        cur_perc = round(cur / n * 100)
        if last_updated < cur_perc:
            last_updated = cur_perc
            context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text=t+str(cur_perc) + '%')

        #Check if list if friends for uid hadn't been received.
        if uid in uid2friends:
            continue
        get_friends_ids(uid, uid2friends)
        cur += 1
        sleep(0.3)


def create_df_for_person(update, context, uid):
    info = get_user_info(uid)
    info = transform_user_info(info)
    graph = dict()
    make_graph(update, context, uid, graph)
    graph_1 = make_graph_for_user(uid, graph)
    graph_feat = get_graph_features(graph_1)
    combined_info = {**info, **graph_feat}
    person_df = pd.DataFrame({str(k): [v] for k, v in combined_info.items()})
    person_df.fillna(value=0, axis=1, inplace=True)
    return person_df

def deal_with_message(update, context):
    uid = update.message.text
    print(uid, type(uid))
    if not get_user_info(uid):
        context.bot.send_message(chat_id=update.effective_chat.id, text="User with such id is not found!")
        return ConversationHandler.END
    person_df = create_df_for_person(update, context, uid)
    pred = make_prediction(person_df)
    dec = pred[0]                                                                                                                    
    prob = pred[1]
    message = f'The user with id {uid} is'
    if dec == 0:
        message += f' not a bot with probability {1 - prob}'
    else:
        message += f' a bot with probability {prob}'
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    
def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    message_handler = MessageHandler(Filters.text & (~Filters.command), deal_with_message)
    start_handler = CommandHandler('start', start)
    go_handler = CommandHandler('go', go)
    dispatcher.add_handler(message_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(go_handler)
    updater.start_polling()

main()
