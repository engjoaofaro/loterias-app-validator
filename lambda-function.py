import boto3
import json
from adapters.dynamo import send_to_dynamo as send

dynamodb = boto3.resource('dynamodb')


def lambda_handler(event, context):
    print("Receiving event: {} and context: {}", event, context)
    table = dynamodb.Table('Game')

    item = event['Records'][0]['body']
    item = json.loads(item)

    send(item, table)
