# import os
from django.contrib import admin
from .utils.api_functions import refreshReflection, getReflection
from .models import *
from django_celery_beat.models import PeriodicTask
from datetime import datetime as dt


@admin.action(description='Refresh Reflection')
def refreshReflectionAction(modeladmin, request, queryset):
    """
    Admin action to manually refresh reflections.
    """
    for row in queryset.all():
        reflection_id = str(row.reflection_id)
        print('refreshing ', row.name, ': ', reflection_id)
        # Refresh in Dremio
        resp_json = refreshReflection(reflection_id)
        # Update to db
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
        print(resp_json)


@admin.action(description='Get Reflection')
def getReflectionAction(modeladmin, request, queryset):
    """
    Admin action to get information of reflections.
    """
    for row in queryset.all():
        reflection_id = str(row.reflection_id)
        print('getting ', row.name, ': ', reflection_id)
        resp_json = getReflection(reflection_id)
        Reflection.objects. \
            filter(reflection_id=reflection_id). \
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
        print('DONE:', resp_json)


@admin.action(description='Schedule Reflection')
def scheduleReflectionAction(modeladmin, request, queryset):
    """
    Admin action to get information of reflections.
    """
    for row in queryset.all():
        if row.scheduled_crontab is not None:
            reflection_id = str(row.reflection_id)
            ref_instance = Reflection.objects.get(reflection_id=reflection_id)
            task_name = 'refresh_' + ref_instance.datasetId.path.replace('"', '')
            scheduled_crontab = ref_instance.scheduled_crontab
            task_args = '["' + reflection_id + '"]'
            task = 'Refresh Reflection'
            task_enabled = True
            task_start_time = dt.utcnow()
            # task_start_time = dt.fromisoformat('2021-12-23 00:00:00+00:00')
            periodic_task_instance = PeriodicTask(name=task_name,
                                                  task=task,
                                                  crontab=scheduled_crontab,
                                                  args=task_args,
                                                  start_time=task_start_time,
                                                  enabled=task_enabled
                                                  )
            periodic_task_instance.save()
            print('Scheduled', row.name, '(', reflection_id, ') at', scheduled_crontab)
        else:
            print('Please enter the crontab time for schedule')


# @admin.action(description='Test')
# def waitParentDataset(modeladmin, request, queryset):
#     # """
#     # Admin action to get information of reflections.
#     # """
#     for row in queryset.all():
#         # all_refs = Reflection.objects.all()
#         # for ref in all_refs:
#         parent_ds = row.datasetId.parent_datasets
#         parent_ds = literal_eval(parent_ds)  # string to list
#         print(parent_ds, type(parent_ds), len(parent_ds))
#         for parent in parent_ds:
#             if Reflection.objects.filter(datasetId__path=parent).exists():
#                 # print(Reflection.objects.filter(datasetId__path=ds_path).exists())
#                 parent_ref = Reflection.objects.get(datasetId__path=parent)
#                 parent_ref_id = str(parent_ref.reflection_id)
#                 resp_json = getReflection(parent_ref_id)
#                 Reflection.objects. \
#                     filter(reflection_id=parent_ref_id). \
#                     update(tag=resp_json['tag'],
#                            createdAt=resp_json['createdAt'],
#                            updatedAt=resp_json['updatedAt'],
#                            name=resp_json['name'],
#                            currentSizeBytes=resp_json['currentSizeBytes'],
#                            totalSizeBytes=resp_json['totalSizeBytes'],
#                            enabled=resp_json['enabled'],
#                            status=resp_json['status'],
#                            partitionDistributionStrategy=resp_json['partitionDistributionStrategy']
#                            )
#                 parent_ref = Reflection.objects.get(datasetId__path=parent)
#                 parent_name = parent_ref.name
#                 parent_status = dict(parent_ref.status)
#                 print('parent with ref:', parent_name, parent_status['refresh'])
#                 if parent_status['refresh'] != 'SCHEDULED':
#                     print('STOP !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
#             else:
#                 print('parent without ref:', parent)

