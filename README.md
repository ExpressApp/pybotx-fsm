# pybotx-fsm

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
botx-fsm = { git = "https://github.com/ExpressApp/pybotx-fsm", rev = "0.1.4" }
```

## Работа с графом состояний

1. Добавьте экземпляр автомата в мидлваре для того, чтобы бот мог использовать его:

```python
# bot.py

bot.add_middleware(
    FSMMiddleware,
    storage=redis_storage,
    fsm_instances=your_fsm_instance,
)
```

2. Создайте `enum` для возможных состояний автомата:

```python
from enum import Enum, auto
from botx_fsm import FSM


class ProcessStates(Enum):
    state1 = auto()
    state2 = auto()

fsm = FSM(ProcessStates)
```

3. Создайте обработчик конкретного состояния:

```python
from botx_fsm import FlowError


@fsm.on(ProcessStates.state1, on_success=ProcessStates.state2)
async def process_state(message: Message, bot: Bot) -> None:
    if message.body == "to_state2":
        await bot.answer_message("going to state2", message)
        return  # No exceptions, going to `on_success` argument state

    await bot.answer_message("wrong text, try again", message)
    raise FlowError  # State haven't changed
```

4. Передайте управление обработчику состояний из любого обработчика сообщений:

```python
# bot.py
@collector.handler(command="/start-process")
async def start_process_fsm(message: Message, bot: Bot) -> None:
    await bot.answer_message("started process", message)
    await fsm.change_state(message, ProcessStates.state1)
```

**Примечание:** В `example/bot` находятся примеры нескольких процессов,
созданных через pybotx-fsm.


## Продвинутая работа с библиотекой

1. В `FlowError` можно передать состояние из enum-а, тогда бот автоматически
   перейдёт в него. Также можно выбросить `FlowError(clear=True)`, чтобы выйти
   из машины состояний (управление будет передано обработчикам сообщений).

2. Помимо аргумента `on_success` для `@fsm.on` можно использовать `on_failure`.
   Тогда выбрасывание `FlowError` без аргументов будет переводить в это
   состояние.

   Также есть состояние `unset`, которое позволяет выйти из
   выполнения конечного автомата:

```python
from botx_fsm import unset


@fsm.on(ProcessStates.state2, on_success=unset, on_failure=ProcessStates.state1)
async def process_state(message: Message, bot: Bot) -> None:
    ...
```

3. Чтобы передать данные в следующее состояние, необходимо явно вызвать процесс
   перехода и распаковать данные в следующем состоянии.

```python
from botx_fsm import StateExtractor


@collector.hidden(command="/start-process", name="start-process")
async def start_process(message: Message, bot: Bot) -> None:
    await fsm.change_state(message, ProcessStates.state1, foo="bar")


@fsm.on(ProcessStates.state2, on_success=unset)
async def get_additional_data(
    message: Message, bot: Bot, foo: str = Depends(StateExtractor.foo)
) -> None:
    ...
```
