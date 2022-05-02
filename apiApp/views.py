from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import json
import random

#-------------import api serializers --------------------
from apiApp.serializers import eversideNpsDataSerializer,eversideAlertComments,eversideTopComments,eversideWordFrequencySerializer
#--------------------------------------------------------

#---------------import models-----------------------------
from apiApp.models import everside_nps,everside_nps_clinics,everside_nps_word_frequency
#--------------------------------------------------------

#-------REST MODULES---------------------------
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http.response import JsonResponse
#-------------------------------------------------

# Create your views here.
#---------------------Dashboard API Start here--------------------------------------------
            
@api_view(['GET'])
def netPromoterScore(request,format=None):
    if request.method == 'GET':
        try:
            #data = request.data
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')

            #start_year = str(data['start_year'])
            #start_month = str(data['start_month'])
            #end_year = str(data['end_year'])
            #end_month = str(data['end_month'])

            if start_year == end_year:
                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+str(start_month)+' AND year='+str(start_year)+') AND (CAST(month as inT)<='+str(end_month)+' AND year='+str(end_year)+');'
                print(query)
                count = everside_nps.objects.raw(query)
                total_count = len(count)

                query = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Promoter" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                count = everside_nps.objects.raw(query)
                promoters = round(len(count)/total_count*100)
                if promoters==0:
                    promoters = round(len(count)/total_count*100,2)

                query = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Passive" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                count = everside_nps.objects.raw(query)
                passive = round(len(count)/total_count*100)
                if passive==0:
                    passive = round(len(count)/total_count*100,2)

                query = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Detractor" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                count = everside_nps.objects.raw(query)
                detractor = round(len(count)/total_count*100)
                if detractor==0:
                    detractor = round(len(count)/total_count*100,2)

            
            else:
                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12'+' AND year='+start_year+');'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1'+' AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                total_count = len(count1)+len(count2)

                query1 = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Promoter" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12'+' AND year='+start_year+');'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Promoter" AND (CAST(month as inT)>=1'+' AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                count = len(count1)+len(count2)
                promoters = round(count/total_count*100)
                if promoters==0:
                    promoters = round(count/total_count*100,2)
               
                query1 = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Passive" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12'+' AND year='+start_year+');'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Passive" AND (CAST(month as inT)>=1'+' AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                count = len(count1)+len(count2)
                passive = round(count/total_count*100)
                if passive==0:
                    passive = round(count/total_count*100,2)

                query1 = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Detractor" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12'+' AND year='+start_year+');'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Detractor" AND (CAST(month as inT)>=1'+' AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                count = len(count1)+len(count2)
                detractor = round(count/total_count*100)
                if detractor==0:
                    detractor = round(count/total_count*100,2)





            nps ={
                "nps_score":(promoters-detractor),
                "promoters":promoters,
                "passive":passive,
                "detractors":detractor,
            }
            
            nps_pie = [{
                        "label":"Promoters",
                        "percentage":promoters,
                        "color":"#00AC69",
                    },
                    {
                        "label":"Passives",
                        "percentage":passive,
                        "color":"#4D5552",
                    },
                    {
                        "label":"Detractors",
                        "percentage":detractor,
                        "color":"#DB2B39",
                    }]

            
            return Response({'nps':nps,
                            'nps_pie':nps_pie})
        except:
            return Response({'Message':'No Data  except'})



@api_view(['GET'])
def netSentimentScore(request,format=None):
    if request.method == 'GET':
        try:
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')

            if start_year == end_year:
                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+str(start_year)+') AND (CAST(month as inT)<='+str(end_month)+' AND year='+str(end_year)+');'
                count = everside_nps.objects.raw(query)
                total_count = len(count)
                query = 'SELECT * FROM apiApp_everside_nps WHERE label="Positive" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                count = everside_nps.objects.raw(query)
                positive = round(len(count)/total_count*100)
                if positive==0:
                    positive = round(len(count)/total_count*100,2)

                query = 'SELECT * FROM apiApp_everside_nps WHERE label="Negative" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                count = everside_nps.objects.raw(query)
                negative = round(len(count)/total_count*100)
                if negative==0:
                    negative = round(len(count)/total_count*100,2)

                query = 'SELECT * FROM apiApp_everside_nps WHERE label="Extreme" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                count = everside_nps.objects.raw(query)
                extreme = round(len(count)/total_count*100)
                if extreme==0:
                    extreme = round(len(count)/total_count*100,2)
            
            else:
                    query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12'+' AND year='+start_year+');'
                    query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1'+' AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                    count1 = everside_nps.objects.raw(query1)
                    count2 = everside_nps.objects.raw(query2)
                    total_count = len(count1)+len(count2)


                    query1 = 'SELECT * FROM apiApp_everside_nps WHERE label="Positive" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12'+' AND year='+start_year+');'
                    query2 = 'SELECT * FROM apiApp_everside_nps WHERE label="Positive" AND (CAST(month as inT)>=1'+' AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                    count1 = everside_nps.objects.raw(query1)
                    count2 = everside_nps.objects.raw(query2)
                    count = len(count1)+len(count2)
                    positive = round(count/total_count*100)
                    if positive==0:
                        positive = round(count/total_count*100,2)
        
                
                    query1 = 'SELECT * FROM apiApp_everside_nps WHERE label="Negative" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12'+' AND year='+start_year+');'
                    query2 = 'SELECT * FROM apiApp_everside_nps WHERE label="Negative" AND (CAST(month as inT)>=1'+' AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                    count1 = everside_nps.objects.raw(query1)
                    count2 = everside_nps.objects.raw(query2)
                    count = len(count1)+len(count2)
                    negative = round(count/total_count*100)
                    if negative==0:
                        negative = round(count/total_count*100,2)
                    

                    query1 = 'SELECT * FROM apiApp_everside_nps WHERE label="Extreme" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12'+' AND year='+start_year+');'
                    query2 = 'SELECT * FROM apiApp_everside_nps WHERE label="Extreme" AND (CAST(month as inT)>=1'+' AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                    count1 = everside_nps.objects.raw(query1)
                    count2 = everside_nps.objects.raw(query2)
                    count = len(count1)+len(count2)
                    extreme = round(count/total_count*100)
                    if extreme==0:
                        extreme = round(count/total_count*100,2)
                        
                    
            nss ={
                    "nss_score":(positive-negative-extreme),
                    "positive":positive,
                    "negative":negative,
                    "extreme":extreme,
                }
                
            nss_pie = [{
                        "label":"Positive",
                        "percentage":positive,
                        "color":"#00AC69",
                    },
                    {
                        "label":"Negative",
                        "percentage":negative,
                        "color":"#f6da09",
                    },
                    {
                        "label":"Extreme",
                        "percentage":extreme,
                        "color":"#DB2B39",
                    }]
            return Response({'nss':nss,
                             'nss_pie':nss_pie})
        
        except:
            return Response({'Message':'No Data  except'})



@api_view(['GET'])
def npsOverTime(request,format=None):
    try:
        if request.method == 'GET':
            months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            nps_over_time = []
            if start_year == end_year:
                for i in range(int(start_month),int(end_month)+1):
                    query = 'SELECT * FROM apiApp_everside_nps WHERE year='+start_year+' And month='+str(i)+';'
                    count = everside_nps.objects.raw(query)
                    total_count = len(count)

                    query = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Promoter" AND year='+start_year+' And month='+str(i)+';'
                    count = everside_nps.objects.raw(query)
                    if(len(count)!=0):
                        promoter = round(len(count)/total_count*100)
                        if promoter == 0:
                            promoter = round(len(count)/total_count*100,2)
                    else:
                        promoter = 0

                    query = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Passive" AND year='+start_year+' And month='+str(i)+';'
                    count = everside_nps.objects.raw(query)
                    if len(count)!=0:
                        passive = round(len(count)/total_count*100)
                        if passive == 0:
                            passive = round(len(count)/total_count*100,2)
                    else:
                        passive=0

                    query = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Detractor" AND year='+start_year+' And month='+str(i)+';'
                    count = everside_nps.objects.raw(query)
                    if len(count)!=0:
                        detractor = round(len(count)/total_count*100)
                        if detractor == 0:
                            detractor = round(len(count)/total_count*100,2)
                    else:
                        detractor=0    
                    
                    over_time_data = {
                        'month': str(months[i-1]),
                        'year': start_year,
                        'nps': int(promoter-detractor),
                        'promoter':promoter,
                        'passive':passive,
                        'detractor':detractor,
                    }
                    nps_over_time.append(over_time_data)

                  
            else:
                for i in range(int(start_month),13):
                    query = 'SELECT * FROM apiApp_everside_nps WHERE year='+start_year+' And month='+str(i)+';'
                    count = everside_nps.objects.raw(query)
                    total_count = len(count)

                    query = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Promoter" AND year='+start_year+' And month='+str(i)+';'
                    count = everside_nps.objects.raw(query)
                    if(len(count)!=0):
                        promoter = round(len(count)/total_count*100)
                        if promoter == 0:
                            promoter = round(len(count)/total_count*100,2)
                    else:
                        promoter = 0
                    
                    query = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Passive" AND year='+start_year+' And month='+str(i)+';'
                    count = everside_nps.objects.raw(query)
                    if(len(count)!=0):
                        passive = round(len(count)/total_count*100)
                        if passive == 0:
                            passive = round(len(count)/total_count*100,2)
                    else:
                        passive = 0

                    query = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Detractor" AND year='+start_year+' And month='+str(i)+';'
                    count = everside_nps.objects.raw(query)
                    if(len(count)!=0):
                        detractor = round(len(count)/total_count*100)
                        if detractor == 0:
                            detractor = round(len(count)/total_count*100,2)
                    else:
                        detractor = 0
                    
                    over_time_data = {
                        'month': str(months[i-1]),
                        'year': start_year,
                        'nps': int(promoter-detractor),
                        'promoter':promoter,
                        'passive':passive,
                        'detractor':detractor,
                    }
                    nps_over_time.append(over_time_data)

                for j in range(1,int(end_month)+1):
                    query = 'SELECT * FROM apiApp_everside_nps WHERE year='+end_year+' And month='+str(j)+';'
                    count = everside_nps.objects.raw(query)
                    total_count = len(count)

                    query = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Promoter" AND year='+end_year+' And month='+str(j)+';'
                    count = everside_nps.objects.raw(query)
                    if(len(count)!=0):
                        promoter = round(len(count)/total_count*100)
                        if promoter == 0:
                            promoter = round(len(count)/total_count*100,2)
                    else:
                        promoter = 0
                    
                    query = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Passive" AND year='+end_year+' And month='+str(j)+';'
                    count = everside_nps.objects.raw(query)
                    if(len(count)!=0):
                        passive = round(len(count)/total_count*100)
                        if passive == 0:
                            passive = round(len(count)/total_count*100,2)
                    else:
                        passive = 0

                    query = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Detractor" AND year='+end_year+' And month='+str(j)+';'
                    count = everside_nps.objects.raw(query)
                    if(len(count)!=0):
                        detractor = round(len(count)/total_count*100)
                        if detractor == 0:
                            detractor = round(len(count)/total_count*100,2)
                    else:
                        detractor = 0
                    
                    over_time_data = {
                        'month': str(months[j-1]),
                        'year': end_year,
                        'nps': int(promoter-detractor),
                        'promoter':promoter,
                        'passive':passive,
                        'detractor':detractor,
                    }
                    nps_over_time.append(over_time_data)
            return Response({'nps_over_time':nps_over_time})
    except:
        return Response({'Message':'No Data  except'})



@api_view(['GET'])
def nssOverTime(request,format=None):
    try:
        if request.method == 'GET':
            months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            nss_over_time = []
            if start_year == end_year:
                for i in range(int(start_month),int(end_month)+1):
                    query = 'SELECT * FROM apiApp_everside_nps WHERE year='+start_year+' And month='+str(i)+';'
                    count = everside_nps.objects.raw(query)
                    total_count = len(count)
                    print(query)
                    print(total_count)
                    query = 'SELECT * FROM apiApp_everside_nps WHERE label="Positive" AND year='+start_year+' And month='+str(i)+';'
                    count = everside_nps.objects.raw(query)
                    if(len(count)!=0):
                        positive = round(len(count)/total_count*100)
                        if positive == 0:
                            positive = round(len(count)/total_count*100,2)
                    else:
                        positive = 0
                    print(query)
                    query = 'SELECT * FROM apiApp_everside_nps WHERE label="Negative" AND year='+start_year+' And month='+str(i)+';'
                    count = everside_nps.objects.raw(query)
                    if len(count)!=0:
                        negative = round(len(count)/total_count*100)
                        if negative == 0:
                            negative = round(len(count)/total_count*100,2)
                    else:
                        negative=0

                    query = 'SELECT * FROM apiApp_everside_nps WHERE label="Extreme" AND year='+start_year+' And month='+str(i)+';'
                    count = everside_nps.objects.raw(query)
                    if len(count)!=0:
                        extreme = round(len(count)/total_count*100)
                        if extreme == 0:
                            extreme = round(len(count)/total_count*100,2)
                    else:
                        extreme=0    

                    query = 'SELECT * FROM apiApp_everside_nps WHERE label="Neutral" AND year='+start_year+' And month='+str(i)+';'
                    count = everside_nps.objects.raw(query)
                    if len(count)!=0:
                        neutral = round(len(count)/total_count*100)
                        if neutral == 0:
                            neutral = round(len(count)/total_count*100,2)
                    else:
                        neutral=0
                    
                    over_time_data = {
                        'month': str(months[i-1]),
                        'year': start_year,
                        'nss': int(positive-negative-extreme),
                        'positive':positive,
                        'negative':negative,
                        'extreme':extreme,
                        'neutral':neutral,
                    }
                    nss_over_time.append(over_time_data)       
            else:
                    for i in range(int(start_month),13):
                        query = 'SELECT * FROM apiApp_everside_nps WHERE year='+start_year+' And month='+str(i)+';'
                        count = everside_nps.objects.raw(query)
                        total_count = len(count)

                        query = 'SELECT * FROM apiApp_everside_nps WHERE label="Positive" AND year='+start_year+' And month='+str(i)+';'
                        count = everside_nps.objects.raw(query)
                        if(len(count)!=0):
                            positive = round(len(count)/total_count*100)
                            if positive == 0:
                                positive = round(len(count)/total_count*100,2)
                        else:
                            positive = 0
                        
                        query = 'SELECT * FROM apiApp_everside_nps WHERE label="Negative" AND year='+start_year+' And month='+str(i)+';'
                        count = everside_nps.objects.raw(query)
                        if(len(count)!=0):
                            negative = round(len(count)/total_count*100)
                            if negative == 0:
                                negative = round(len(count)/total_count*100,2)
                        else:
                            negative = 0

                        query = 'SELECT * FROM apiApp_everside_nps WHERE label="Extreme" AND year='+start_year+' And month='+str(i)+';'
                        count = everside_nps.objects.raw(query)
                        if(len(count)!=0):
                            extreme = round(len(count)/total_count*100)
                            if extreme == 0:
                                extreme = round(len(count)/total_count*100,2)
                        else:
                            extreme = 0
                        

                        query = 'SELECT * FROM apiApp_everside_nps WHERE label="Neutral" AND year='+start_year+' And month='+str(i)+';'
                        count = everside_nps.objects.raw(query)
                        if(len(count)!=0):
                            neutral = round(len(count)/total_count*100)
                            if neutral == 0:
                                neutral = round(len(count)/total_count*100,2)
                        else:
                            neutral = 0


                        over_time_data = {
                            'month': str(months[i-1]),
                            'year': start_year,
                            'nss': int(positive-negative-extreme),
                            'positive':positive,
                            'negative':negative,
                            'extreme':extreme,
                            'neutral':neutral,
                        }
                        nss_over_time.append(over_time_data)

                    for j in range(1,int(end_month)+1):
                        query = 'SELECT * FROM apiApp_everside_nps WHERE year='+end_year+' And month='+str(j)+';'
                        count = everside_nps.objects.raw(query)
                        total_count = len(count)

                        query = 'SELECT * FROM apiApp_everside_nps WHERE label="Positive" AND year='+end_year+' And month='+str(j)+';'
                        count = everside_nps.objects.raw(query)
                        if(len(count)!=0):
                            positive = round(len(count)/total_count*100)
                            if positive == 0:
                                positive = round(len(count)/total_count*100,2)
                        else:
                            positive = 0
                        
                        query = 'SELECT * FROM apiApp_everside_nps WHERE label="Negative" AND year='+end_year+' And month='+str(j)+';'
                        count = everside_nps.objects.raw(query)
                        if(len(count)!=0):
                            negative = round(len(count)/total_count*100)
                            if negative == 0:
                                negative = round(len(count)/total_count*100,2)
                        else:
                            negative = 0

                        query = 'SELECT * FROM apiApp_everside_nps WHERE label="Extreme" AND year='+end_year+' And month='+str(j)+';'
                        count = everside_nps.objects.raw(query)
                        if(len(count)!=0):
                            extreme = round(len(count)/total_count*100)
                            if extreme == 0:
                                extreme = round(len(count)/total_count*100,2)
                        else:
                            extreme = 0

                        query = 'SELECT * FROM apiApp_everside_nps WHERE label="Neutral" AND year='+end_year+' And month='+str(j)+';'
                        count = everside_nps.objects.raw(query)
                        if(len(count)!=0):
                            neutral = round(len(count)/total_count*100)
                            if neutral == 0:
                                neutral = round(len(count)/total_count*100,2)
                        else:
                            neutral = 0
                        
                        over_time_data = {
                            'month': str(months[j-1]),
                            'year': end_year,
                            'nss': int(positive-negative-extreme),
                            'positive':positive,
                            'negative':negative,
                            'extreme':extreme,
                            'neutral':neutral,
                        }
                        nss_over_time.append(over_time_data)
            return Response({'nss_over_time':nss_over_time})
    except:
        return Response({'Message':'No Data  except'})


@api_view(['GET'])
def npsVsSentiments(request,format=None):
    try:
        if request.method == 'GET':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            
            if start_year == end_year:
                #-------------Extreme---------------------------------
                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Extreme";'
                count = everside_nps.objects.raw(query)
                total_count = len(count)

                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Extreme" AND nps_label="Promoter";'
                count = everside_nps.objects.raw(query)
                if len(count)!=0:
                    promoter = round(len(count)/total_count*100)
                    if promoter == 0:
                        promoter = round(len(count)/total_count*100,2)
                else:
                    promoter = 0


                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Extreme" AND nps_label="Passive";'
                count = everside_nps.objects.raw(query)
                if len(count)!=0:
                    passive = round(len(count)/total_count*100)
                    if passive == 0:
                        passive = round(len(count)/total_count*100,2)
                else:
                    passive = 0

                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Extreme" AND nps_label="Detractor";'
                count = everside_nps.objects.raw(query)
                if len(count)!=0:
                    detractor = round(len(count)/total_count*100)
                    if detractor == 0:
                        detractor = round(len(count)/total_count*100,2)
                else:
                    detractor = 0
                
                extreme = {
                    'sentiment_label':'Extreme',
                    'promoter':promoter,
                    'passive':passive,
                    'detractor':detractor
                }
            #------------Positive-----------------------------
                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Positive";'
                count = everside_nps.objects.raw(query)
                total_count = len(count)

                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Positive" AND nps_label="Promoter";'
                count = everside_nps.objects.raw(query)
                if len(count)!=0:
                    promoter = round(len(count)/total_count*100)
                    if promoter == 0:
                        promoter = round(len(count)/total_count*100,2)
                else:
                    promoter = 0


                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Positive" AND nps_label="Passive";'
                count = everside_nps.objects.raw(query)
                if len(count)!=0:
                    passive = round(len(count)/total_count*100)
                    if passive == 0:
                        passive = round(len(count)/total_count*100,2)
                else:
                    passive = 0

                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Positive" AND nps_label="Detractor";'
                count = everside_nps.objects.raw(query)
                if len(count)!=0:
                    detractor = round(len(count)/total_count*100)
                    if detractor == 0:
                        detractor = round(len(count)/total_count*100,2)
                else:
                    detractor = 0
            
                positive = {
                    'sentiment_label':'Positive',
                    'promoter':promoter,
                    'passive':passive,
                    'detractor':detractor
                }

            #--------------Negative-----------------
                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Negative";'
                count = everside_nps.objects.raw(query)
                total_count = len(count)

                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Negative" AND nps_label="Promoter";'
                count = everside_nps.objects.raw(query)
                if len(count)!=0:
                    promoter = round(len(count)/total_count*100)
                    if promoter == 0:
                        promoter = round(len(count)/total_count*100,2)
                else:
                    promoter = 0


                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Negative" AND nps_label="Passive";'
                count = everside_nps.objects.raw(query)
                if len(count)!=0:
                    passive = round(len(count)/total_count*100)
                    if passive == 0:
                        passive = round(len(count)/total_count*100,2)
                else:
                    passive = 0

                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Negative" AND nps_label="Detractor";'
                count = everside_nps.objects.raw(query)
                if len(count)!=0:
                    detractor = round(len(count)/total_count*100)
                    if detractor == 0:
                        detractor = round(len(count)/total_count*100,2)
                else:
                    detractor = 0

                negative = {
                    'sentiment_label':'Negative',
                    'promoter':promoter,
                    'passive':passive,
                    'detractor':detractor
                }

            #------------------Neutral----------------------------------------
                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Neutral";'
                count = everside_nps.objects.raw(query)
                total_count = len(count)

                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Neutral" AND nps_label="Promoter";'
                count = everside_nps.objects.raw(query)
                if len(count)!=0:
                    promoter = round(len(count)/total_count*100)
                    if promoter == 0:
                        promoter = round(len(count)/total_count*100,2)
                else:
                    promoter = 0


                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Neutral" AND nps_label="Passive";'
                count = everside_nps.objects.raw(query)
                if len(count)!=0:
                    passive = round(len(count)/total_count*100)
                    if passive == 0:
                        passive = round(len(count)/total_count*100,2)
                else:
                    passive = 0

                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Neutral" AND nps_label="Detractor";'
                count = everside_nps.objects.raw(query)
                if len(count)!=0:
                    detractor = round(len(count)/total_count*100)
                    if detractor == 0:
                        detractor = round(len(count)/total_count*100,2)
                else:
                    detractor = 0  

                neutral = {
                    'sentiment_label':'neutral',
                    'promoter':promoter,
                    'passive':passive,
                    'detractor':detractor
                }  

            else:
                #--------------Extreme---------------------------------------
                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Extreme";'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Extreme";'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                total_count = len(count1)+len(count2)

                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Extreme" AND nps_label="Promoter";'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Extreme" AND nps_label="Promoter";'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                count = len(count1)+len(count2)
                if count!=0:
                    promoter = round(count/total_count*100)
                    if promoter == 0:
                        promoter = round(count/total_count*100,2)
                else:
                    promoter = 0

                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Extreme" AND nps_label="Passive";'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Extreme" AND nps_label="Passive";'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                count = len(count1)+len(count2)
                if count!=0:
                    passive = round(count/total_count*100)
                    if passive == 0:
                        passive = round(count/total_count*100,2)
                else:
                    passive = 0
                
                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Extreme" AND nps_label="Detractor";'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Extreme" AND nps_label="Detractor";'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                count = len(count1)+len(count2)
                if count!=0:
                    detractor = round(count/total_count*100)
                    if detractor == 0:
                        detractor = round(count/total_count*100,2)
                else:
                    detractor = 0

                extreme = {
                    'sentiment_label':'Extreme',
                    'promoter':promoter,
                    'passive':passive,
                    'detractor':detractor
                }

                #----------Positive-------------------------------
                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Positive";'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Positive";'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                total_count = len(count1)+len(count2)

                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Positive" AND nps_label="Promoter";'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Positive" AND nps_label="Promoter";'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                count = len(count1)+len(count2)
                if count!=0:
                    promoter = round(count/total_count*100)
                    if promoter == 0:
                        promoter = round(count/total_count*100,2)
                else:
                    promoter = 0

                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Positive" AND nps_label="Passive";'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Positive" AND nps_label="Passive";'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                count = len(count1)+len(count2)
                if count!=0:
                    passive = round(count/total_count*100)
                    if passive == 0:
                        passive = round(count/total_count*100,2)
                else:
                    passive = 0
                
                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Positive" AND nps_label="Detractor";'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Positive" AND nps_label="Detractor";'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                count = len(count1)+len(count2)
                if count!=0:
                    detractor = round(count/total_count*100)
                    if detractor == 0:
                        detractor = round(count/total_count*100,2)
                else:
                    detractor = 0

                positive = {
                    'sentiment_label':'Positive',
                    'promoter':promoter,
                    'passive':passive,
                    'detractor':detractor
                }

                #----------------Negative--------------------------------
                
                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Negative";'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Negative";'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                total_count = len(count1)+len(count2)

                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Negative" AND nps_label="Promoter";'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Negative" AND nps_label="Promoter";'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                count = len(count1)+len(count2)
                if count!=0:
                    promoter = round(count/total_count*100)
                    if promoter == 0:
                        promoter = round(count/total_count*100,2)
                else:
                    promoter = 0

                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Negative" AND nps_label="Passive";'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Negative" AND nps_label="Passive";'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                count = len(count1)+len(count2)
                if count!=0:
                    passive = round(count/total_count*100)
                    if passive == 0:
                        passive = round(count/total_count*100,2)
                else:
                    passive = 0
                
                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Negative" AND nps_label="Detractor";'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Negative" AND nps_label="Detractor";'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                count = len(count1)+len(count2)
                if count!=0:
                    detractor = round(count/total_count*100)
                    if detractor == 0:
                        detractor = round(count/total_count*100,2)
                else:
                    detractor = 0

                negative = {
                    'sentiment_label':'Negative',
                    'promoter':promoter,
                    'passive':passive,
                    'detractor':detractor
                }

                #-------------Neutral-------------------------
                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Neutral";'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Neutral";'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                total_count = len(count1)+len(count2)

                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Neutral" AND nps_label="Promoter";'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Neutral" AND nps_label="Promoter";'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                count = len(count1)+len(count2)
                if count!=0:
                    promoter = round(count/total_count*100)
                    if promoter == 0:
                        promoter = round(count/total_count*100,2)
                else:
                    promoter = 0

                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Neutral" AND nps_label="Passive";'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Neutral" AND nps_label="Passive";'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                count = len(count1)+len(count2)
                if count!=0:
                    passive = round(count/total_count*100)
                    if passive == 0:
                        passive = round(count/total_count*100,2)
                else:
                    passive = 0
                
                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Neutral" AND nps_label="Detractor";'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Neutral" AND nps_label="Detractor";'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                count = len(count1)+len(count2)
                if count!=0:
                    detractor = round(count/total_count*100)
                    if detractor == 0:
                        detractor = round(count/total_count*100,2)
                else:
                    detractor = 0

                neutral = {
                    'sentiment_label':'Neutral',
                    'promoter':promoter,
                    'passive':passive,
                    'detractor':detractor
                }


            final_data = [extreme,negative,neutral,positive]
            '''return Response({'extreme':extreme,
                             'positive':positive,
                             'negative':negative,
                             'neutral':neutral})'''
            return Response(final_data)
            
    except:
        return Response({'Message':'No Data except'})


@api_view(['GET'])
def alertComments(request,format=None):
    try:
        if request.method == 'GET':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')

            if start_year == end_year:
                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Extreme" ORDER BY (CASE WHEN CAST(day AS INT)<10 THEN (CAST(month||0||day AS INT))ELSE (CAST(month||day AS INT)) END) DESC'
                query_exec = everside_nps.objects.raw(query)
                serialized_data = eversideAlertComments(query_exec,many=True)
                
            else:
                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Extreme" ORDER BY (CASE WHEN CAST(day AS INT)<10 THEN (CAST(month||0||day AS INT))ELSE (CAST(month||day AS INT)) END) DESC;'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Extreme" ORDER BY (CASE WHEN CAST(day AS INT)<10 THEN (CAST(month||0||day AS INT))ELSE (CAST(month||day AS INT)) END) DESC;'
                query_exec1 = everside_nps.objects.raw(query1)
                query_exec2 = everside_nps.objects.raw(query2)

                query_exec = list(query_exec2)+list(query_exec1)
                serialized_data = eversideAlertComments(query_exec,many=True)

        final_data = []
        for i in range(len(serialized_data.data)):
            dict_id = {'id':i+1}
            final_dict = dict_id|dict((serialized_data.data)[i])
            final_data.append(final_dict)
        return Response(final_data)
    except:
        return Response({'Message':'No Data except'})


@api_view(['GET'])
def topComments(request,format=None):
    try:
        if request.method == 'GET':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')

            if start_year == end_year:
                query = 'SELECT * from apiApp_everside_nps where (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Positive" ORDER BY RANDOM() LIMIT 4'
                positive = everside_nps.objects.raw(query)
                
                query = 'SELECT * from apiApp_everside_nps where (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Negative" ORDER BY RANDOM() LIMIT 4'
                negative = everside_nps.objects.raw(query)
                
                query = 'SELECT * from apiApp_everside_nps where (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Extreme" ORDER BY RANDOM() LIMIT 4'
                extreme = everside_nps.objects.raw(query)
                
                query = 'SELECT * from apiApp_everside_nps where (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Neutral" ORDER BY RANDOM() LIMIT 4'
                neutral = everside_nps.objects.raw(query)

                query_exec = list(positive)+list(negative)+list(extreme)+list(neutral)
                random.shuffle(query_exec)
                serialized_data = eversideTopComments(query_exec,many=True)

            
            else:
                query1 = 'SELECT * from apiApp_everside_nps where (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Positive" ORDER BY RANDOM() LIMIT 2'    
                query2 = 'SELECT * from apiApp_everside_nps where (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Positive" ORDER BY RANDOM() LIMIT 2'
                query_exec1 = everside_nps.objects.raw(query1)
                query_exec2 = everside_nps.objects.raw(query2)
                positive = list(query_exec1)+list(query_exec2)

                query1 = 'SELECT * from apiApp_everside_nps where (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Negative" ORDER BY RANDOM() LIMIT 2'    
                query2 = 'SELECT * from apiApp_everside_nps where (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Negative" ORDER BY RANDOM() LIMIT 2'
                query_exec1 = everside_nps.objects.raw(query1)
                query_exec2 = everside_nps.objects.raw(query2)
                negative = list(query_exec1)+list(query_exec2)

                query1 = 'SELECT * from apiApp_everside_nps where (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Extreme" ORDER BY RANDOM() LIMIT 2'    
                query2 = 'SELECT * from apiApp_everside_nps where (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Extreme" ORDER BY RANDOM() LIMIT 2'
                query_exec1 = everside_nps.objects.raw(query1)
                query_exec2 = everside_nps.objects.raw(query2)
                extreme = list(query_exec1)+list(query_exec2)

                query1 = 'SELECT * from apiApp_everside_nps where (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Neutral" ORDER BY RANDOM() LIMIT 2'    
                query2 = 'SELECT * from apiApp_everside_nps where (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Neutral" ORDER BY RANDOM() LIMIT 2'
                query_exec1 = everside_nps.objects.raw(query1)
                query_exec2 = everside_nps.objects.raw(query2)
                neutral = list(query_exec1)+list(query_exec2)
                
                query_exec = positive + negative + extreme + neutral
                random.shuffle(query_exec)
                serialized_data = eversideTopComments(query_exec,many=True)
        final_data = []
        for i in range(len(serialized_data.data)):
            dict_id = {'id':i+1}
            final_dict = dict_id|dict((serialized_data.data)[i])
            final_data.append(final_dict)
        return Response(final_data)
        
    except:
        return Response({'Message':'No Data except'})

@api_view(['GET'])
def clinics_data(request,format=None):
    try:
        if request.method == 'GET':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            clinic_list = []
            u_clinic_list = []
            nps_list = []
            city_list = []
            state_list = []
            final_data = []
            if start_year == end_year:
                query = 'SELECT * from apiApp_everside_nps where (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+')'
                query_exec = everside_nps.objects.raw(query)
                for i in list(query_exec):
                    clinic_name = getattr(i, 'clinic')
                    clinic_list.append(clinic_name)
                clinic_list = list(set(clinic_list))
                
                for i in clinic_list:
                    query = 'SELECT * from apiApp_everside_nps where (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND clinic="'+i+'"'
                    query_exec = everside_nps.objects.raw(query)
                    nps = 0
                    for j in list(query_exec):
                        clinic_nps = getattr(j, 'nps_score')
                        nps = nps + float(clinic_nps)
                    nps = round(nps/len(query_exec),2)
                    query = 'Select * From apiApp_everside_nps_clinics where clinic="'+i+'"'
                    query_exec = everside_nps_clinics.objects.raw(query)
                    if (len(list(query_exec))) != 0 :
                        city = getattr(list(query_exec)[0], 'city')
                        state = getattr(list(query_exec)[0], 'state')
                        
                        u_clinic_list.append(i)
                        nps_list.append(nps)
                        city_list.append(city)
                        state_list.append(state)
                
                
                df = pd.DataFrame({'clinic':u_clinic_list,
                                   'city':city_list,
                                   'state':state_list,
                                   'nps':nps_list})
                df = df.sort_values(by=['nps'], ascending=False)
                
                for i in range((df.shape)[0]):
                    data = {
                        'clinic':list(df['clinic'])[i],
                        'city':list(df['city'])[i],
                        'state':list(df['state'])[i],
                        'nps':list(df['nps'])[i], 
                    }
                    final_data.append(data)

            else:
                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+');'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                query_exec1 = everside_nps.objects.raw(query1)
                query_exec2 = everside_nps.objects.raw(query2) 

                for i in list(query_exec1):
                    clinic_name = getattr(i, 'clinic')
                    clinic_list.append(clinic_name)
                for i in list(query_exec2):
                    clinic_name = getattr(i, 'clinic')
                    clinic_list.append(clinic_name)
                clinic_list = list(set(clinic_list))

                for i in clinic_list:
                    query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND clinic="'+i+'"'
                    query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND clinic="'+i+'"'
                    query_exec1 = everside_nps.objects.raw(query1)
                    query_exec2 = everside_nps.objects.raw(query2)
                    nps = 0
                    for j in list(query_exec1):
                        clinic_nps = getattr(j, 'nps_score')
                        nps = nps + float(clinic_nps)
                    for j in list(query_exec2):
                        clinic_nps = getattr(j, 'nps_score')
                        nps = nps + float(clinic_nps)
                    nps = round(nps/(len(query_exec1)+len(query_exec2)),2)
                    query = 'Select * From apiApp_everside_nps_clinics where clinic="'+i+'"'
                    query_exec = everside_nps_clinics.objects.raw(query)
                    if (len(list(query_exec))) != 0 :
                        city = getattr(list(query_exec)[0], 'city')
                        state = getattr(list(query_exec)[0], 'state')
                        
                        u_clinic_list.append(i)
                        nps_list.append(nps)
                        city_list.append(city)
                        state_list.append(state)

                df = pd.DataFrame({'clinic':u_clinic_list,
                                   'city':city_list,
                                   'state':state_list,
                                   'nps':nps_list})
                df = df.sort_values(by=['nps'], ascending=False)
                for i in range((df.shape)[0]):
                    data = {
                        'clinic':list(df['clinic'])[i],
                        'city':list(df['city'])[i],
                        'state':list(df['state'])[i],
                        'nps':list(df['nps'])[i], 
                    }
                    final_data.append(data)

            return Response({'data':final_data})     
        
    except:
        return Response({'Message':'No Data except'})


@api_view(['GET'])
def totalCards(request,format=None):
    try:
        if request.method == 'GET':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            
            if start_year == end_year:
               query = 'SELECT * from apiApp_everside_nps where (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+')'
               query_exec = everside_nps.objects.raw(query)
               survey_list = []
               clinic_list = []
               for i in list(query_exec):
                    survey = getattr(i,'review_ID')
                    clinic = getattr(i,'clinic')
                    survey_list.append(survey)
                    clinic_list.append(clinic)
               query = 'SELECT * from apiApp_everside_nps where (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Extreme"'
               alerts = everside_nps.objects.raw(query)
               card_data = {
                            'survey':len(list(set(survey_list))),
                            'comments': len(query_exec),
                            'alerts': len(alerts),
                            'clinic': len(list(set(clinic_list))),
                            'doctors':5125,
                            'clients':956
                    }
            else:
                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+')'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+')'
                query_exec1 = everside_nps.objects.raw(query1)
                query_exec2 = everside_nps.objects.raw(query2)
                survey_list = []
                clinic_list = []
                for i in list(query_exec1):
                    survey = getattr(i,'review_ID')
                    clinic = getattr(i,'clinic')
                    survey_list.append(survey)
                    clinic_list.append(clinic)
                for i in list(query_exec2):
                    survey = getattr(i,'review_ID')
                    clinic = getattr(i,'clinic')
                    survey_list.append(survey)
                    clinic_list.append(clinic)
                query1 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+') AND label="Extreme"'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+') AND label="Extreme"'
                alert1 = everside_nps.objects.raw(query1)
                alert2 = everside_nps.objects.raw(query2)
                card_data = {
                            'survey':len(list(set(survey_list))),
                            'comments': len(query_exec1)+len(query_exec2),
                            'alerts': len(alert1)+len(alert2),
                            'clinic': len(list(set(clinic_list))),
                            'doctors':5125,
                            'clients':956
                    }
            return Response({'card_data':card_data})
            
    except:
        return Response({'Message':'No Data except'})


@api_view(['GET'])
def wordFrequency(request,format=None):
    try:
        if request.method == 'GET':
            query = 'SELECT * FROM apiApp_everside_nps_word_frequency ORDER BY CAST(frequency AS INT) DESC LIMIT 8'
            query_exec = everside_nps_word_frequency.objects.raw(query)
            data_serializer = eversideWordFrequencySerializer(query_exec,many=True)
            return Response({'word_frequency':data_serializer.data})
    except:
        Response({'Message':'No Data except'})
