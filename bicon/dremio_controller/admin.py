from django.contrib import admin
from . import models
from . import forms
from .admin_actions import refreshReflectionAction, getReflectionAction, scheduleReflectionAction
from .utils.api_functions import url_ref, getHeaders
import requests
from .csvexport.actions import csvexport
# from django.utils.html import format_html

# Register your models here.


class CatalogAdmin(admin.ModelAdmin):
    model = models.Catalog
    list_display = ('__str__', 'catalog_id', 'createdAt', 'path', 'tag', 'type',
                    'createdAt', 'containerType', 'datasetType')
    date_hierarchy = 'createdAt'
    search_fields = ('path', 'catalog_id')
    list_filter = ['type']
    actions = [csvexport]


class DatasetAdmin(admin.ModelAdmin):
    model = models.Dataset
    readonly_fields = ['dataset_id',]
    list_display = ('__str__', 'dataset_id', 'createdAt', 'path', 'tag', 'type',
                    'createdAt', 'sqlContext', 'parent_datasets'
                    # 'sql',
                    # 'fields'
                    )
    list_filter = ['path']
    search_fields = ('path', 'dataset_id')
    date_hierarchy = 'createdAt'
    actions = [csvexport]


class ReflectionAdmin(admin.ModelAdmin):
    form = forms.ReflectionForm
    model = models.Reflection
    readonly_fields = ['reflection_id', 'tag', 'status']
    list_display = ('__str__', 'reflection_id', 'datasetId', 'type', 'name', 'tag',
                    'createdAt', 'updatedAt', 'currentSizeBytes', 'totalSizeBytes',
                    'enabled', 'arrowCachingEnabled', 'status', 'scheduled_crontab',
                    # 'displayFields',
                    'partitionDistributionStrategy')
    list_filter = ['name', 'enabled', 'type', 'arrowCachingEnabled']
    search_fields = ('reflection_id', 'name')
    date_hierarchy = 'updatedAt'

    # override delete function in Django Admin
    def delete_queryset(self, request, queryset):
        for query in queryset:
            url = url_ref + str(query.reflection_id)
            requests.request("DELETE", url=url, headers=getHeaders())
        queryset.delete()
    # TODO: override save_form admin function
    actions = [refreshReflectionAction, csvexport, getReflectionAction, scheduleReflectionAction]
    autocomplete_fields = ['datasetId']


admin.site.register(models.Reflection, ReflectionAdmin)
admin.site.register(models.Dataset, DatasetAdmin)
admin.site.register(models.Catalog, CatalogAdmin)
