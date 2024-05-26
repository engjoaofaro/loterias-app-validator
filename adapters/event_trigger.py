import boto3
import os
from util.cron import get_cron

client = boto3.client('scheduler')


def schedule(game_type):

    if game_type == 1:
        cron = get_cron(1)
        update_schedule('schedule-step-function-flow', cron)

    if game_type == 2:
        cron = get_cron(2)
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
