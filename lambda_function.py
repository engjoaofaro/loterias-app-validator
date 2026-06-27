import boto3
import json
import logging

from adapters.dynamo import send_to_dynamo as send
from util.validation import validate_item

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'Game'


def lambda_handler(event, context):
    """Consome o GameDto da fila SQS: valida e persiste a aposta (status PENDING).

    Processa TODOS os records do batch e usa partial batch response
    (requer ReportBatchItemFailures na ESM). A notificação ao usuário é feita por
    e-mail (SES): confirmação na sim-api e resultado na apuração (core)."""
    table = dynamodb.Table(TABLE_NAME)
    failures = []

    for record in event.get('Records', []):
        message_id = record.get('messageId')
        try:
            item = validate_item(json.loads(record['body']))
            send(item, table)
            logger.info("Aposta processada: voucher=%s", item['voucher'])
        except Exception as error:  # noqa: BLE001 - isola a falha por mensagem
            logger.exception("Falha ao processar mensagem %s: %s", message_id, error)
            failures.append({"itemIdentifier": message_id})

    return {"batchItemFailures": failures}
