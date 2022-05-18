# pybotx-fsm

[![codecov](https://codecov.io/gh/ExpressApp/pybotx-fsm/branch/master/graph/badge.svg?token=JWT9JWU2Z4)](https://codecov.io/gh/ExpressApp/pybotx-fsm)

Конечный автомат (Finite state machine) для ботов на базе библиотеки
[pybotx](https://github.com/ExpressApp/pybotx).


## Возможности

* Лёгкое создание графа состояний и их переключений.
* Передача данных в следующее состояние при явном вызове перехода.


## Подготовка к установке

Для работы библиотеки необходим Redis, который уже встроен в последние версии
[коробки](https://github.com/ExpressApp/async-box).


## Установка
Используя `poetry`:

```bash
poetry add pybotx-fsm
```

## Работа с графом состояний

1. Создайте `enum` для возможных состояний автомата:

```python #fsm_init
from enum import Enum, auto

from pybotx_fsm import FSMCollector


class LoginStates(Enum):
    enter_email = auto()
    enter_password = auto()


fsm = FSMCollector(LoginStates)
```


2. Добавьте экземпляр автомата в мидлвари для того, чтобы бот мог использовать его:

```python #fsm_usage
Bot(
    collectors=[
        myfile.collector,
    ],
    bot_accounts=[
        BotAccountWithSecret(
            # Не забудьте заменить эти учётные данные на настоящие,
            # когда создадите бота в панели администратора.
            id=UUID("123e4567-e89b-12d3-a456-426655440000"),
            host="cts.example.com",
            secret_key="e29b417773f2feab9dac143ee3da20c5",
        ),
    ],
    middlewares=[
        FSMMiddleware([myfile.fsm], state_repo_key="redis_repo"),
    ],
)
```

3. Добавьте в `bot.state.{state_repo_key}` совместимый redis репозиторий:

```python #noqa
bot.state.redis_repo = await RedisRepo.init(...)
```


4. Создайте обработчики конкретных состояний:

```python #fsm_state_handlers
@fsm.on(LoginStates.enter_email)
async def enter_email(message: IncomingMessage, bot: Bot) -> None:
    email = message.body

    if not check_user_exist(email):
        await bot.answer_message("Wrong email, try again")
        return

    await message.state.fsm.change_state(LoginStates.enter_password, email=email)
    await bot.answer_message("Enter your password")


@fsm.on(LoginStates.enter_password)
async def enter_password(message: IncomingMessage, bot: Bot) -> None:
    email = message.state.fsm_storage.email
    password = message.body

    try:
        login(email, password)
    except IncorrectPasswordError:
        await bot.answer_message("Wrong password, try again")
        return

    await message.state.fsm.drop_state()
    await bot.answer_message("Success!")
```

5. Передайте управление обработчику состояний из любого обработчика сообщений:

```python #fsm_change_state
@collector.command("/login")
async def start_login(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message("Enter your email")
    await message.state.fsm.change_state(LoginStates.enter_email)
```


## Примеры

### Минимальный пример бота с конечным автоматом

```python #fsm_sample
# Здесь и далее будут пропущены импорты и код, не затрагивающий
# непосредственно pybotx_fsm
class FsmStates(Enum):
    EXAMPLE_STATE = auto()


fsm = FSMCollector(FsmStates)


@collector.command("/echo", description="Echo command")
async def help_command(message: IncomingMessage, bot: Bot) -> None:
    await message.state.fsm.change_state(FsmStates.EXAMPLE_STATE)
    await bot.answer_message("Input your text:")


@fsm.on(FsmStates.EXAMPLE_STATE)
async def example_state(message: IncomingMessage, bot: Bot) -> None:
    user_text = message.body
    await message.state.fsm.drop_state()
    await bot.answer_message(f"Your text is {user_text}")


bot = Bot(
    collectors=[
        collector,
    ],
    bot_accounts=[
        BotAccountWithSecret(
            # Не забудьте заменить эти учётные данные на настоящие,
            # когда создадите бота в панели администратора.
            id=UUID("123e4567-e89b-12d3-a456-426655440000"),
            host="cts.example.com",
            secret_key="e29b417773f2feab9dac143ee3da20c5",
        ),
    ],
    middlewares=[
        FSMMiddleware([fsm], state_repo_key="redis_repo"),
    ],
)
```


### Передача данных между состояниями
```python #fsm_storage
@fsm.on(FsmStates.INPUT_FIRST_NAME)
async def input_first_name(message: IncomingMessage, bot: Bot) -> None:
    first_name = message.body
    await message.state.fsm.change_state(
        FsmStates.INPUT_LAST_NAME,
        first_name=first_name,
    )
    await bot.answer_message("Input your last name:")


@fsm.on(FsmStates.INPUT_LAST_NAME)
async def input_last_name(message: IncomingMessage, bot: Bot) -> None:
    first_name = message.state.fsm_storage.first_name
    last_name = message.body
    await message.state.fsm.drop_state()
    await bot.answer_message(f"Hello {first_name} {last_name}!")
```
