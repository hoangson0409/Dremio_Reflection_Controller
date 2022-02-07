from rest_framework import serializers
from .models import *


class CatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Catalog
        fields = '__all__'


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = '__all__'


class ReflectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reflection
        fields = '__all__'

