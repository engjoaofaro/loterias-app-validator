import boto3
import json
from adapters.dynamo import send_to_dynamo as send
from adapters.sns import check_subscription
from adapters.sns import subscribe
from adapters.event_trigger import schedule as activate

dynamodb = boto3.resource('dynamodb')


def lambda_handler(event, context):
    print("Receiving event: {} and context: {}", event, context)
    table = dynamodb.Table('Game')

    item = event['Records'][0]['body']
    item = json.loads(item)
    email = item['email']

    sub = check_subscription(email)

    if not sub:
        subscribe(email)
    if sub:
        print("Email já inscrito no tópico")

    print("Ativando evento...")
    activate()
    print("Evento ativado")

    send(item, table)
