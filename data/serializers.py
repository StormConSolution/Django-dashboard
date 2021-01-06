from rest_framework import serializers

from data.models import Data

class DataSerializer(serializers.HyperlinkedModelSerializer):

    country = serializers.StringRelatedField(many=False)
    source = serializers.StringRelatedField(many=False)
    keywords = serializers.StringRelatedField(many=True)
    entities = serializers.StringRelatedField(many=True)
    
    class Meta:
        model = Data
        fields = ['date_created', 'country', 'source', 'text', 'keywords',
                'sentiment', 'weighted_score', 'language', 'entities']
