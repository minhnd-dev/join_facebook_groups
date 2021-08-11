import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch import helpers

es = Elasticsearch([{'host':'localhost', 'port': 9200}])
if not es.ping():
    print("Failed to initiate connection to Elasticsearch")
if not es.indices.exists(index = "account_monitor"):
    es.indices.create(index = "account_monitor")
    print("Created index account_monitor")

#update data from elasticsearch
groups_df = pd.read_csv("outfile.csv")
account = {}
for _, row in groups_df.iterrows():
    for acc in row['joined_accounts'].split(","):
        if acc == "":
            continue
        if acc in account:
            if row['group_id'] not in account[acc]:
                account[acc].append(row['group_id'])
        else:
            account[acc] =[row['group_id']]
# add new account to elasticsearch
account_checkpoint = {}
accounts_df = pd.read_csv("fb_accounts.csv")

for _, row in accounts_df.iterrows():
    groups_list = []
    if row['user'] in account:
        groups_list = account[row['user']]
    account_checkpoint[row['user']] = {
        "account": row['user'],
        "is_checkpoint": row['is_checkpointed'],
        "group_ids": groups_list
    }

actions = []

print(account_checkpoint)

for acc in account_checkpoint:
    actions.append({
    "_index": "account_monitor",
    "_id": acc,
    "_source": account_checkpoint[acc]
    })
helpers.bulk(es, actions)




# res = es.search(index="account_monitor", doc_type="_doc", 
#                 body = {
#                     'size' : 10000,
#                     'query': {
#                         'match_all' : {}
#                     }
#                 })

# account_data = res['hits']['hits']


# actions = []
# for key, value in account.items():
#     actions.append({
#     "_index": "account_monitor",
#     "_id": key,
#     "_source": {
#         "account":key,
#         "is_checkpoint": False,
#         "group_ids": value
#         }
#     })

# print(actions)
# print("Inserting to es")