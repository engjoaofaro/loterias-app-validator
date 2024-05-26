import datetime

import boto3
import os
from datetime import datetime
from pytz import timezone

client = boto3.client('scheduler')


def schedule(game_type):
    index_megasena = [2, 4, 6]
    cron = 'cron(00 01 * * ? *)'
    if game_type == 1:
        today = datetime.now()
        fuz = timezone('America/Sao_Paulo')
        date_sao_paulo = today.astimezone(fuz)
        index_week = date_sao_paulo.weekday()
        print(index_week)

        if index_week in index_megasena:
            cron = 'cron(00 01 ? * '+str(index_week)+' *)'
        else:
            if index_week < 2:
                cron = 'cron(00 01 ? * 2 *)'
            elif index_week < 4:
                cron = 'cron(00 01 ? * 4 *)'
            elif index_week < 6:
                cron = 'cron(00 01 ? * 6 *)'
            elif index_week == 7:
                cron = 'cron(00 01 ? * 2 *)'

    client.update_schedule(
        Name='schedule-step-function-flow',
        FlexibleTimeWindow={
            'Mode': 'OFF'
        },
        ScheduleExpression=cron,
        Target={
            'Arn': os.getenv('TARGET_ARN'),
            'RoleArn': os.getenv('ROLE_ARN')
            },
        State='ENABLED'
    )
