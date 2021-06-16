from rest_framework import serializers

from data import models

class DataSerializer(serializers.HyperlinkedModelSerializer):

    country = serializers.StringRelatedField(many=False)
    source = serializers.StringRelatedField(many=False)
    entities = serializers.StringRelatedField(many=True)

    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super(DataSerializer, self).__init__(*args, **kwargs)

        fields = self.context['request'].query_params.get('fields')
        if fields:
            fields = fields.split(',')
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)
                
    class Meta:
        model = models.Data
        fields = ['date_created', 'country', 'source', 'text', 'url',
                'sentiment', 'language', 'entities', 'metadata']

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