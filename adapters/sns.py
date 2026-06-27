import boto3
import os

from util.validation import is_subscribed

client = boto3.client('sns')


def check_subscription(email):
    """Verifica se o e-mail já está inscrito no tópico, paginando os resultados."""
    topic_arn = os.getenv('TOPIC_ARN')
    next_token = None
    while True:
        kwargs = {'TopicArn': topic_arn}
        if next_token:
            kwargs['NextToken'] = next_token
        response = client.list_subscriptions_by_topic(**kwargs)
        if is_subscribed(response.get('Subscriptions', []), email):
            return True
        next_token = response.get('NextToken')
        if not next_token:
            return False


def subscribe(email):
    client.subscribe(
        TopicArn=os.getenv('TOPIC_ARN'),
        Protocol='email-json',
        Endpoint=email,
        Attributes={}
    )
