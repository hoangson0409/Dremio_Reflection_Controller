from celery import shared_task
from .models import *
# from django.http import JsonResponse, HttpResponseRedirect
# import os
from datetime import datetime
from .utils.api_functions import *
import requests
import pandas as pd
import numpy as np
from .utils.udf import processCreatedAt, getParentDataset, checkParentDataset, returnDjangoItems


# Define here due to global variable
def requestCatalogRecursive(container_tab_var):
    global catalog_tab
    if 'containerType' not in container_tab_var:
        container_tab_var['containerType'] = np.nan
    # separate container tab by containerType
    container_tab_var_to_call = container_tab_var[~container_tab_var['containerType'].isna()]
    # if container_tab_var_to_call has content : create for loop then call each inside
    if len(container_tab_var_to_call) > 0:
        for _id in container_tab_var_to_call['id']:
            url = base_url + '/api/v3/catalog/' + _id
            response = requests.request("GET", url, headers=getHeaders())
            catalog = pd.json_normalize(response.json()['children'])
            catalog_tab = catalog_tab.append(catalog)
            requestCatalogRecursive(catalog)
    catalog_tab = catalog_tab.append(container_tab_var)
    return catalog_tab.drop_duplicates(subset=['id']).reset_index(drop=True)


# @shared_task(name="Get Reflections")
# def getReflectionTask():
#     start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
#     # resp_json = refreshReflection(reflection_id)  # refresh reflection
#     all_reflections = Reflection.objects.all()
#     for ref in all_reflections:
#         # print(ref.name)
#         resp_json = getReflection(str(ref.reflection_id))
#         ref_df = pd.json_normalize(resp_json, max_level=0)
#         ref_df['createdAt'] = ref_df['createdAt'].apply(processCreatedAt)
#         ref_df['updatedAt'] = ref_df['updatedAt'].apply(processCreatedAt)
#         ref_df = ref_df.rename(columns={"id": "reflection_id"}).reset_index(drop=True)
#         ref_items = returnDjangoItems(ref_df, 'reflection')
#         for ref_item in ref_items:
#             print(ref_item)
#         Dataset.objects.bulk_update_or_create(ref_items,
#                                               match_field=['reflection_id'],
#                                               update_fields=['tag', 'name', 'type', 'currentSizeBytes', 'totalSizeBytes',
#                                                              'arrowCachingEnabled', 'createdAt', 'updatedAt',
#                                                              'displayFields', 'partitionDistributionStrategy'])
#         print('DONE GETTING REFLECTION')
#     end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
#     print("started from", start_time, "to", end_time)


@shared_task(name="Refresh Reflection")
def refreshReflectionTask(reflection_id):
    """
    Refresh the chosen reflections
    :param reflection_id:
    :return:
    """
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    # Check Parent Reflections
    if checkParentDataset(reflection_id):
        resp_json = refreshReflection(reflection_id)  # refresh reflection
        Reflection.objects. \
            filter(reflection_id=reflection_id). \
            update(tag=resp_json['tag'],
                   createdAt=resp_json['createdAt'],
                   name=resp_json['name'],
                   currentSizeBytes=resp_json['currentSizeBytes'],
                   totalSizeBytes=resp_json['totalSizeBytes'],
                   enabled=resp_json['enabled'],
                   status=resp_json['status'],
                   partitionDistributionStrategy=resp_json['partitionDistributionStrategy']
                   )
        print('Refreshed:', resp_json['name'])
    else:
        print('Skip due to Parent Datasets not Reflected')
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    print("started from", start_time, "to", end_time)


@shared_task(name="Refresh Datasets")
def refreshDataset():
    print('START DATASET JOB')
    catalogs = Catalog.objects.all().filter(type='DATASET')
    datasets = pd.DataFrame(columns=['id', 'path', 'tag', 'type', 'createdAt', 'sql', 'sqlContext', 'fields'])
    for cat in catalogs:
        print(cat.path)
        datasets = datasets.append(getDataset(str(cat.catalog_id)))
    datasets['path'] = datasets['path'].astype(str).apply(processPath)
    datasets['createdAt'] = datasets['createdAt'].apply(processCreatedAt)
    datasets['parent_datasets'] = datasets['sql'].apply(getParentDataset)
    datasets = datasets.rename(columns={"id": "dataset_id"}).reset_index(drop=True)
    # Returning list of django items & Adding to db
    dataset_items = returnDjangoItems(datasets, 'dataset')
    Dataset.objects.bulk_update_or_create(dataset_items,
                                          match_field=['dataset_id'],
                                          update_fields=['tag', 'path', 'type', 'sql', 'sqlContext',
                                                         'fields', 'createdAt', 'parent_datasets'])
    print('DONE REFRESHING DATASET')


@shared_task(name="Refresh Catalogs")
def refreshCatalog():
    print('START CATALOG JOB')
    global catalog_tab
    response = requests.request("GET", url_catalog, headers=getHeaders())
    result_json = response.json()
    initial_catalog = pd.json_normalize(result_json['data'])
    initial_catalog = initial_catalog[initial_catalog['containerType'] == 'SPACE']
    catalog_tab = pd.DataFrame(columns=['id', 'path', 'tag', 'type', 'datasetType', 'containerType', 'createdAt'])
    catalog_tab = requestCatalogRecursive(initial_catalog)
    # Cleaning data
    catalog_tab['path'] = catalog_tab['path'].astype(str).apply(processPath)
    catalog_tab['createdAt'] = catalog_tab['createdAt'].apply(processCreatedAt)
    catalog_tab = catalog_tab.rename(columns={"id": "catalog_id"})
    # delete all existing Catalog
    Catalog.objects.all().delete()
    # Returning list of django items & Adding to db
    catalog_items_list = returnDjangoItems(catalog_tab, 'catalog')
    Catalog.objects.bulk_update_or_create(catalog_items_list,
                                          match_field=['catalog_id'],
                                          update_fields=['tag', 'path', 'type', 'datasetType', 'containerType'])
    print('DONE REFRESHING CATALOG')
