def send_to_dynamo(item, table):
    voucher = item['voucher']
    email = item['email']
    game_type = item['gameType']
    lottery_number = item['lotteryNumber']
    games_list = item['games']

    response = table.put_item(
        Item={
            'voucher': voucher,
            'email': email,
            'gameType': game_type,
            'lotteryNumber': lottery_number,
            'games': games_list
        }
    )

    status_code = response['ResponseMetadata']['HTTPStatusCode']
    print(status_code)
