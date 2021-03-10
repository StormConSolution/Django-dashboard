from rest_framework import serializers

from data import models

class DataSerializer(serializers.HyperlinkedModelSerializer):

    country = serializers.StringRelatedField(many=False)
    source = serializers.StringRelatedField(many=False)
    keywords = serializers.StringRelatedField(many=True)
    entities = serializers.StringRelatedField(many=True)
    
    class Meta:
        model = models.Data
        fields = ['date_created', 'country', 'source', 'text', 'url',
                'sentiment', 'weighted_score', 'language', 'entities']

class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Source
        fields = '__all__'


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Country
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project
        fields = ['id', 'name']

