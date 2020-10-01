import boto3
from datetime import datetime
from datetime import timedelta

createsession = boto3.Session(profile_name='atul')
cloudwatch = createsession.client('cloudwatch')

def getmetricdata(**kwargs):
    if kwargs.get('NextToken') is None or kwargs.get('NextToken') == '':
        return cloudwatch.get_metric_data(MetricDataQueries = 
            kwargs.get("MetricDataQueries"),
            StartTime=kwargs.get("StartTime"),
            EndTime=kwargs.get("EndTime"),
            MaxDatapoints=5000
            )
    else:
        return cloudwatch.get_metric_data(MetricDataQueries = 
            kwargs.get("MetricDataQueries"),
            StartTime=kwargs.get("StartTime"),
            EndTime=kwargs.get("EndTime"),
            NextToken=kwargs.get("NextToken"),
            MaxDatapoints=5000
            )
count = 0
maxval = 0
list2 = []
next_token = ''

starttime = datetime.utcnow() - timedelta(days=14)
endtime = datetime.utcnow()

awslambda = createsession.client('lambda')
lpaginator = awslambda.get_paginator('list_functions')
literator = lpaginator.paginate()

for functionlist in literator:
    if 'Functions' in functionlist:
        for func_name in functionlist['Functions']:
            next_token=''
            while next_token is not None:
                peakresponse = getmetricdata(MetricDataQueries=[
                    {
                        'Id': 'concurrent',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/Lambda',
                                'MetricName': 'ConcurrentExecutions',
                                'Dimensions': [
                                                    {
                                                        'Name': 'FunctionName',
                                                        'Value': func_name['FunctionName']
                                                    },
                                                ]
                            },
                            'Period': 60,
                            'Stat': 'Maximum',
                            'Unit': 'Count'
                        },
                        'Label': 'Concurrent',
                        'ReturnData': True
                    }
                ],
                    StartTime=starttime,
                    EndTime=endtime,
                    NextToken=next_token
                    )

                for result in peakresponse['MetricDataResults']:  
                    maxval = 0
                    count += 1
                    for i in range(len(result['Timestamps'])):
                        #if func_name['FunctionName'] == 'lambdafunction1': 
                           if result['Timestamps'][i] != 0: 
                              if result['Values'][i] > maxval:
                                  maxval = result['Values'][i]
                                  #list2.extend([func_name["FunctionName"],maxval])
                              
                                    
                                   
                    
                    if result['StatusCode']=='PartialData':
                          next_token=peakresponse['NextToken']
                    else:
                          next_token=None        
                list2.append([func_name["FunctionName"],maxval])
                break
print(list2)        