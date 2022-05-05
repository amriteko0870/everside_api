from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import json
import random
import itertools
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser,FormParser


#-------------import api serializers --------------------
from apiApp.serializers import eversideNpsDataSerializer,eversideAlertComments,eversideTopComments,eversideWordFrequencySerializer,eversideTotalComments
#--------------------------------------------------------

#---------------import models-----------------------------
from apiApp.models import everside_nps,everside_nps_clinics,everside_nps_word_frequency
#--------------------------------------------------------

#-------REST MODULES---------------------------
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http.response import JsonResponse
from django.db.models import Avg, Max, Min, Sum
#-------------------------------------------------

# Create your views here.

#-------------------------PROBABILITY FUNCTION-------------------------------------
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
import math 

    
def func(df):
    

    #df_engagement_client_data = pd.read_csv(file_name)
    df_engagement_client_data = df

    
    df_us_census_data = pd.read_csv('us_census_data.csv')

    df_engagement_model_data = df_engagement_client_data.merge(df_us_census_data, on = 'ZIP', how = 'left')


    df_engagement_model_data = df_engagement_model_data.rename(columns = {'__Black_or_African_American_alone':'per_black',
                                                                        '__Asian':'per_asian',
                                                                        '__With_a_disability':'per_with_disability',
                                                                        '__Worked_full-time,_year_round':'per_worked_ft',
                                                                        '__Worked_less_than_full-time,_year_round':'per_worked_lt_ft',
                                                                        '__household_population!!Below_$25,000':'hinc_below_25k',
                                                                        '__household_population!!$25,000_to_$49,999':'hinc_25k_to_50k',
                                                                        '__household_population!!$50,000_to_$74,999':'hinc_50k_to_75k',
                                                                        'Estimate__Percent_Insured_19_to':'per_ins_19_64',
                                                                        'Percent_Insured_AGE_55_to_64_yea':'per_ins_age_55_to_64',
                                                                        'Percent_Insured_Worked_full_time':'per_ins_worked_ft',
                                                                        'Insured__19_to_64_years!!Worked_less_than_full-time':'per_ins_19_64_worked_lt_ft',
                                                                        'Percent_Uninsured_19_to_25_years':'per_unins_19_25',
                                                                        'Percent_Uninsured_AGE_26_to_34_y':'per_unins_26_34',
                                                                        'Percent_Uninsured_AGE__45_to_54':'per_unins_45_54',
                                                                        'Percent_UninsuredAGE__55_to_64_y':'per_unins_55_64',
                                                                        'Percent_UninsuredAGE__19_to_64_y':'per_unins_19_64',
                                                                        'Percent_Uninsured_19_to_64_years':'per_unins_19_64_worked_lt_ft',
                                                                        '__Not_in_labor_force':'per_not_in_labor_force'})


    #Data Preparation

    df_engagement_model_data['per_not_in_labor_force'] = np.where(df_engagement_model_data.per_not_in_labor_force >=50,50,
                                                                np.where((df_engagement_model_data.per_not_in_labor_force >=30) & (df_engagement_model_data.per_not_in_labor_force <=50),30,df_engagement_model_data.per_not_in_labor_force))

    df_engagement_model_data['per_with_disability'] = np.where(df_engagement_model_data.per_with_disability >=30,30
                                                            ,df_engagement_model_data.per_with_disability)

    df_engagement_model_data['hinc_25k_to_50k'] = np.where(df_engagement_model_data.hinc_25k_to_50k >=40,40
                                                            ,df_engagement_model_data.hinc_25k_to_50k)

    df_engagement_model_data['hinc_50k_to_75k'] = np.where(df_engagement_model_data.hinc_50k_to_75k >=40,40
                                                            ,df_engagement_model_data.hinc_50k_to_75k)

    df_engagement_model_data['hinc_below_25k'] = np.where(df_engagement_model_data.hinc_below_25k >=40,40
                                                            ,df_engagement_model_data.hinc_below_25k)


    #State preparation

    df_engagement_model_data['d1_STATE'] = df_engagement_model_data[df_engagement_model_data.STATE == 'IN'].STATE
    df_engagement_model_data['d1_STATE'] = np.where(df_engagement_model_data['d1_STATE'].isna(),0,1)

    df_engagement_model_data['d2_STATE'] = df_engagement_model_data[df_engagement_model_data.STATE.isin(['CO','OH'])].STATE
    df_engagement_model_data['d2_STATE'] = np.where(df_engagement_model_data['d2_STATE'].isna(),0,1)

    df_engagement_model_data['d3_STATE'] = df_engagement_model_data[df_engagement_model_data.STATE == 'MO'].STATE
    df_engagement_model_data['d3_STATE'] = np.where(df_engagement_model_data['d3_STATE'].isna(),0,1)

    df_engagement_model_data['d4_STATE'] = df_engagement_model_data[df_engagement_model_data.STATE == 'NV'].STATE
    df_engagement_model_data['d4_STATE'] = np.where(df_engagement_model_data['d4_STATE'].isna(),0,1)

    #Region Preparation

    df_engagement_model_data['d2_REGION'] = df_engagement_model_data[df_engagement_model_data.REGION == 'Northeast'].REGION
    df_engagement_model_data['d2_REGION'] = np.where(df_engagement_model_data['d2_REGION'].isna(),0,1)

    df_engagement_model_data['d3_REGION'] = df_engagement_model_data[df_engagement_model_data.REGION == 'South'].REGION
    df_engagement_model_data['d3_REGION'] = np.where(df_engagement_model_data['d3_REGION'].isna(),0,1)

    #Age Data Preparation

    df_engagement_model_data['d1_AGE_O'] = df_engagement_model_data[df_engagement_model_data.AGE_ON_DEC20 <= 28].AGE_ON_DEC20
    df_engagement_model_data['d1_AGE_O'] = np.where(df_engagement_model_data['d1_AGE_O'].isna(),0,1)

    df_engagement_model_data['d2_AGE_O'] = df_engagement_model_data[(df_engagement_model_data.AGE_ON_DEC20 > 28) & (df_engagement_model_data.AGE_ON_DEC20 <= 47)].AGE_ON_DEC20
    df_engagement_model_data['d2_AGE_O'] = np.where(df_engagement_model_data['d2_AGE_O'].isna(),0,1)

    df_engagement_model_data['d3_AGE_O'] = df_engagement_model_data[(df_engagement_model_data.AGE_ON_DEC20 > 47) & (df_engagement_model_data.AGE_ON_DEC20 <= 59)].AGE_ON_DEC20
    df_engagement_model_data['d3_AGE_O'] = np.where(df_engagement_model_data['d3_AGE_O'].isna(),0,1)

    #Black and Asian Data Preparation

    df_engagement_model_data['d2_PER_BLACK'] = df_engagement_model_data[(df_engagement_model_data.per_black > 0.47) & (df_engagement_model_data.per_black <= 1.4)].per_black
    df_engagement_model_data['d2_PER_BLACK'] = np.where(df_engagement_model_data['d2_PER_BLACK'].isna(),0,1)

    df_engagement_model_data['d3_PER_ASIAN'] = df_engagement_model_data[(df_engagement_model_data.per_asian > 1.12) & (df_engagement_model_data.per_asian <= 3.03)].per_asian
    df_engagement_model_data['d3_PER_ASIAN'] = np.where(df_engagement_model_data['d3_PER_ASIAN'].isna(),0,1)


    #Estimated Population

    df_engagement_model_data['d3_Estimate'] = df_engagement_model_data[(df_engagement_model_data.Estimate__population > 16396) & (df_engagement_model_data.Estimate__population <= 30646)].Estimate__population
    df_engagement_model_data['d3_Estimate'] = np.where(df_engagement_model_data['d3_Estimate'].isna(),0,1)

    df_engagement_model_data['d1_PER_NOT_IN_LABOUR_FORCE'] = df_engagement_model_data[(df_engagement_model_data.per_not_in_labor_force <= 17.22)].per_not_in_labor_force
    df_engagement_model_data['d1_PER_NOT_IN_LABOUR_FORCE'] = np.where(df_engagement_model_data['d1_PER_NOT_IN_LABOUR_FORCE'].isna(),0,1)


    df_engagement_model_data['d1_PER_INS_19_64_WORKED_LT_FT'] = df_engagement_model_data[(df_engagement_model_data.per_ins_19_64_worked_lt_ft <= 80.5)].per_ins_19_64_worked_lt_ft
    df_engagement_model_data['d1_PER_INS_19_64_WORKED_LT_FT'] = np.where(df_engagement_model_data['d1_PER_INS_19_64_WORKED_LT_FT'].isna(),0,1)

    df_engagement_model_data['d1_PER_WORKED_FT'] = df_engagement_model_data[(df_engagement_model_data.per_worked_ft <= 58.96)].per_worked_ft
    df_engagement_model_data['d1_PER_WORKED_FT'] = np.where(df_engagement_model_data['d1_PER_WORKED_FT'].isna(),0,1)

    df_engagement_model_data['d1_PER_WITH_DISABILITY'] = df_engagement_model_data[(df_engagement_model_data.per_with_disability <= 9.28)].per_with_disability
    df_engagement_model_data['d1_PER_WITH_DISABILITY'] = np.where(df_engagement_model_data['d1_PER_WITH_DISABILITY'].isna(),0,1)

    #Household Inome data Preparation

    df_engagement_model_data['d1_HHINC_25K_TO_50K'] = df_engagement_model_data[(df_engagement_model_data.hinc_25k_to_50k <= 9.86)].hinc_25k_to_50k
    df_engagement_model_data['d1_HHINC_25K_TO_50K'] = np.where(df_engagement_model_data['d1_HHINC_25K_TO_50K'].isna(),0,1)

    df_engagement_model_data['d2_HHINC_25K_TO_50K'] = df_engagement_model_data[(df_engagement_model_data.hinc_25k_to_50k > 9.86) & (df_engagement_model_data.hinc_25k_to_50k <= 17.16)].hinc_25k_to_50k
    df_engagement_model_data['d2_HHINC_25K_TO_50K'] = np.where(df_engagement_model_data['d2_HHINC_25K_TO_50K'].isna(),0,1)

    df_engagement_model_data['d3_HHINC_25K_TO_50K'] = df_engagement_model_data[(df_engagement_model_data.hinc_25k_to_50k > 17.16) & (df_engagement_model_data.hinc_25k_to_50k <= 22.96)].hinc_25k_to_50k
    df_engagement_model_data['d3_HHINC_25K_TO_50K'] = np.where(df_engagement_model_data['d3_HHINC_25K_TO_50K'].isna(),0,1)

    df_engagement_model_data['d2_HHINC_50_TO_75K'] = df_engagement_model_data[(df_engagement_model_data.hinc_50k_to_75k > 12.32) & (df_engagement_model_data.hinc_50k_to_75k <= 17.74)].hinc_50k_to_75k
    df_engagement_model_data['d2_HHINC_50_TO_75K'] = np.where(df_engagement_model_data['d2_HHINC_50_TO_75K'].isna(),0,1)

    df_engagement_model_data['d3_HHINC_50_TO_75K'] = df_engagement_model_data[(df_engagement_model_data.hinc_50k_to_75k > 17.74) & (df_engagement_model_data.hinc_50k_to_75k <= 24.25)].hinc_50k_to_75k
    df_engagement_model_data['d3_HHINC_50_TO_75K'] = np.where(df_engagement_model_data['d3_HHINC_50_TO_75K'].isna(),0,1)

    df_engagement_model_data['d1_HHINC_BELOW_25K'] = df_engagement_model_data[(df_engagement_model_data.hinc_below_25k <= 4.91)].hinc_below_25k
    df_engagement_model_data['d1_HHINC_BELOW_25K'] = np.where(df_engagement_model_data['d1_HHINC_BELOW_25K'].isna(),0,1)

    df_engagement_model_data['d2_HHINC_BELOW_25K'] = df_engagement_model_data[(df_engagement_model_data.hinc_below_25k > 4.91) & (df_engagement_model_data.hinc_below_25k <= 11.48)].hinc_below_25k
    df_engagement_model_data['d2_HHINC_BELOW_25K'] = np.where(df_engagement_model_data['d2_HHINC_BELOW_25K'].isna(),0,1)


    Contract_Type = 'FF & Near Site'

    if Contract_Type == 'FF & Near Site':
        df_engagement_model_data['d1_Contract_Type'] = 1
        df_engagement_model_data['d2_Contract_Type'] = 0
        df_engagement_model_data['d4_Contract_Type'] = 0
        df_engagement_model_data['score'] = -0.6923-0.1696*df_engagement_model_data['d1_STATE']-0.72*df_engagement_model_data['d2_STATE']-3.1469*df_engagement_model_data['d3_STATE']+1.7295*df_engagement_model_data['d4_STATE']-0.72*df_engagement_model_data['d2_STATE']-3.1469*df_engagement_model_data['d3_STATE']+1.7295*df_engagement_model_data['d4_STATE']-1.1351*df_engagement_model_data['d2_REGION']+0.2374*df_engagement_model_data['d3_REGION']-0.4876*df_engagement_model_data['d1_AGE_O']+0.2411*df_engagement_model_data['d2_AGE_O']+0.2971*df_engagement_model_data['d3_AGE_O']-0.117*df_engagement_model_data['d2_PER_BLACK']-0.1393*df_engagement_model_data['d3_PER_ASIAN']+0.0638*df_engagement_model_data['d3_Estimate']+0.2138*df_engagement_model_data['d1_PER_NOT_IN_LABOUR_FORCE']-0.1564*df_engagement_model_data['d1_PER_INS_19_64_WORKED_LT_FT']-0.3065*df_engagement_model_data['d1_PER_WORKED_FT']-0.1627*df_engagement_model_data['d1_PER_WITH_DISABILITY']-0.1854*df_engagement_model_data['d1_HHINC_25K_TO_50K']-0.1286*df_engagement_model_data['d2_HHINC_25K_TO_50K']-0.068*df_engagement_model_data['d3_HHINC_25K_TO_50K']+0.1218*df_engagement_model_data['d2_HHINC_50_TO_75K']+0.2493*df_engagement_model_data['d3_HHINC_50_TO_75K']+0.2997*df_engagement_model_data['d1_HHINC_BELOW_25K']+0.134*df_engagement_model_data['d2_HHINC_BELOW_25K']--0.4972*df_engagement_model_data['d1_Contract_Type']+0.3927*df_engagement_model_data['d2_Contract_Type']+0.335*df_engagement_model_data['d4_Contract_Type']
    elif Contract_Type == 'FF & On Site':
        df_engagement_model_data['d1_Contract_Type'] = 0
        df_engagement_model_data['d2_Contract_Type'] = 1
        df_engagement_model_data['d4_Contract_Type'] = 0
        df_engagement_model_data['score'] = -0.6923-0.1696*df_engagement_model_data['d1_STATE']-0.72*df_engagement_model_data['d2_STATE']-3.1469*df_engagement_model_data['d3_STATE']+1.7295*df_engagement_model_data['d4_STATE']-0.72*df_engagement_model_data['d2_STATE']-3.1469*df_engagement_model_data['d3_STATE']+1.7295*df_engagement_model_data['d4_STATE']-1.1351*df_engagement_model_data['d2_REGION']+0.2374*df_engagement_model_data['d3_REGION']-0.4876*df_engagement_model_data['d1_AGE_O']+0.2411*df_engagement_model_data['d2_AGE_O']+0.2971*df_engagement_model_data['d3_AGE_O']-0.117*df_engagement_model_data['d2_PER_BLACK']-0.1393*df_engagement_model_data['d3_PER_ASIAN']+0.0638*df_engagement_model_data['d3_Estimate']+0.2138*df_engagement_model_data['d1_PER_NOT_IN_LABOUR_FORCE']-0.1564*df_engagement_model_data['d1_PER_INS_19_64_WORKED_LT_FT']-0.3065*df_engagement_model_data['d1_PER_WORKED_FT']-0.1627*df_engagement_model_data['d1_PER_WITH_DISABILITY']-0.1854*df_engagement_model_data['d1_HHINC_25K_TO_50K']-0.1286*df_engagement_model_data['d2_HHINC_25K_TO_50K']-0.068*df_engagement_model_data['d3_HHINC_25K_TO_50K']+0.1218*df_engagement_model_data['d2_HHINC_50_TO_75K']+0.2493*df_engagement_model_data['d3_HHINC_50_TO_75K']+0.2997*df_engagement_model_data['d1_HHINC_BELOW_25K']+0.134*df_engagement_model_data['d2_HHINC_BELOW_25K']--0.4972*df_engagement_model_data['d1_Contract_Type']+0.3927*df_engagement_model_data['d2_Contract_Type']+0.335*df_engagement_model_data['d4_Contract_Type']
    elif Contract_Type == 'PEPM & On Site':
        df_engagement_model_data['d1_Contract_Type'] = 0
        df_engagement_model_data['d2_Contract_Type'] = 0
        df_engagement_model_data['d4_Contract_Type'] = 1
        df_engagement_model_data['score'] = -0.6923-0.1696*df_engagement_model_data['d1_STATE']-0.72*df_engagement_model_data['d2_STATE']-3.1469*df_engagement_model_data['d3_STATE']+1.7295*df_engagement_model_data['d4_STATE']-0.72*df_engagement_model_data['d2_STATE']-3.1469*df_engagement_model_data['d3_STATE']+1.7295*df_engagement_model_data['d4_STATE']-1.1351*df_engagement_model_data['d2_REGION']+0.2374*df_engagement_model_data['d3_REGION']-0.4876*df_engagement_model_data['d1_AGE_O']+0.2411*df_engagement_model_data['d2_AGE_O']+0.2971*df_engagement_model_data['d3_AGE_O']-0.117*df_engagement_model_data['d2_PER_BLACK']-0.1393*df_engagement_model_data['d3_PER_ASIAN']+0.0638*df_engagement_model_data['d3_Estimate']+0.2138*df_engagement_model_data['d1_PER_NOT_IN_LABOUR_FORCE']-0.1564*df_engagement_model_data['d1_PER_INS_19_64_WORKED_LT_FT']-0.3065*df_engagement_model_data['d1_PER_WORKED_FT']-0.1627*df_engagement_model_data['d1_PER_WITH_DISABILITY']-0.1854*df_engagement_model_data['d1_HHINC_25K_TO_50K']-0.1286*df_engagement_model_data['d2_HHINC_25K_TO_50K']-0.068*df_engagement_model_data['d3_HHINC_25K_TO_50K']+0.1218*df_engagement_model_data['d2_HHINC_50_TO_75K']+0.2493*df_engagement_model_data['d3_HHINC_50_TO_75K']+0.2997*df_engagement_model_data['d1_HHINC_BELOW_25K']+0.134*df_engagement_model_data['d2_HHINC_BELOW_25K']--0.4972*df_engagement_model_data['d1_Contract_Type']+0.3927*df_engagement_model_data['d2_Contract_Type']+0.335*df_engagement_model_data['d4_Contract_Type']
    else:
        df_engagement_model_data['d1_Contract_Type'] = 0
        df_engagement_model_data['d2_Contract_Type'] = 0
        df_engagement_model_data['d4_Contract_Type'] = 0
        df_engagement_model_data['score'] = -0.6923-0.1696*df_engagement_model_data['d1_STATE']-0.72*df_engagement_model_data['d2_STATE']-3.1469*df_engagement_model_data['d3_STATE']+1.7295*df_engagement_model_data['d4_STATE']-0.72*df_engagement_model_data['d2_STATE']-3.1469*df_engagement_model_data['d3_STATE']+1.7295*df_engagement_model_data['d4_STATE']-1.1351*df_engagement_model_data['d2_REGION']+0.2374*df_engagement_model_data['d3_REGION']-0.4876*df_engagement_model_data['d1_AGE_O']+0.2411*df_engagement_model_data['d2_AGE_O']+0.2971*df_engagement_model_data['d3_AGE_O']-0.117*df_engagement_model_data['d2_PER_BLACK']-0.1393*df_engagement_model_data['d3_PER_ASIAN']+0.0638*df_engagement_model_data['d3_Estimate']+0.2138*df_engagement_model_data['d1_PER_NOT_IN_LABOUR_FORCE']-0.1564*df_engagement_model_data['d1_PER_INS_19_64_WORKED_LT_FT']-0.3065*df_engagement_model_data['d1_PER_WORKED_FT']-0.1627*df_engagement_model_data['d1_PER_WITH_DISABILITY']-0.1854*df_engagement_model_data['d1_HHINC_25K_TO_50K']-0.1286*df_engagement_model_data['d2_HHINC_25K_TO_50K']-0.068*df_engagement_model_data['d3_HHINC_25K_TO_50K']+0.1218*df_engagement_model_data['d2_HHINC_50_TO_75K']+0.2493*df_engagement_model_data['d3_HHINC_50_TO_75K']+0.2997*df_engagement_model_data['d1_HHINC_BELOW_25K']+0.134*df_engagement_model_data['d2_HHINC_BELOW_25K']--0.4972*df_engagement_model_data['d1_Contract_Type']+0.3927*df_engagement_model_data['d2_Contract_Type']+0.335*df_engagement_model_data['d4_Contract_Type']



    #-0.4972*df_engagement_model_data['d1_Contract_Type']+0.3927*df_engagement_model_data['d2_Contract_Type']+0.335*df_engagement_model_data['d4_Contract_Type']


    probab = []

    scores = df_engagement_model_data['score']

    for s in scores:
        probb = math.exp(-s)/(1+math.exp(-s))
        probab.append(probb)


    df_engagement_model_data['probability'] = probab

    return(df_engagement_model_data)



#---------------------Dashboard API Start here--------------------------------------------
@api_view(['GET'])
def cityStateClinics(request,format=None):
    if request.method == 'GET':
        try:
            #-----------------date------------------------------
            date = []
            date_data = everside_nps.objects.all().aggregate(Min('year'))
            date.append(date_data['year__min'])
            date_data = everside_nps.objects.all().aggregate(Max('year'))
            date.append(date_data['year__max'])
            #-----------------Region----------------------------
            region = []
            obj = everside_nps.objects.values_list('city','state').distinct()
            for i in obj:
                region_name = str(i[0])+','+str(i[1])
                region.append(region_name)
                region.sort()
            #-----------------Clinics-------------------------------
            clinics = {}
            for i in region:
                c_s = i.split(',')
                city = str(c_s[0])
                state = str(c_s[1])
                clinic_names = everside_nps.objects.values_list('clinic').filter(city=city,state=state).distinct()
                clinics[i] = itertools.chain(*clinic_names)
            return Response({'date':date,'region':region,'clinics':clinics})
        except:
            return Response({'Message':'No Data  except'})



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

            if int(start_year) == int(end_year):
                pass
            elif int(end_year) == int(start_year)+1: 
                pass
            else:
                return Response({'Message':'FALSE'})

            if int(end_year) == int(start_year)+1:
                month_count = 13 - int(start_month) + int(end_month)
                if month_count > 13:
                    return Response({'Message':'FALSE'})



            if start_year == end_year:
                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+str(start_month)+' AND year='+str(start_year)+') AND (CAST(month as inT)<='+str(end_month)+' AND year='+str(end_year)+');'
                count = everside_nps.objects.raw(query)
                total_count = len(count)

                query = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Promoter" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                count = everside_nps.objects.raw(query)
                total_promoters = len(count)
                promoters = round(len(count)/total_count*100)
                if promoters==0:
                    promoters = round(len(count)/total_count*100,2)

                query = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Passive" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                count = everside_nps.objects.raw(query)
                total_passive = len(count)
                passive = round(len(count)/total_count*100)
                if passive==0:
                    passive = round(len(count)/total_count*100,2)

                query = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Detractor" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                count = everside_nps.objects.raw(query)
                total_detractors = len(count)
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
                total_promoters = count
                promoters = round(count/total_count*100)
                if promoters==0:
                    promoters = round(count/total_count*100,2)
               
                query1 = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Passive" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12'+' AND year='+start_year+');'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Passive" AND (CAST(month as inT)>=1'+' AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                count = len(count1)+len(count2)
                total_passive = count
                passive = round(count/total_count*100)
                if passive==0:
                    passive = round(count/total_count*100,2)

                query1 = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Detractor" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12'+' AND year='+start_year+');'
                query2 = 'SELECT * FROM apiApp_everside_nps WHERE nps_label="Detractor" AND (CAST(month as inT)>=1'+' AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                count1 = everside_nps.objects.raw(query1)
                count2 = everside_nps.objects.raw(query2)
                count = len(count1)+len(count2)
                total_detractors = count
                detractor = round(count/total_count*100)
                if detractor==0:
                    detractor = round(count/total_count*100,2)





            nps ={
                "nps_score":(promoters-detractor),
                "promoters":promoters,
                "total_promoters":total_promoters,
                "passive":passive,
                "total_passive":total_passive,
                "detractors":detractor,
                "total_detractors":total_detractors
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

            
            return Response({'Message':'TRUE',
                             'nps':nps,
                             'nps_pie':nps_pie})
        except:
            return Response({'Message':'FALSE'})



@api_view(['GET'])
def netSentimentScore(request,format=None):
    if request.method == 'GET':
        try:
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')

            if int(start_year) == int(end_year):
                pass
            elif int(end_year) == int(start_year)+1: 
                pass
            else:
                return Response({'Message':'FALSE'})

            if int(end_year) == int(start_year)+1:
                month_count = 13 - int(start_month) + int(end_month)
                if month_count > 13:
                    return Response({'Message':'FALSE'})

            if start_year == end_year:
                query = 'SELECT * FROM apiApp_everside_nps WHERE (CAST(month as inT)>='+start_month+' AND year='+str(start_year)+') AND (CAST(month as inT)<='+str(end_month)+' AND year='+str(end_year)+');'
                count = everside_nps.objects.raw(query)
                total_count = len(count)
                query = 'SELECT * FROM apiApp_everside_nps WHERE label="Positive" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                count = everside_nps.objects.raw(query)
                total_positive = len(count)
                positive = round(len(count)/total_count*100)
                if positive==0:
                    positive = round(len(count)/total_count*100,2)

                query = 'SELECT * FROM apiApp_everside_nps WHERE label="Negative" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                count = everside_nps.objects.raw(query)
                total_negative = len(count)
                negative = round(len(count)/total_count*100)
                if negative==0:
                    negative = round(len(count)/total_count*100,2)

                query = 'SELECT * FROM apiApp_everside_nps WHERE label="Extreme" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                count = everside_nps.objects.raw(query)
                total_extreme = len(count)
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
                    total_positive = count
                    positive = round(count/total_count*100)
                    if positive==0:
                        positive = round(count/total_count*100,2)
        
                
                    query1 = 'SELECT * FROM apiApp_everside_nps WHERE label="Negative" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12'+' AND year='+start_year+');'
                    query2 = 'SELECT * FROM apiApp_everside_nps WHERE label="Negative" AND (CAST(month as inT)>=1'+' AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                    count1 = everside_nps.objects.raw(query1)
                    count2 = everside_nps.objects.raw(query2)
                    count = len(count1)+len(count2)
                    total_negative = count
                    negative = round(count/total_count*100)
                    if negative==0:
                        negative = round(count/total_count*100,2)
                    

                    query1 = 'SELECT * FROM apiApp_everside_nps WHERE label="Extreme" AND (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12'+' AND year='+start_year+');'
                    query2 = 'SELECT * FROM apiApp_everside_nps WHERE label="Extreme" AND (CAST(month as inT)>=1'+' AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+');'
                    count1 = everside_nps.objects.raw(query1)
                    count2 = everside_nps.objects.raw(query2)
                    count = len(count1)+len(count2)
                    total_extreme = count
                    extreme = round(count/total_count*100)
                    if extreme==0:
                        extreme = round(count/total_count*100,2)
                        
                    
            nss ={
                    "nss_score":(positive-negative-extreme),
                    "total": total_count,
                    "positive":positive,
                    "total_positive":total_positive,
                    "negative":negative,
                    "total_negative":total_negative,
                    "extreme":extreme,
                    "total_extreme":total_extreme,
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
            return Response({'Message':'TRUE',
                             'nss':nss,
                             'nss_pie':nss_pie})
        
        except:
            return Response({'Message':'FALSE'})



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

            if int(start_year) == int(end_year):
                pass
            elif int(end_year) == int(start_year)+1: 
                pass
            else:
                return Response({'Message':'FALSE'})

            if int(end_year) == int(start_year)+1:
                month_count = 13 - int(start_month) + int(end_month)
                if month_count > 13:
                    return Response({'Message':'FALSE'})

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
            return Response({'Message':'TRUE','nps_over_time':nps_over_time})
    except:
        return Response({'Message':'FALSE'})



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

            if int(start_year) == int(end_year):
                pass
            elif int(end_year) == int(start_year)+1: 
                pass
            else:
                return Response({'Message':'FALSE'})

            if int(end_year) == int(start_year)+1:
                month_count = 13 - int(start_month) + int(end_month)
                if month_count > 13:
                    return Response({'Message':'FALSE'})

            if start_year == end_year:
                for i in range(int(start_month),int(end_month)+1):
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
            return Response({'Message':'TRUE','nss_over_time':nss_over_time})
    except:
        return Response({'Message':'FALSE'})


@api_view(['GET'])
def npsVsSentiments(request,format=None):
    try:
        if request.method == 'GET':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            
            if int(start_year) == int(end_year):
                pass
            elif int(end_year) == int(start_year)+1: 
                pass
            else:
                return Response({'Message':'FALSE'})

            if int(end_year) == int(start_year)+1:
                month_count = 13 - int(start_month) + int(end_month)
                if month_count > 13:
                    return Response({'Message':'FALSE'})

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
            return Response({'Message':'TRUE','data':final_data})
            
    except:
        return Response({'Message':'FALSE'})


@api_view(['GET'])
def alertComments(request,format=None):
    try:
        if request.method == 'GET':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')

            if int(start_year) == int(end_year):
                pass
            elif int(end_year) == int(start_year)+1: 
                pass
            else:
                return Response({'Message':'FALSE'})

            if int(end_year) == int(start_year)+1:
                month_count = 13 - int(start_month) + int(end_month)
                if month_count > 13:
                    return Response({'Message':'FALSE'})

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
            final_dict = {}
            dict_id = {'id':i+1}
            final_dict.update(dict_id)
            final_dict.update(dict((serialized_data.data)[i]))
            # final_dict = dict_id|dict((serialized_data.data)[i])
            final_data.append(final_dict)
        return Response({'Message':'TRUE','data':final_data})
    except:
        return Response({'Message':'FALSE'})


@api_view(['GET'])
def topComments(request,format=None):
    try:
        if request.method == 'GET':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')

            if int(start_year) == int(end_year):
                pass
            elif int(end_year) == int(start_year)+1: 
                pass
            else:
                return Response({'Message':'FALSE'})

            if int(end_year) == int(start_year)+1:
                month_count = 13 - int(start_month) + int(end_month)
                if month_count > 13:
                    return Response({'Message':'FALSE'})


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
            final_dict = {}
            dict_id = {'id':i+1}
            # final_dict = dict_id|dict((serialized_data.data)[i])
            final_dict.update(dict_id)
            final_dict.update(dict((serialized_data.data)[i]))
            final_data.append(final_dict)
        return Response({'Message':'TRUE','data':final_data})
        
    except:
        return Response({'Message':'FALSE'})

@api_view(['GET'])
def totalComments(request,format=None):
    try:
        if request.method == 'GET':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            
            if start_year == end_year:
                query = 'SELECT * from apiApp_everside_nps where (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+')'
                query_exec = everside_nps.objects.raw(query)
                serialized_data = eversideTotalComments(query_exec,many=True)
            else:
                query1 = 'SELECT * from apiApp_everside_nps where (CAST(month as inT)>='+start_month+' AND year='+start_year+') AND (CAST(month as inT)<=12 AND year='+start_year+')'    
                query2 = 'SELECT * from apiApp_everside_nps where (CAST(month as inT)>=1 AND year='+end_year+') AND (CAST(month as inT)<='+end_month+' AND year='+end_year+')'
                query_exec1 = everside_nps.objects.raw(query1)
                query_exec2 = everside_nps.objects.raw(query2)
                query_exec =  list(query_exec1)+list(query_exec2)
                serialized_data = eversideTotalComments(query_exec,many=True)
            return Response({'Message':'TRUE','data':serialized_data.data})
    except:
        return Response({'Message':'FALSE'})

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

            if int(start_year) == int(end_year):
                pass
            elif int(end_year) == int(start_year)+1: 
                pass
            else:
                return Response({'Message':'FALSE'})

            if int(end_year) == int(start_year)+1:
                month_count = 13 - int(start_month) + int(end_month)
                if month_count > 13:
                    return Response({'Message':'FALSE'})

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

            return Response({'Message':'TRUE','data':final_data})     
        
    except:
        return Response({'Message':'FALSE'})


@api_view(['GET'])
def totalCards(request,format=None):
    try:
        if request.method == 'GET':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            
            if int(start_year) == int(end_year):
                pass
            elif int(end_year) == int(start_year)+1: 
                pass
            else:
                return Response({'Message':'FALSE'})

            if int(end_year) == int(start_year)+1:
                month_count = 13 - int(start_month) + int(end_month)
                if month_count > 13:
                    return Response({'Message':'FALSE'})

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
            return Response({'Message':'TRUE','card_data':card_data})
            
    except:
        return Response({'Message':'FALSE'})


@api_view(['GET'])
def wordFrequency(request,format=None):
    try:
        if request.method == 'GET':
            query = 'SELECT * FROM apiApp_everside_nps_word_frequency ORDER BY CAST(frequency AS INT) DESC'
            query_exec = everside_nps_word_frequency.objects.raw(query)
            data_serializer = eversideWordFrequencySerializer(query_exec,many=True)
            return Response(data_serializer.data)
    except:
        return Response({'Message':'No Data except'})


#----------------------Engagement Score----------------------------------------
@api_view(['POST'])
@parser_classes([MultiPartParser,FormParser])
def egStatistics(request,format=None):
    try:
        up_file = request.FILES.getlist('file')

        df = pd.read_csv(up_file[0])
        print(df.shape)
        if 'CLIENT_ID' in list(df.columns) and "MEMBER_ID" in list(df.columns) and 'ZIP' in df.columns and 'HOUSEHOLD_ID' in list(df.columns):
            mes = 'TRUE'

        else:
            mes = 'FALSE'
        return Response({'Message':mes,'rows':df.shape[0],'columns':df.shape[1]})

    except:
        return Response({'Message':"FALSE",'ERROR':'INCORRECT FILE TYPE'})



@api_view(['POST'])
@parser_classes([MultiPartParser,FormParser])
def egPercentileMember(request,format=None):
    try:
        up_file = request.FILES.getlist('file')
        df = pd.read_csv(up_file[0])
        out = func(df)
        out_prob = list(out['probability'])
        low = 0 # n < 0.5
        med = 0 # 0.5 < n < 0.75
        high = 0 # 0.75 < n
        graph = [] 
        p_values = [0,1,25,33,50,66,75,95,99,100]
        for i in p_values:
            p = np.percentile(out_prob,i)
            percentile_name = "P"+str(i)
            percentile_value = round(p,3)
            member_score = out_prob.count(p)
            if p < 0.5:
                low = low + 1
            elif 0.5 <= p < 0.75:
                med = med + 1
            else:
                high = high + 1

            frame = {
                'percentile_name':percentile_name,
                'percentile_value':percentile_value,
                'member_score':member_score
            }
            graph.append(frame)
            percentage = {
                'low':str(low*10)+"%",
                'medium':str(low*10+med*10)+"%",
                'high':'100%',
            }


        return Response({'Message':'TRUE','graph':graph,'percentage':percentage})

    except:
        return Response({'Message':"FALSE"})


# @api_view(['POST'])
# @parser_classes([MultiPartParser,FormParser])
# def egPercentileClient(request,format=None):
#     #try:
#         up_file = request.FILES.getlist('file')
#         df = pd.read_csv(up_file[0])
#         out_df = func(df)
#         out = out_df.loc[out_df.CLIENT_ID == request.data['client']]
#         out_prob = list(out['probability'])
#         print(out.shape)
#         low = {} # n < 0.5
#         med = {} # 0.5 < n < 0.75
#         high = {} # 0.75 < n
#         p_values = [0,1,25,33,50,66,75,95,99,100]
#         for i in p_values:
#             p = np.percentile(out_prob,i)
            
#             if p < 0.5:
#                 low['p'+str(i)] = round(p,3)
#                 low['p'+str(i)+'_total'] = out_prob.count(p)
#             elif 0.5 <= p < 0.75:
#                 med['p'+str(i)] = round(p,3)
#                 med['p'+str(i)+'_total'] = out_prob.count(p)
#             else:
#                 high['p'+str(i)] = round(p,3)
#                 high['p'+str(i)+'_total'] = out_prob.count(p)
#         return Response({'Message':"TRY",'low':low,'medium':med,'high':high})
        
#     #except:
#         #return Response({'Message':"FALSE"})
#         #df.loc[df.b > 10, 'b'].min()