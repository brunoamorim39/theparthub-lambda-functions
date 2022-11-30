import boto3
import json
import threading
import sys

class ScraperThread(threading.Thread):
    def __init__(self, thread_id, name, target):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name
        self.target = target
    
    def run(self):
        print(f'Starting {self.name}')
        function = {'target': self.target}
        function['target']()
        print(f'Exiting {self.name}')

def print_error_message(error_message, function_name, response_payload):
    print('='*len(str(error_message)))
    print(f'{function_name}')
    print('-'*len(str(error_message)))
    print(f'{error_message}')
    print('-'*len(str(error_message)))
    print(f'{response_payload}')
    print('='*len(str(error_message)))

#####################
#### Mule - Beta ####
#####################
def lambda_handler(event, context):
    # Autozone
    # Currently having timeout issues when request is sent via AWS Lambda
    def autozone():
        try:
            response = aws_lambda.invoke(
                FunctionName='arn:aws:lambda:us-east-2:263954138296:function:scrape_autozone',
                InvocationType='RequestResponse',
                LogType='None',
                Payload=json.dumps(scraper_payload)
            )
            response_payload = response['Payload'].read()
            for result in json.loads(json.loads(response_payload)):
                results.append(result)
        except (AttributeError, TypeError, json.decoder.JSONDecodeError) as e:
            print_error_message(e, sys._getframe().f_code.co_name, response_payload)
    
    # O'Reilly Auto Parts
    # Currently having timeout issues when request is sent via AWS Lambda
    def oreillyautoparts():
        try:
            response = aws_lambda.invoke(
                FunctionName='arn:aws:lambda:us-east-2:263954138296:function:scrape_oreilly-auto-parts',
                InvocationType='RequestResponse',
                LogType='None',
                Payload=json.dumps(scraper_payload)
            )
            response_payload = response['Payload'].read()
            for result in json.loads(json.loads(response_payload)):
                results.append(result)
        except (AttributeError, TypeError, json.decoder.JSONDecodeError) as e:
            print_error_message(e, sys._getframe().f_code.co_name, response_payload)

    # Bimmerworld
    def bimmerworld():
        try:
            response = aws_lambda.invoke(
                FunctionName='arn:aws:lambda:us-east-2:263954138296:function:scrape_bimmerworld',
                InvocationType='RequestResponse',
                LogType='None',
                Payload=json.dumps(scraper_payload)
            )
            response_payload = response['Payload'].read()
            for result in json.loads(json.loads(response_payload)):
                results.append(result)
        except (AttributeError, TypeError, json.decoder.JSONDecodeError) as e:
            print_error_message(e, sys._getframe().f_code.co_name, response_payload)

    # RockAuto
    def rockauto():
        try:
            response = aws_lambda.invoke(
                FunctionName='arn:aws:lambda:us-east-2:263954138296:function:scrape_rockauto',
                InvocationType='RequestResponse',
                LogType='None',
                Payload=json.dumps(scraper_payload)
            )
            response_payload = response['Payload'].read()
            for result in json.loads(json.loads(response_payload)):
                results.append(result)
        except (AttributeError, TypeError, json.decoder.JSONDecodeError) as e:
            print_error_message(e, sys._getframe().f_code.co_name, response_payload)

    # AutohausAZ
    def autohausaz():
        try:
            response = aws_lambda.invoke(
                FunctionName='arn:aws:lambda:us-east-2:263954138296:function:scrape_autohausaz',
                InvocationType='RequestResponse',
                LogType='None',
                Payload=json.dumps(scraper_payload)
            )
            response_payload = response['Payload'].read()
            for result in json.loads(json.loads(response_payload)):
                results.append(result)
        except (AttributeError, TypeError, json.decoder.JSONDecodeError) as e:
            print_error_message(e, sys._getframe().f_code.co_name, response_payload)

    scraper_payload = event
    aws_lambda = boto3.client('lambda')
    results = []

    threads = []
    # threads.append(ScraperThread(6, 'thread_autozone', autozone))
    # threads.append(ScraperThread(7, 'thread_oreillyautoparts', oreillyautoparts))
    threads.append(ScraperThread(8, 'thread_bimmerworld', bimmerworld))
    threads.append(ScraperThread(9, 'thread_rockauto', rockauto))
    threads.append(ScraperThread(10, 'thread_autohausaz', autohausaz))

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    return results[:100]