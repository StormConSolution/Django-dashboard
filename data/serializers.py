from rest_framework import serializers

from data.models import Data

class DataSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Data
        fields = ['date_created', 'text', 'sentiment', 'weighted_score', 'language',]
