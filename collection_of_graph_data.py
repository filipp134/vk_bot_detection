import json
import pandas as pd
import networkx as nx
import csv
from statistics import *

vk_prof_df = pd.read_csv("VK_profiles_info.csv")
graph_final_file = open("graph_final.json")
graph = dict((int(k), v)for k, v in json.load(graph_final_file).items())
graph_final_file.close()

def make_graph_for_user(user_id_1, uid2friends):
    """Создание графа друзей Вконтакте пользователя с user_id."""

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

def get_graph_features(graph_1, user_id): 
    id_degree = graph_1.degree(user_id)
    avg_cl = nx.average_clustering(graph_1)
    trans = nx.transitivity(graph_1)
    deg_centr = mean(nx.degree_centrality(graph_1).values())
    return (id_degree, avg_cl, trans, deg_centr)

with open('Graph_data.csv', 'a') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['uid', 'id_degree', 'avg_cl', 'trans', 'centr'])
    writer.writeheader()
    for uid in vk_prof_df.uid:
        graph_1 = make_graph_for_user(uid, graph)
        feat = get_graph_features(graph_1, uid)
        writer.writerow({'uid': uid, 'id_degree': feat[0], 'avg_cl': feat[1], 'trans': feat[2], 'centr': feat[3]})
