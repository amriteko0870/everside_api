from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd

#-------------import api serializers --------------------
from apiApp.serializers import eversideNpsDataSerializer
#--------------------------------------------------------

#---------------import models-----------------------------
from apiApp.models import everside_nps
#--------------------------------------------------------

#-------REST MODULES---------------------------
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http.response import JsonResponse
#-------------------------------------------------

# Create your views here.
@api_view(['GET'])
def index(request,format=None):   
    if request.method == 'GET':
        try:
            data = everside_nps.objects.all()
            data_serializer = eversideNpsDataSerializer(data, many=True)
            print(data_serializer)
            return JsonResponse(data_serializer.data, safe=False)

        except:
            return Response({'Message':'No Data Available'})

@api_view(['GET'])
def date_filter(request,format=None):
    if(request.method == 'GET'):
        try:
            data = request.data
            start_year = data['start_year']
            end_year = data['end_year']
            if(start_year == end_year):
                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+str(data['start_month'])+' AND year='+str(start_year)+') AND (CAST(month as inT)<='+str(data['end_month'])+' AND year='+str(end_year)+');'
                filter_data = everside_nps.objects.raw(query)            
                data_serializer = eversideNpsDataSerializer(filter_data, many=True)

            else:
                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+str(data['start_month'])+' AND year='+str(start_year)+') AND (CAST(month as inT)<=12'+' AND year='+str(start_year)+');'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1'+' AND year='+str(end_year)+') AND (CAST(month as inT)<='+str(data['end_month'])+' AND year='+str(end_year)+');'
                filter_data1 = everside_nps.objects.raw(query1)
                filter_data2 = everside_nps.objects.raw(query2)
                new_data = list(filter_data1)+list(filter_data2)
                data_serializer = eversideNpsDataSerializer(new_data, many=True)

            return JsonResponse(data_serializer.data, safe=False)
            
        except:
            return Response({'Message':'No Data Available'})

'''def data_store(request):
    df = pd.read_csv('C:/Users/Eko-3/Everside/full_data.csv')
    print(df.shape)
    print()
    print()
    for i in range(df.shape[0]):
        review_ID = list(df['ID'])[i]
        review = list(df['review'])[i]
        label = list(df['label'])[i]
        polarity_score = list(df['polarity_score'])[i]
        nps_score = list(df['nps_score'])[i]
        nps_label = list(df['nps_label'])[i]
        date = list(df['date'])[i]
        clinic = list(df['clinic'])[i]
        city = list(df['city'])[i]
        state = list(df['state'])[i]
        day = list(df['day'])[i]
        month = list(df['month'])[i]
        year = list(df['year'])[i]
        
        data = everside_nps.objects.create(review_ID = review_ID,
                                            review = review,
                                            label = label,
                                            polarity_score = polarity_score,
                                            nps_score = nps_score,
                                            nps_label = nps_label,
                                            date = date,
                                            clinic = clinic,
                                            city = city,
                                            state = state,
                                            day = day,
                                            month = month,
                                            year = year)
        data.save()
        print(i) 
    return HttpResponse('hello world')'''