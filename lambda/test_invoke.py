import boto3
import json
import time

part_number = '64118391363'

test_payload = f'''
    {{
        "headers": {{
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        }},
        "proxies": {{
            "http": "http://45.72.59.14:3128"
        }},
        "part_number": "{part_number}"
    }}
    '''

client = boto3.client('lambda')

# response = client.invoke(
#     FunctionName='arn:aws:lambda:us-east-2:263954138296:function:scrape_ecs-tuning',
#     InvocationType='RequestResponse',
#     LogType='None',
#     Payload=json.dumps(test_payload)
# )


# response_payload = json.loads(json.loads(response['Payload'].read()))

# print(response_payload)

response = client.invoke(
    FunctionName='arn:aws:lambda:us-east-2:263954138296:function:mule-alpha',
    InvocationType='RequestResponse',
    LogType='None',
    Payload=test_payload
)

response_payload = response['Payload'].read()

print(response_payload)