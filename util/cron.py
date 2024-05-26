from datetime import datetime
from pytz import timezone


def get_cron(game_type):
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
        return cron
    if game_type == 2:
        if index_week == 7:
            cron = 'cron(50 23 ? * 2 *)'
        return cron
    if game_type == 3:
        if index_week == 1 or index_week > 5:
            cron = 'cron(50 23 ? * 2 *)'
        if index_week == 2 or index_week == 3:
            cron = 'cron(50 23 ? * 4 *)'
        if index_week == 4 or index_week == 5:
            cron = 'cron(50 23 ? * 6 *)'
        return cron
