import boto3
import os

client = boto3.client('sns')


def check_subscription(email):
    print(email)
    response = client.list_subscriptions_by_topic(
        TopicArn=os.getenv('TOPIC_ARN'),
        NextToken=''
    )
    subscriptions = response['Subscriptions']

    for i in subscriptions:
        if i['Endpoint'] == email:
            return True
        else:
            return False


def subscribe(email):
    client.subscribe(
        TopicArn=os.getenv('TOPIC_ARN'),
        Protocol='email-json',
        Endpoint=email,
        Attributes={}
    )
