import boto3
from datetime import datetime
from datetime import timedelta

session=boto3.Session(profile_name='name')
lamdadata=session.client('lambda')
response=lamdadata.list_functions()
print(response)
cloudwatch=session.client('cloudwatch')
maxval = 0
list1= []
starttime=datetime.utcnow() - timedelta(days=14)
endtime = datetime.utcnow()
for i in range(len(response['Functions'])):
    peakresponse=cloudwatch.get_metric_data(
        MetricDataQueries=[
           {
                        'Id': 'concurrent',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/Lambda',
                                'MetricName': 'ConcurrentExecutions',
                                'Dimensions': [
                                                    {
                                                        'Name': 'FunctionName',
                                                        'Value':response['Functions'][i]['FunctionName']
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
                    EndTime=endtime
    )
    for result in  peakresponse['MetricDataResults']:
        maxval = 0
        for j in range(len(result['Timestamps'])):
           if maxval < result['Values'][j]:
                maxval = result['Values'][j]
                
    list1.append([response['Functions'][i]['FunctionName'],maxval])
            


print(list1)
