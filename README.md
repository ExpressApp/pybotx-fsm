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

## Примеры

### Минимальный пример бота с конечным автоматом

```python
from enum import Enum, auto
from uuid import UUID

from pybotx import Bot, BotAccountWithSecret, HandlerCollector, IncomingMessage

from pybotx_fsm import FSMCollector, FSMMiddleware


class FsmStates(Enum):
    EXAMPLE_STATE = auto()


collector = HandlerCollector()
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
```python
from enum import Enum, auto

from pybotx import Bot, HandlerCollector, IncomingMessage

from pybotx_fsm import FSMCollector


class FsmStates(Enum):
    INPUT_FIRST_NAME = auto()
    INPUT_LAST_NAME = auto()


collector = HandlerCollector()
fsm = FSMCollector(FsmStates)


@collector.command("/login", description="Login command")
async def help_command(message: IncomingMessage, bot: Bot) -> None:
    await message.state.fsm.change_state(FsmStates.INPUT_FIRST_NAME)
    await bot.answer_message("Input your first name:")


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
