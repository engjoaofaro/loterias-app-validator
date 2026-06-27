import boto3
import json
import logging

from adapters.dynamo import send_to_dynamo as send
from adapters.sns import check_subscription, subscribe
from util.validation import validate_item

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'Game'


def lambda_handler(event, context):
    """Consome o GameDto da fila SQS: valida, inscreve e-mail (opcional),
    agenda a apuração e persiste a aposta. Processa TODOS os records do batch
    e usa partial batch response (requer ReportBatchItemFailures na ESM)."""
    table = dynamodb.Table(TABLE_NAME)
    failures = []

    for record in event.get('Records', []):
        message_id = record.get('messageId')
        try:
            item = validate_item(json.loads(record['body']))
            email = item['email']

            if email:
                if not check_subscription(email):
                    subscribe(email)
                else:
                    logger.info("E-mail já inscrito no tópico")

            # A apuração roda por agendamento diário (EventBridge) — o validador
            # não gerencia mais schedules. Aqui apenas persistimos a aposta.
            send(item, table)
            logger.info("Aposta processada: voucher=%s", item['voucher'])
        except Exception as error:  # noqa: BLE001 - isola a falha por mensagem
            logger.exception("Falha ao processar mensagem %s: %s", message_id, error)
            failures.append({"itemIdentifier": message_id})

    return {"batchItemFailures": failures}
