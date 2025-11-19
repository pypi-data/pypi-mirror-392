# Gambit Platform Integration SDK

[![PyPI version](https://badge.fury.io/py/gambit-sdk.svg)](https://badge.fury.io/py/gambit-sdk)
[![Python Version](https://img.shields.io/pypi/pyversions/gambit-sdk)](https://pypi.org/project/gambit-sdk/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

**Gambit SDK** — это официальный инструментарий для разработки **Адаптеров Платформ** для системы автоматизации Gambit. Этот SDK предоставляет все необходимые контракты, схемы данных и утилиты, чтобы вы могли интегрировать любую образовательную платформу с ядром Gambit.

## Философия

SDK спроектирован по принципу **"Адаптер как Плагин"**. Это означает, что вы, как разработчик, фокусируетесь исключительно на бизнес-логике взаимодействия с конкретной платформой (реверс-инжиниринг её API, парсинг данных). Всю сложную инфраструктурную работу (взаимодействие с RabbitMQ, управление состоянием, логирование) берет на себя хост-система Gambit (`AdapterRunner`), которая будет запускать ваш код.

Ваша задача — реализовать простой и понятный интерфейс (`BaseAdapter`), который работает как "драйвер" для целевой платформы.

## Установка

Для начала работы установите пакет с помощью pip:

```bash
pip install gambit-sdk
```

## Быстрый старт

Вот минимальный пример рабочего адаптера. Ваша задача — унаследовать класс `BaseAdapter` и реализовать его абстрактные методы.

```python
# my_platform_adapter.py

from datetime import datetime
from httpx import AsyncClient

from gambit_sdk import (
    BaseAdapter,
    ExerciseType,
    UnifiedAssignmentPreview,
    UnifiedAssignmentDetails,
    UnifiedExercise,
    UnifiedGrade,
    UnifiedSolution,
    ChoiceStructure,
    StringAnswer,
)

class MyPlatformAdapter(BaseAdapter):
    """
    Адаптер для вымышленной платформы "MyPlatform".
    """
    def __init__(self, session: AsyncClient) -> None:
        # SDK передает уже сконфигурированный HTTP-клиент
        super().__init__(session)
        self.base_url = "https://api.my-platform.com"

    async def login(self, username: str, password: str) -> None:
        """Логинимся на платформе и сохраняем токен/cookie в сессию."""
        response = await self.session.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        # httpx автоматически сохранит cookie из ответа в self.session

    async def get_assignment_previews(self) -> list[UnifiedAssignmentPreview]:
        """Получаем легкий список заданий."""
        response = await self.session.get(f"{self.base_url}/homeworks")
        response.raise_for_status()
        
        previews = []
        for hw_data in response.json()["data"]:
            preview = UnifiedAssignmentPreview(
                platform_assignment_id=str(hw_data["id"]),
                title=hw_data["title"],
                assigned_date=datetime.fromisoformat(hw_data["assigned_to_day"]),
                deadline=datetime.fromisoformat(hw_data["deadline_at"]),
                context_data={"details_url": hw_data["_links"]["details"]}
            )
            previews.append(preview)
        return previews

    async def get_assignment_details(self, preview: UnifiedAssignmentPreview) -> UnifiedAssignmentDetails:
        """Получаем полную информацию о задании по его превью."""
        details_url = preview.context_data["details_url"]
        response = await self.session.get(details_url)
        response.raise_for_status()
        details_data = response.json()["data"]

        exercises = [
            UnifiedExercise(
                platform_exercise_id=str(ex["id"]),
                type=ExerciseType.INPUT_STRING, # Здесь должна быть логика маппинга
                question=ex["question_text"],
                max_score=float(ex["points"]),
                structure=None # Для простых типов структура не нужна
            ) for ex in details_data["exercises"]
        ]
            
        return UnifiedAssignmentDetails(
            platform_assignment_id=preview.platform_assignment_id,
            title=preview.title,
            assigned_date=preview.assigned_date,
            deadline=preview.deadline,
            description=details_data.get("description"),
            exercises=exercises
        )

    async def submit_solution(self, details: UnifiedAssignmentDetails, solution: UnifiedSolution) -> UnifiedGrade | None:
        """Отправляем решение и, если возможно, сразу получаем оценку."""
        # 1. Конвертируем UnifiedSolution в формат, понятный платформе
        platform_payload = {
            "assignment_id": details.platform_assignment_id,
            "answers": [
                {"question_id": ans.platform_exercise_id, "value": ans.answer.value}
                for ans in solution.answers if isinstance(ans.answer, StringAnswer)
            ]
        }
        
        # 2. Отправляем запрос
        response = await self.session.post(
            f"{self.base_url}/homeworks/{details.platform_assignment_id}/submit",
            json=platform_payload
        )
        response.raise_for_status()
        
        # 3. Если платформа сразу возвращает оценку, парсим и возвращаем ее
        grade_data = response.json().get("grade")
        if grade_data:
            return UnifiedGrade(
                platform_assignment_id=details.platform_assignment_id,
                score=float(grade_data["score"]),
                max_score=float(grade_data["max_score"]),
                is_passed=grade_data["is_passed"]
            )
        return None

    async def get_grade(self, details: UnifiedAssignmentDetails) -> UnifiedGrade | None:
        """Отдельно запрашиваем оценку для ранее сданного задания."""
        response = await self.session.get(f"{self.base_url}/homeworks/{details.platform_assignment_id}/grade")
        if response.status_code == 404:
            return None # Оценка еще не выставлена
        response.raise_for_status()
        
        grade_data = response.json()["data"]
        return UnifiedGrade(
            platform_assignment_id=details.platform_assignment_id,
            score=float(grade_data["score"]),
            max_score=float(grade_data["max_score"]),
            is_passed=grade_data["is_passed"]
        )
```

## Воркфлоу взаимодействия

Хост-система `AdapterRunner` будет взаимодействовать с вашим адаптером в следующем порядке:

1.  **`login(username, password)`**: Вызывается один раз для аутентификации и настройки сессии.
2.  **`get_assignment_previews()`**: Вызывается периодически для получения списка доступных заданий. Этот метод должен быть максимально быстрым и легким.
3.  **`get_assignment_details(preview)`**: Вызывается для каждого нового задания из списка, полученного на шаге 2. Здесь можно делать более "тяжелые" запросы для получения полной информации.
4.  **`submit_solution(details, solution)`**: Вызывается, когда ядро Gambit сгенерировало решение. Ваша задача — правильно отформатировать и отправить его на платформу.
5.  **`get_grade(details)`**: Вызывается после отправки решения для получения итоговой оценки, если `submit_solution` не вернул ее сразу.

## Справочник по API

### `BaseAdapter`
Абстрактный класс, определяющий контракт для всех адаптеров.

- `__init__(self, session: AsyncClient)`: Конструктор. Принимает готовый `httpx.AsyncClient`.
- `login(self, username, password)`: Абстрактный метод для аутентификации.
- `get_assignment_previews(self)`: Абстрактный метод. Должен вернуть `list[UnifiedAssignmentPreview]`.
- `get_assignment_details(self, preview)`: Абстрактный метод. Принимает `UnifiedAssignmentPreview` и должен вернуть `UnifiedAssignmentDetails`.
- `submit_solution(self, details, solution)`: Абстрактный метод. Принимает `UnifiedAssignmentDetails` и `UnifiedSolution`, может вернуть `UnifiedGrade`.
- `get_grade(self, details)`: Абстрактный метод. Принимает `UnifiedAssignmentDetails`, должен вернуть `UnifiedGrade`.

### `AssignmentType` (Enum)
Перечисление всех унифицированных типов упражнений.
- `CHOICE_SINGLE`: Выбор одного варианта.
- `CHOICE_MULTIPLE`: Выбор нескольких вариантов.
- `INPUT_STRING`: Ввод короткой строки.
- `INPUT_TEXT`: Ввод длинного текста.
- `TEXT_FILE`: Загрузка файла с текстовым содержимым.
- `MATCHING_PAIRS`: Сопоставление пар.
- `SEQUENCE_ORDERING`: Установление последовательности.
- `UNSUPPORTED`: Неподдерживаемый тип.

### Схемы данных

Все схемы данных являются Pydantic-моделями и обеспечивают строгую типизацию.

- **`UnifiedAssignmentPreview`**: Легковесное представление задания. Ключевое поле — `context_data`, "черный ящик" для передачи данных между `get_previews` и `get_details`.
- **`UnifiedAssignmentDetails`**: Полное представление задания со списком упражнений (`exercises: list[UnifiedExercise]`).
- **`UnifiedExercise`**: Одно упражнение. Ключевое поле — `structure`, строго типизированная модель (`ChoiceStructure`, `MatchingStructure` и т.д.), описывающая варианты ответов или элементы для сопоставления.
- **`UnifiedSolution`**: Полное решение, состоящее из списка `UnifiedSolutionExercise`.
- **`UnifiedSolutionExercise`**: Ответ на одно упражнение. Ключевое поле — `answer`, строго типизированная модель (`ChoiceAnswer`, `StringAnswer` и т.д.).
- **`UnifiedGrade`**: Итоговая оценка. Содержит `score`, `max_score`, `is_passed` и опционально `correct_answers`.

## Содействие

На данный момент проект находится в стадии активной разработки. Если вы заинтересованы в создании адаптера для новой платформы или нашли ошибку в SDK, пожалуйста, создайте Issue в [нашем репозитории](https://github.com/brilliant-gambit/gambit-sdk/issues).

## Лицензия

Использование данного SDK регулируется **проприетарной лицензией**. Пожалуйста, ознакомьтесь с полным текстом в файле [LICENSE](LICENSE) перед использованием. Ключевое ограничение: SDK может быть использован **исключительно** для создания адаптеров для платформы Gambit.