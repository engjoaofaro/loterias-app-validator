import datetime

import boto3
import os
from datetime import datetime
from pytz import timezone

client = boto3.client('scheduler')


def schedule(game_type):
    cron = 'cron(00 01 * * ? *)'
    today = datetime.now()
    fuz = timezone('America/Sao_Paulo')
    date_sao_paulo = today.astimezone(fuz)
    index_week = date_sao_paulo.isoweekday()

    if game_type == 1:
        if index_week <= 2:
            cron = 'cron(50 23 ? * 3 *)'
        elif index_week == 3 or index_week == 4:
            cron = 'cron(50 23 ? * 5 *)'
        elif index_week == 5 or index_week == 6:
            cron = 'cron(50 23 ? * 7 *)'
        elif index_week == 7:
            cron = 'cron(50 23 ? * 3 *)'
        update_schedule('schedule-step-function-flow', cron)

    if game_type == 2:
        if index_week == 7:
            cron = 'cron(50 23 ? * 2 *)'
        update_schedule('schedule-step-function-flow_2', cron)


def update_schedule(name, cron):
    client.update_schedule(
        Name=name,
        FlexibleTimeWindow={
            'Mode': 'OFF'
        },
        ScheduleExpression=cron,
        ScheduleExpressionTimezone='America/Sao_Paulo',
        Target={
            'Arn': os.getenv('TARGET_ARN'),
            'RoleArn': os.getenv('ROLE_ARN')
        },
        State='ENABLED'
    )
