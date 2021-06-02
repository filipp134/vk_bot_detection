import pandas as pd
vk_prof_df = pd.read_csv('VK_profiles_info.csv')
vk_target_df = pd.read_csv('VK_UIDS.csv')
graph_data = pd.read_csv('Graph_data.csv')
uids = vk_target_df['uid'].tolist()
graph_data['uid'] = uids
first_merge_df = pd.merge(vk_prof_df, graph_data, how='outer', on='uid')
df = pd.merge(first_merge_df, vk_target_df, how='outer', on='uid')
df.fillna(value=0, axis=1, inplace=True)
df.to_csv('Dataset_for_VK_project.csv')
