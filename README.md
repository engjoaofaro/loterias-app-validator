# loterias-app-validator

Lambda (Python) que **recebe as apostas do usuário pela fila SQS**, persiste no
DynamoDB, inscreve o e-mail no tópico SNS de resultados e **agenda a execução do
fluxo de apuração** (Step Functions via EventBridge Scheduler) conforme o calendário
de cada loteria. É o ponto de entrada do pipeline de apuração do **Loterias Sim**.

> Função Lambda implantada: `loterias-app-to-dynamodb`.
> Parte do ecossistema **Loterias Sim** — visão geral em [Arquitetura](#arquitetura-e-fluxo).

---

## Visão geral

| Item | Valor |
|------|-------|
| Runtime | Python 3.9+ |
| Handler | `lambda_function.lambda_handler` |
| Gatilho | Mensagens da fila **SQS** `loterias-app-queue` |
| Persistência | DynamoDB tabela `Game` |
| Notificação | SNS (inscrição de e-mail, protocolo `email-json`) |
| Agendamento | EventBridge **Scheduler** → Step Functions (`loterias-app-core`) |
| Fuso | `America/Sao_Paulo` |

### Loterias suportadas (`gameType`)
| Código | Loteria |
|:------:|---------|
| 1 | Mega-Sena |
| 2 | Lotofácil |
| 3 | Lotomania |

---

## Estrutura

```
loterias-app-validator/
├── lambda_function.py        # Handler: orquestra inscrição + agendamento + persistência
├── adapters/                 # Padrão Adapter (integrações AWS)
│   ├── dynamo.py             # send_to_dynamo(item, table) → grava aposta na tabela Game
│   ├── sns.py                # check_subscription(email) / subscribe(email) no tópico SNS
│   └── event_trigger.py      # schedule(game_type) / update_schedule(name, cron) no Scheduler
└── util/
    └── cron.py               # get_cron(game_type) → expressão cron por loteria e dia da semana
```

---

## Fluxo do handler

Evento recebido (SQS):
```json
{
  "Records": [
    { "body": "{\"email\":\"...\",\"gameType\":1,\"voucher\":\"...\",\"lotteryNumber\":2890,\"games\":[[...]]}" }
  ]
}
```

Passos (`lambda_function.py`):
1. Lê o `Game` table e faz `json.loads` do `Records[0].body`.
2. Extrai `email` e `gameType`.
3. `check_subscription(email)`; se não inscrito, `subscribe(email)` no SNS.
4. `activate(game_type)` → calcula o cron da loteria (`util/cron.py`) e faz
   `update_schedule` no EventBridge Scheduler apontando para a Step Function.
5. `send(item, table)` → grava a aposta completa na tabela `Game`.

---

## Lógica de agendamento (`util/cron.py`)

`get_cron(game_type)` gera a expressão **cron(EventBridge)** com base no `gameType` e no
**dia da semana atual** (fuso São Paulo), para que a apuração rode logo após o próximo
sorteio. Default: `cron(00 01 * * ? *)`.

| gameType | Regra (dia atual → cron) |
|:--------:|--------------------------|
| 1 (Mega-Sena) | Seg–Ter→`cron(50 23 ? * 3 *)` · Qua–Qui→`cron(50 23 ? * 5 *)` · Sex–Sáb→`cron(50 23 ? * 7 *)` · Dom→`cron(50 23 ? * 3 *)` |
| 2 (Lotofácil) | Dom→`cron(45 23 ? * 2 *)` · demais dias→default diário |
| 3 (Lotomania) | Seg/Sex–Dom→`cron(40 23 ? * 2 *)` · Ter–Qua→`cron(40 23 ? * 4 *)` · Qui–Sex→`cron(40 23 ? * 6 *)` |

> Os schedules são **atualizados** (`update_schedule`), não criados — devem existir
> previamente: `schedule-step-function-flow`, `schedule-step-function-flow_2`,
> `schedule-step-function-flow_3`.

---

## Variáveis de ambiente

| Variável | Descrição |
|----------|-----------|
| `TOPIC_ARN` | ARN do tópico SNS de resultados |
| `TARGET_ARN` | ARN da Step Function alvo (apuração / `loterias-app-core`) |
| `ROLE_ARN` | ARN da role usada pelo EventBridge Scheduler para invocar o alvo |

---

## Permissões (IAM)

A role precisa de: `dynamodb:PutItem` (tabela `Game`), `sns:Subscribe` +
`sns:ListSubscriptionsByTopic`, `scheduler:UpdateSchedule`/`GetSchedule`, `iam:PassRole`
(para `ROLE_ARN`) e o acesso de leitura da fila SQS de origem
(`sqs:ReceiveMessage`/`DeleteMessage`/`GetQueueAttributes`).

---

## Deploy

```bash
pip install -r requirements.txt -t build/
cp -r lambda_function.py adapters/ util/ build/
( cd build && zip -r ../function.zip . )
aws lambda update-function-code --function-name loterias-app-to-dynamodb \
  --zip-file fileb://function.zip --region sa-east-1
```

---

## Arquitetura e fluxo

```
loterias-sim-api ─► SQS (loterias-app-queue) ─► loterias-app-validator
                                                      │
                       ┌──────────────┬──────────────┤
                       ▼              ▼              ▼
                  DynamoDB(Game)   SNS(subscribe)  EventBridge Scheduler
                                                      │  (no horário do sorteio)
                                                      ▼
                                              Step Functions ─► loterias-app-core ─► SNS(e-mail)
```

---

## Pontos de atenção e melhorias

- 🐞 **Bug em `adapters/sns.py` (`check_subscription`):** retorna no meio do loop e
  pode dar falso negativo na primeira inscrição que não casa. Trocar por `any(...)` ou
  `continue` em vez de `return` dentro do laço.
- ⚠️ **Sem tratamento de erro / validação** do evento (assume `Records[0]`, JSON
  válido, campos presentes). Adicionar validação + DLQ na fila.
- ⚠️ **Tabela `Game` fixa no código** — externalizar em variável de ambiente.
- 🕐 **`datetime.now()` sem timezone** em `cron.py` (linha 7): usar
  `datetime.now(timezone('America/Sao_Paulo'))` para evitar depender do fuso do runtime.
- ✉️ A inscrição SNS `email-json` exige **confirmação manual** do usuário antes de
  receber resultados — documentar isso no fluxo do produto.
- 📌 Idempotência: `update_schedule` roda a cada mensagem; ok, mas vale registrar/logar.
- 🧪 Sem testes — cobrir `get_cron` (lógica por dia/loteria) e os adapters.
