from rest_framework import serializers

#---------------- import model------------------
from apiApp.models import everside_nps,everside_nps_word_frequency
#--------------------------------------------------


class eversideNpsDataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = everside_nps
        fields = [  'id',
                    'review_ID',
                    'review',
                    'label',
                    'polarity_score',
                    'nps_score',
                    'nps_label',
                    'date',
                    'clinic',
                    'city',
                    'state',
                    'day',
                    'month',
                    'year']

class eversideAlertComments(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = everside_nps
        fields = [
                'review',
                'label',
                'date'
                ]


class eversideTopComments(serializers.HyperlinkedModelSerializer):
    class Meta:
        model =  everside_nps
        fields = [
                'review',
                'label'
                ]

class eversideWordFrequencySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = everside_nps_word_frequency
        fields = [
                'word',
                'frequency'
                ]