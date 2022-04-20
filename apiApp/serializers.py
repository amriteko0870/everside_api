from rest_framework import serializers

#---------------- import model------------------
from apiApp.models import everside_nps
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