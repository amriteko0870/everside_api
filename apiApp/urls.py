from unicodedata import name
from django.urls import path,include
from . import views


urlpatterns = [
        path('netPromoterScore',views.netPromoterScore,name='netPromoterScore'),
        path('netSentimentScore',views.netSentimentScore,name='netSentimentScore'),
        path('npsOverTime',views.npsOverTime,name='npsOverTime'),
        path('nssOverTime',views.nssOverTime,name='nssOverTime'),
        path('npsVsSentiments',views.npsVsSentiments,name='npsVsSentiments'),
        path('alertComments',views.alertComments,name='alertComments'),
        path('topComments',views.topComments,name='topComments'),
        path('totalComments',views.totalComments,name='totalComments'),
        path('clinics_data',views.clinics_data,name='clinics_data'),
        path('totalCards',views.totalCards,name='totalCards'),
        path('wordFrequency',views.wordFrequency,name='wordFrequency'),
        path('cityStateClinics',views.cityStateClinics,name='cityStateClinics'),
        path('egStatistics',views.egStatistics,name='egStatistics'),
        path('egPercentileMember',views.egPercentileMember,name='egPercentileMember'),

        #path('store_data',views.store_data,name='store_data')
]


