'''@api_view(['GET'])
def date_filter(request,format=None):
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
            return Response({'Message':'No Data Available'})'''

