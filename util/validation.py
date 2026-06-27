"""Validação pura do GameDto recebido via SQS e checagem de inscrição SNS.

Sem dependências de AWS — totalmente testável.
"""

VALID_GAME_TYPES = (1, 2, 3)


def validate_item(item):
    """Valida e normaliza um GameDto. Lança ValueError se inválido.

    Contrato esperado: {gameType:int, voucher:str, lotteryNumber, games:[[int]], email?:str}
    """
    if not isinstance(item, dict):
        raise ValueError("Mensagem inválida: não é um objeto.")

    for field in ("gameType", "voucher", "lotteryNumber", "games"):
        if field not in item or item[field] in (None, ""):
            raise ValueError(f"Campo obrigatório ausente: {field}")

    try:
        game_type = int(item["gameType"])
    except (TypeError, ValueError):
        raise ValueError("gameType inválido.")
    if game_type not in VALID_GAME_TYPES:
        raise ValueError(f"gameType inválido: {game_type} (use 1, 2 ou 3).")

    games = item["games"]
    if not isinstance(games, list) or len(games) == 0:
        raise ValueError("games deve ser uma lista não-vazia de jogos.")
    for game in games:
        if not isinstance(game, list) or len(game) == 0:
            raise ValueError("Cada jogo deve ser uma lista não-vazia de dezenas.")

    return {
        "gameType": game_type,
        "email": item.get("email") or None,
        "voucher": item["voucher"],
        "lotteryNumber": item["lotteryNumber"],
        "games": games,
    }


def is_subscribed(subscriptions, email):
    """True se o e-mail consta entre as inscrições do tópico."""
    return any(s.get("Endpoint") == email for s in (subscriptions or []))
