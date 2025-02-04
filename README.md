# Описание лабортаорной работы №4

Этот код реализует парсинг регекса с захватом групп и опережающими проверками. Также реализовано построение КС-грамматики.


## Запуск программы

```bash
python main.py
```

## Пример работы программы 

```bash
Проверка: (a|b)c
Типы операторов и токенов:
{'type': 'Operator', 'value': '('}
{'type': 'Symbol', 'value': 'a'}
{'type': 'Operator', 'value': '|'}
{'type': 'Symbol', 'value': 'b'}
{'type': 'Operator', 'value': ')'}
{'type': 'Symbol', 'value': 'c'}
{'type': 'EndOfString', 'value': '$'}

{'type': 'CaptureStart', 'index': 1}
{'type': 'CaptureEnd', 'index': 1}

Регулярное выражение корректно.

Дерево AST:
Concatenation
├── Capture
│   ├── Alternation
│   │   ├── Symbol
│   │   └── Symbol
└── Symbol

Грамматика для (a|b)c:
Типы операторов и токенов:
{'type': 'Operator', 'value': '('}
{'type': 'Symbol', 'value': 'a'}
{'type': 'Operator', 'value': '|'}
{'type': 'Symbol', 'value': 'b'}
{'type': 'Operator', 'value': ')'}
{'type': 'Symbol', 'value': 'c'}
{'type': 'EndOfString', 'value': '$'}

{'type': 'CaptureStart', 'index': 1}
{'type': 'CaptureEnd', 'index': 1}
S = N_5 | ε
T_1 = a
T_2 = b
N_3 = T_1 | T_2
T_4 = c
N_5 = N_3  T_4
```
