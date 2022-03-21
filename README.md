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

Добавьте эту строку в зависимости проекта в `pyproject.toml`:

```toml
botx-fsm = { git = "https://github.com/ExpressApp/pybotx-fsm", rev = "0.2.0" }
```

## Работа с графом состояний

1. Добавьте экземпляр автомата в мидлвари для того, чтобы бот мог использовать его:

``` python
Bot(
    collectors=...,
    bot_accounts=...,
    middlewares=[FSMMiddleware([myfile.fsm], state_repo_key="redis_repo")],
)
```

2. Добавьте в `bot.state.{state_repo_key}` совместимый redis репозиторий:

``` python
bot.state.redis_repo = await RedisRepo.init(...)
```

3. Создайте `enum` для возможных состояний автомата:

``` python
from enum import Enum, auto
from pybotx_fsm import FSMCollector


class LoginStates(Enum):
    enter_email = auto()
    enter_password = auto()


fsm = FSMCollector(LoginStates)
```

4. Создайте обработчики конкретных состояний:

``` python
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

``` python
@collector.handler(command="/login")
async def start_login(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message("Enter your email")
    await fsm.change_state(LoginStates.enter_email)
```
