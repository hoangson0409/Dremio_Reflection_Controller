import uuid
from ast import literal_eval

import json
import requests
from bulk_update_or_create import BulkUpdateOrCreateQuerySet
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import CrontabSchedule
# from django.db.models.signals import pre_save, post_save
# from django.dispatch import receiver
from .utils.api_functions import url_ref, getHeaders, processCreatedAt


# Create your models here.
class Catalog(models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()  # for bulk_update_or_create

    catalog_id = models.UUIDField(primary_key=True, unique=True)
    path = models.CharField(max_length=100)
    tag = models.CharField(max_length=100, null=True)
    type = models.CharField(max_length=100)
    containerType = models.CharField(max_length=100, null=True, blank=True)
    datasetType = models.CharField(max_length=100, null=True, blank=True)
    createdAt = models.DateTimeField(null=True)
    # TODO: Timezone warning for createdAt when create/update records


class Dataset(models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()  # for bulk_update_or_create

    dataset_id = models.UUIDField(primary_key=True, unique=True)
    path = models.CharField(max_length=100, unique=True)
    tag = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    createdAt = models.DateTimeField(null=True)
    sql = models.TextField()
    sqlContext = models.CharField(max_length=100)
    fields = models.TextField()  # json
    parent_datasets = models.TextField(null=True, blank=True)  # list

    def __str__(self):
        return self.path


class Reflection(models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()  # for bulk_update_or_create

    reflection_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    datasetId = models.ForeignKey(
        Dataset, on_delete=models.CASCADE,
        verbose_name=_('Parent Dataset'),
        db_column='datasetId'
        # help_text=_('....'),
    )
    type = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    tag = models.CharField(max_length=100)
    createdAt = models.DateTimeField(auto_now=True)
    updatedAt = models.DateTimeField(auto_now=True)
    currentSizeBytes = models.PositiveBigIntegerField(null=True, blank=True, )
    totalSizeBytes = models.PositiveBigIntegerField(null=True, blank=True, )
    enabled = models.BooleanField()
    arrowCachingEnabled = models.BooleanField(default=False)
    status = models.JSONField(null=True, blank=True, )
    displayFields = models.TextField(null=True, blank=True,
                                     help_text=_('Leave Blank to Select all Fields in the Dataset'))  # json
    partitionDistributionStrategy = models.CharField(max_length=15, null=True, blank=True,
                                                     help_text=_('Leave Blank for Default Selection'))
    scheduled_crontab = models.ForeignKey(
        CrontabSchedule, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name=_('Crontab Schedule'),
        help_text=_('Crontab Schedule to run the task on.'),
    )

    # override save() function to link with Dremio
    def save(self, *args, **kwargs):
        # def createReflection(sender, instance, **kwargs):
        dataset_instance = self.datasetId
        dataset_id = str(dataset_instance.dataset_id)
        dataset_fields = literal_eval(dataset_instance.fields)
        for i in dataset_fields:
            i.pop('type')
        body = {
            "type": self.type,
            "name": self.name,
            "datasetId": dataset_id,
            "enabled": 1,
            "arrowCachingEnabled": 0,
            "displayFields": dataset_fields,
            "partitionDistributionStrategy": "STRIPED",
            "entityType": "reflection"
        }
        # TODO: 1. more params for creating Reflections => function to alter reflection as dataset changed (**)
        ## 2. Function to update PeriodicTask (if exist) whenever reflection changed

        # POST request to create real reflection in Dremio
        # get_resp = requests.request('GET', url=url_ref + str(self.reflection_id))
        # print(get_resp.status_code)
        # if get_resp.status_code != 200:
        # TODO: change save behavior: not create after update
        post_resp = requests.request('POST',
                                     url=url_ref,
                                     data=json.dumps(body),
                                     headers=getHeaders())
        # print(post_resp.json())
        response_json = post_resp.json()
        self.reflection_id = response_json['id']
        self.type = response_json['type']
        self.name = response_json['name']
        self.tag = response_json['tag']
        self.createdAt = processCreatedAt(response_json['createdAt'])
        self.updatedAt = processCreatedAt(response_json['updatedAt'])
        self.currentSizeBytes = response_json['currentSizeBytes']
        self.totalSizeBytes = response_json['totalSizeBytes']
        self.enabled = response_json['enabled']
        self.arrowCachingEnabled = response_json['arrowCachingEnabled']
        self.status = response_json['status']
        self.displayFields = response_json['displayFields']
        self.partitionDistributionStrategy = response_json['partitionDistributionStrategy']
        super(Reflection, self).save(*args, **kwargs)
        # super(Reflection, self).save(*args, **kwargs)

    # override delete() function to link with Dremio (but not related to Django Admin)
    def delete(self):
        url = url_ref + self.reflection_id
        requests.request("DELETE", url=url, headers=getHeaders())
        print('deleted: ', self.reflection_id)
        super(Reflection, self).delete()
