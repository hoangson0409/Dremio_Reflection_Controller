import re
# import pandas as pd
# from datetime import datetime as dt
from ..models import Catalog, Dataset, Reflection
from ast import literal_eval
from .api_functions import *


def getParentDataset(sql):
    ds_list = []
    for ds in re.findall('FROM (\w\S+)', sql.replace('"', '')):
        if 'external_query' not in ds:
            ds = ds.replace(')', '')
            ds = '"' + '"."'.join(ds.split('.')) + '"'
            if ds not in ds_list:
                ds_list.append(ds)
    for ds in re.findall('JOIN (\w\S+)', sql.replace('"', '')):
        ds = ds.replace(')', '')
        ds = '"' + '"."'.join(ds.split('.')) + '"'
        if ds not in ds_list:
            ds_list.append(ds)
    return ds_list


def processCreatedAt(x):
    if x == x:  # when createdAt value not nan
        x = dt.strftime(pd.to_datetime(x), "%Y-%m-%d %H:%M:%S")
    else:
        x = None
    return x


def processPath(x):
    x = x.replace("[", "").replace("]", "").replace(", ", ".").replace("\'", "\"")
    return x


# def preprocessData(df, dtype):
#     df['path'] = df['path'].astype(str).apply(processPath)
#     df['createdAt'] = df['createdAt'].apply(processCreatedAt)
#     if dtype == 'catalog':
#         df = df.rename(columns={"id": "catalog_id"})
#     elif dtype == 'dataset':
#         df = df.rename(columns={"id": "dataset_id"})
#     elif dtype == 'reflection':
#         df = df.rename(columns={"id": "reflection_id"})
#
#     df = df.where(pd.notnull(df), None)
#     return df


def returnDjangoItems(df, datatype):
    items = []
    if datatype == 'catalog':
        for index, row in df.iterrows():
            catalog_instance = Catalog(row['catalog_id'], row['path'], row['tag'], row['type'], row['datasetType'],
                                       row['containerType'], row['createdAt'])
            items.append(catalog_instance)
    elif datatype == 'dataset':
        for index, row in df.iterrows():
            dataset_instance = Dataset(row['dataset_id'], row['path'], row['tag'], row['type'], row['createdAt'],
                                       row['sql'], row['sqlContext'], row['fields'], row['parent_datasets'])
            items.append(dataset_instance)
    elif datatype == 'reflection':
        for index, row in df.iterrows():
            ref_instance = Reflection(row['reflection_id'], row['name'], row['tag'], row['type'], row['createdAt'],
                                      row['updatedAt'], row['currentSizeBytes'],
                                      row['totalSizeBytes'], row['arrowCachingEnabled'],  row['status'],
                                      row['displayFields'], row['partitionDistributionStrategy'])
            items.append(ref_instance)
    return items


def checkParentDataset(reflection_id):
    parent_reflection_ready_ = True
    parent_ds = Reflection.objects.get(reflection_id=reflection_id).datasetId.parent_datasets
    parent_ds = literal_eval(parent_ds)  # string to list
    print(parent_ds, type(parent_ds), len(parent_ds))
    for parent in parent_ds:
        if Reflection.objects.filter(datasetId__path=parent).exists():
            # print(Reflection.objects.filter(datasetId__path=ds_path).exists())
            parent_ref = Reflection.objects.get(datasetId__path=parent)
            parent_ref_id = str(parent_ref.reflection_id)
            resp_json = getReflection(parent_ref_id)
            Reflection.objects. \
                filter(reflection_id=parent_ref_id). \
                update(tag=resp_json['tag'],
                       createdAt=resp_json['createdAt'],
                       updatedAt=resp_json['updatedAt'],
                       name=resp_json['name'],
                       currentSizeBytes=resp_json['currentSizeBytes'],
                       totalSizeBytes=resp_json['totalSizeBytes'],
                       enabled=resp_json['enabled'],
                       status=resp_json['status'],
                       partitionDistributionStrategy=resp_json['partitionDistributionStrategy']
                       )
            parent_ref = Reflection.objects.get(datasetId__path=parent)
            parent_name = parent_ref.name
            parent_status = dict(parent_ref.status)
            print('parent with ref:', parent_name, parent_status['refresh'])
            if parent_status['refresh'] != 'SCHEDULED':
                print('STOP !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                parent_reflection_ready_ = False
        else:
            print('parent without ref:', parent)
    return parent_reflection_ready_
