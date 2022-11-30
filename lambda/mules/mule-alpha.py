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

######################
#### Mule - Alpha ####
######################
def lambda_handler(event, context):
    # ECS Tuning
    def ecstuning():
        try:
            response = aws_lambda.invoke(
                FunctionName='arn:aws:lambda:us-east-2:263954138296:function:scrape_ecs-tuning',
                InvocationType='RequestResponse',
                LogType='None',
                Payload=json.dumps(scraper_payload)
            )
            response_payload = response['Payload'].read()
            for result in json.loads(json.loads(response_payload)):
                results.append(result)
        except (AttributeError, TypeError, json.decoder.JSONDecodeError) as e:
            print_error_message(e, sys._getframe().f_code.co_name, response_payload)

    # Turner Motorsport
    def turnermotorsport():
        try:
            response = aws_lambda.invoke(
                FunctionName='arn:aws:lambda:us-east-2:263954138296:function:scrape_turner-motorsport',
                InvocationType='RequestResponse',
                LogType='None',
                Payload=json.dumps(scraper_payload)
            )
            response_payload = response['Payload'].read()
            for result in json.loads(json.loads(response_payload)):
                results.append(result)
        except (AttributeError, TypeError, json.decoder.JSONDecodeError) as e:
            print_error_message(e, sys._getframe().f_code.co_name, response_payload)

    # Pelican Parts
    def pelicanparts():
        try:
            response = aws_lambda.invoke(
                FunctionName='arn:aws:lambda:us-east-2:263954138296:function:scrape_pelican-parts',
                InvocationType='RequestResponse',
                LogType='None',
                Payload=json.dumps(scraper_payload)
            )
            response_payload = response['Payload'].read()
            for result in json.loads(json.loads(response_payload)):
                results.append(result)
        except (AttributeError, TypeError, json.decoder.JSONDecodeError) as e:
            print_error_message(e, sys._getframe().f_code.co_name, response_payload)

    # FCP Euro
    def fcpeuro():
        try:
            response = aws_lambda.invoke(
                FunctionName='arn:aws:lambda:us-east-2:263954138296:function:scrape_fcp-euro',
                InvocationType='RequestResponse',
                LogType='None',
                Payload=json.dumps(scraper_payload)
            )
            response_payload = response['Payload'].read()
            for result in json.loads(json.loads(response_payload)):
                results.append(result)
        except (AttributeError, TypeError, json.decoder.JSONDecodeError) as e:
            print_error_message(e, sys._getframe().f_code.co_name, response_payload)

    # 034 Motorsport
    def _034motorsport():
        try:
            response = aws_lambda.invoke(
                FunctionName='arn:aws:lambda:us-east-2:263954138296:function:scrape_034-motorsport',
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
    threads.append(ScraperThread(1, 'thread_ecstuning', ecstuning))
    threads.append(ScraperThread(2, 'thread_turnermotorsport', turnermotorsport))
    # threads.append(ScraperThread(3, 'thread_pelicanparts', pelicanparts))
    threads.append(ScraperThread(4, 'thread_fcpeuro', fcpeuro))
    threads.append(ScraperThread(5, 'thread_034motorsport', _034motorsport))

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    return results[:100]