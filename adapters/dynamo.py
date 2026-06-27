def send_to_dynamo(item, table):
    """Persiste a aposta na tabela Game com status PENDING (apurada depois)."""
    response = table.put_item(
        Item={
            'voucher': item['voucher'],
            'email': item.get('email'),
            'gameType': item['gameType'],
            'lotteryNumber': item['lotteryNumber'],
            'games': item['games'],
            'status': 'PENDING',
        }
    )
    return response['ResponseMetadata']['HTTPStatusCode']
