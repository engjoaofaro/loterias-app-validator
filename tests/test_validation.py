import unittest

from util.validation import validate_item, is_subscribed


def valid_item():
    return {
        "gameType": 1,
        "email": "user@dominio.com",
        "voucher": "uuid-x",
        "lotteryNumber": 2890,
        "games": [[7, 18, 35, 42, 51, 60]],
    }


class TestValidateItem(unittest.TestCase):
    def test_aceita_item_valido_e_normaliza_gametype_para_int(self):
        item = valid_item()
        item["gameType"] = "1"  # pode chegar como string
        out = validate_item(item)
        self.assertEqual(out["gameType"], 1)

    def test_rejeita_quando_falta_campo_obrigatorio(self):
        for field in ("gameType", "voucher", "lotteryNumber", "games"):
            item = valid_item()
            del item[field]
            with self.assertRaises(ValueError):
                validate_item(item)

    def test_email_e_opcional(self):
        item = valid_item()
        del item["email"]
        out = validate_item(item)
        self.assertIsNone(out["email"])

    def test_rejeita_gametype_invalido(self):
        item = valid_item()
        item["gameType"] = 9
        with self.assertRaises(ValueError):
            validate_item(item)

    def test_rejeita_games_vazio_ou_mal_formado(self):
        item = valid_item()
        item["games"] = []
        with self.assertRaises(ValueError):
            validate_item(item)
        item2 = valid_item()
        item2["games"] = "nao-e-lista"
        with self.assertRaises(ValueError):
            validate_item(item2)


class TestIsSubscribed(unittest.TestCase):
    def test_retorna_true_quando_email_esta_inscrito(self):
        subs = [{"Endpoint": "a@b.com"}, {"Endpoint": "c@d.com"}]
        self.assertTrue(is_subscribed(subs, "c@d.com"))

    def test_retorna_false_quando_email_nao_esta_inscrito(self):
        subs = [{"Endpoint": "a@b.com"}, {"Endpoint": "c@d.com"}]
        self.assertFalse(is_subscribed(subs, "x@y.com"))

    def test_retorna_false_para_lista_vazia(self):
        self.assertFalse(is_subscribed([], "a@b.com"))


if __name__ == "__main__":
    unittest.main()
