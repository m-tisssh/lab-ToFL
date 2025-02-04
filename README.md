# Описание лабортаорной работы №3

Этот код реализует **построение PDA на основе LR(0)**  

## Запуск 

Для запуска выполните следующую команду:
```bash
python main.py
```

## Описание работы программы*

Сначала вводятся правила грамматики в файл main.py. Пример:
```python
grammar_rules = [
    "S -> a S b",
    "S -> a A",
    "S -> c",
    "A -> a A",
    "A -> c c"
]
```
Затем выполняется класс **LR0Parser**, который парсит грамматику LR(0) и выводит состояния в терминал. Также выводится управляющая таблица ACTION-GOTO.

За визуализацию автомата, соответствующего парсеру LR(0), отвечает класс **AutomatonVisualizer**. Результат работы сохраняется в файл lr0_automaton.png

Построение PDA на основе LR(0) выполняется классом **PDAVisualizer**. Результат работы сохраняется в файл pda_automaton.png


## Тестирование
```bash
Грамматика:
S -> a S b
S -> a A
S -> c
A -> a A
A -> c c

Состояния:
Состояние 0:
  S ->  • a A
  S' ->  • S
  S ->  • a S b
  S ->  • c

Состояние 1:
  S ->  • a A
  S -> a • S b
  A ->  • a A
  S -> a • A
  S ->  • c
  A ->  • c c
  S ->  • a S b

Состояние 2:
  S -> c • 
  Reduce by: S -> c

Состояние 3:
  S' -> S • 
  Reduce by: S' -> S

Состояние 4:
  S -> a A • 
  Reduce by: S -> a A

Состояние 5:
  S -> a • S b
  S -> a • A
  A ->  • c c
  A ->  • a A
  S ->  • a S b
  S ->  • a A
  S ->  • c
  A -> a • A

Состояние 6:
  S -> c • 
  A -> c • c
  Reduce by: S -> c

Состояние 7:
  S -> a S • b

Состояние 8:
  S -> a A • 
  A -> a A • 
  Reduce by: S -> a A
  Reduce by: A -> a A

Состояние 9:
  A -> c c • 
  Reduce by: A -> c c

Состояние 10:
  S -> a S b • 
  Reduce by: S -> a S b

Номера правил для reduce:
1: S -> a S b
2: S -> a A
3: S -> c
4: A -> a A
5: A -> c c
6: S' -> S
Конфликт свертка-свертка в состоянии 6 и символе 'c'. Выбираем первое reduce.

Управляющая таблица:
State   | Action                                  | Goto                
--------------------------------------------------------------------------------
0       | a: shift 1, c: shift 2                  | S: 3                
1       | a: shift 5, c: shift 6                  | A: 4, S: 7          
2       | a: reduce 3, b: reduce 3, c: reduce 3, $: reduce 3|                     
3       | $: accept                               |                     
4       | a: reduce 2, b: reduce 2, c: reduce 2, $: reduce 2|                     
5       | a: shift 5, c: shift 6                  | A: 8, S: 7          
6       | c: shift 9, a: reduce 3, b: reduce 3, $: reduce 3|                     
7       | b: shift 10                             |                     
8       | a: reduce 2, b: reduce 2, c: reduce 2, $: reduce 2|                     
9       | a: reduce 5, b: reduce 5, c: reduce 5, $: reduce 5|                     
10      | a: reduce 1, b: reduce 1, c: reduce 1, $: reduce 1|
```

