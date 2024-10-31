# Описание лабортаорной работы №2

Этот код реализует **L\*-алгоритм** для построения полного описания конечного автомата. L\*-алгоритм применяется для построения автомата по языку, который распознается "МАТ". В свою очередь "МАТ" генерирует случайный автомат, соответствующий задаче, и реагирует на запросы об эквивалентности и включении.


## Вариация L* - осторожный L*

Для оптимизации алгоритма был использован осторожный L\*.

Осторожный L\*-алгоритм — это модификация алгоритма L\*, который добавляет больше различающих суффиксов для получения корректного автомата. 

Если находятся противоречия при проверки эквивалентности, алгоритм добавляет различающие суффиксы и обновляет таблицу, пока не будет достигнута эквивалентность или пока не будут исчерпаны все варианты. 


## Запуск 

Для запуска алгоритма выполните следующую команду:
```bash
python main.py
```


## Тестирование

Угадыватель тестировался на МАТ, реализующий планарный лабиринт (для тестирования был взят МАТ Никиты Нащёкина, ИУ9-52Б)

L\*-алгоритм взаимодействует с сервером для выполнения двух типов запросов:
1. **Запрос проверки принадлежности слова языку (check_membership)** — для определения, является ли конкретное слово частью целевого языка.
2. **Запрос проверки эквивалентности (check_equivalence)** — для проверки, совпадает ли гипотеза автомата с целевой системой или есть различия.


#### Пример вывода из терминала
```bash
Request to checkWord for 'RRRLLRLR': 200, b'{"response":false}\n'
Updated table for 'RRRLLR' with suffix 'LR'
Request to checkWord for 'RRRLLRR': 200, b'{"response":false}\n'
Updated table for 'RRRLLR' with suffix 'R'
Request to checkTable: 200, b'{"response":"RLLRLRR","type":true}\n'
Counterexample found: RLLRLRR
Adding counterexample suffix: RLLRLRR
Adding counterexample suffix: LLRLRR
Adding counterexample suffix: LRLRR
Adding counterexample suffix: RLRR
Adding counterexample suffix: LRR
Adding counterexample suffix: RR
Request to checkWord for 'RLLRLRR': 200, b'{"response":true}\n'
```


## Режимы работы

Алгоритм поддерживает два режима работы:
1. **Автоматический режим с сервером** (при `server_mode=True`) — отправка запросов на сервер для проверки принадлежности и эквивалентности.
2. **Ручной режим** — если сервер отключен, алгоритм может работать в ручном режиме, где ответы должны быть даны пользователем, проверяя гипотезы самостоятельно.

Выбор режима осуществляется через терминал.


## Файл `parameters.json`

Файл `parameters.json` содержит основные параметры для запуска алгоритма:
- `max_depth` — максимальная глубина слов, проверяемых в таблице наблюдений.
- `exit_count` — максимальное число итераций перед выходом из цикла.


## Работа с МАТ 
Если мы работаем в автоматическом режиме с сервером, то выполняются функции:
```bash
def check_membership(self, word):
        if self.server_mode:
            try:
                word_to_send = word if word else "ε"
                payload = {"word": word_to_send}
                response = requests.post(f"{self.server_url}/checkWord", json=payload)
                print(f"Request to checkWord for '{word_to_send}': {response.status_code}, {response.content}")
                response.raise_for_status()
                response_data = response.json()
                return response_data['response']
            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")
                print(f"Response content: {response.content}")
                return False
            except ValueError as json_err:
                print(f"JSON decode error: {json_err}")
                print(f"Response content: {response.content}")
                return False
        else:
            return self.manual_membership(word)

def check_equivalence(self):
        main_prefixes = " ".join("ε" if s == "" else s for s in self.S)
        non_main_prefixes = " ".join("ε" if s == "" else s for s in [s + a for s in self.S for a in self.alphabet if s + a not in self.S])
        suffixes = " ".join("ε" if e == "" else e for e in self.E)
        
        table_values = []
        for s in self.S + [s + a for s in self.S for a in self.alphabet if s + a not in self.S]:
            row = [self.table.get(s, {}).get(e, 0) for e in self.E]
            table_values.extend(row)
        table_as_string = " ".join(str(int(value)) for value in table_values)

        if self.server_mode:
            payload = {
                "main_prefixes": main_prefixes,
                "non_main_prefixes": non_main_prefixes,
                "suffixes": suffixes,
                "table": table_as_string
            }

            response = requests.post(f"{self.server_url}/checkTable", json=payload)
            print(f"Request to checkTable: {response.status_code}, {response.content}")
            response.raise_for_status()

            response_data = response.json()
            counterexample_type = response_data.get("type")
            counterexample_word = response_data.get("response")

            if counterexample_type is None:
                print("Languages are equivalent.")
                save_table_as_image(self)
                return True, ""
            else:
                print(f"Counterexample found: {counterexample_word}")
                return False, counterexample_word
        else:
            return self.manual_equivalence()
```

Если мы работаем в ручном режиме, то выполняются следующие функции:
```bash
def manual_membership(self, word):
        for checked_word, result in self.checked_words:
            if checked_word == word:
                return result
        
        result = input(f"Is \"{word}\" part of the language? (+/-): ").strip().lower() == "+"
        self.checked_words.append((word, result))
        return result

def manual_equivalence(self):
        self.display_observation_table()  
        is_equivalent = input("Is it equivalent (yes/no)? ").strip().lower() == "yes"
        if is_equivalent:
            save_table_as_image(self)  
            return True, ""
        else:
            counter_example = input("Enter counter example: ")
            return False, counter_example
```

## Вывод данных

Данные таблицы наблюдений выводятся в консоль в структурированном виде после каждой итерации. Если эквивалентность достигнута, финальная таблица сохраняется с помощью функции `save_table_as_image`, которая сохраняет таблицу в виде изображения. Это сделано для улучшения читаемости заполненной таблицы.

