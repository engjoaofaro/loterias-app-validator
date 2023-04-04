import boto3
import os

client = boto3.client('scheduler')


def schedule():
    client.update_schedule(
        Name='schedule-step-function-flow',
        FlexibleTimeWindow={
            'Mode': 'OFF'
        },
        ScheduleExpression='cron(00 22 * * ? *)',
        Target={
            'Arn': os.getenv('TARGET_ARN'),
            'RoleArn': os.getenv('ROLE_ARN')
            },
        State='ENABLED'
    )
