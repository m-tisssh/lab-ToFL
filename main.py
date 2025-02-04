from graphviz import Digraph

class LR0Parser:
    def __init__(self, grammar_rules):
        # Сохраняем правила грамматики и инициализируем вспомогательные структуры
        self.grammar_rules = grammar_rules
        self.start_symbol = grammar_rules[0].split("->")[0].strip()  # Определяем начальный символ
        self.rules = {}            # Словарь правил вида {нетерминал: [правила]}
        self.items = []            # Множества ситуаций (LR0 items)
        self.transitions = {}      # Переходы между состояниями
        self.reductions = {}       # Сведения о свертках (reduce)             
        self.action_table = {}     
        self.goto_table = {}       
        self._parse_grammar()

    def _parse_grammar(self):
        # разбираем каждое правило грамматики
        for rule in self.grammar_rules:
            left, right = rule.split('->')
            left = left.strip()
            right = tuple(right.strip().split())
            if left not in self.rules:
                self.rules[left] = []
            self.rules[left].append(right)  # добавляем правило в словарь rules

    def _closure(self, item_set):
        # находим замыкание множества ситуаций
        closure = set(item_set)  # изначально включаем переданные ситуации !
        while True:
            new_items = set()
            for item in closure:
                left_side, right_side, dot_pos = item
                if dot_pos < len(right_side):  # если точка не в конце
                    next_symbol = right_side[dot_pos]
                    if next_symbol in self.rules:  # если это нетерминал, то добавляем его правило
                        for production in self.rules[next_symbol]:
                            new_item = (next_symbol, production, 0)
                            if new_item not in closure:
                                new_items.add(new_item)
            if not new_items:  # если нет новых ситуаций для добавления, выходим из цикла
                break
            closure.update(new_items)  # обновление замыкания
        return closure

    def _goto(self, item_set, symbol):
        new_items = set()
        for item in item_set:
            left_side, right_side, dot_pos = item
            if dot_pos < len(right_side) and right_side[dot_pos] == symbol:  # ессли точка перед символом
                new_item = (left_side, right_side, dot_pos + 1)  # перемещаем точку вправо
                new_items.add(new_item)
        return self._closure(new_items)  # возвращаем замыкание для новых ситуаций

    def _build_lr0_items(self):
        # добавляем стартовое правило S' -> S !
        start_rule = (self.start_symbol + "'", (self.start_symbol,), 0)
        self.rules[self.start_symbol + "'"] = [(self.start_symbol,)]  # обновляем словарь правил

        # начальное замыкание для стартового правила
        initial_closure = self._closure([start_rule])
        self.items.append(initial_closure)

        i = 0
        while i < len(self.items):  # для каждого множества ситуаций
            item_set = self.items[i]
            for symbol in set(sym for item in item_set for sym in item[1]):  
                new_item_set = self._goto(item_set, symbol)
                if new_item_set and new_item_set not in self.items:
                    # добавляем новое множество ситуаций, если оно уникально
                    self.items.append(new_item_set)
                    self.transitions[(i, symbol)] = len(self.items) - 1
                elif new_item_set:
                    # если множество уже существует, сохраняем его индекс
                    self.transitions[(i, symbol)] = self.items.index(new_item_set)

            for item in item_set:
                left_side, right_side, dot_pos = item
                if dot_pos == len(right_side):  # если точка в конце, это свертка
                    if i not in self.reductions:
                        self.reductions[i] = []  # список редукций
                    self.reductions[i].append((left_side, right_side))  # добавляем редукцию
            i += 1


    def _build_action_goto_table(self):
        """Строит таблицы Action/Goto"""
        print("Номера правил для reduce:")
        rule_number = 1
        rule_map = {}  # для сопоставления (left, right) с номерами правил
        for left, right_list in self.rules.items():
            for right in right_list:
                rule_map[(left, right)] = rule_number
                print(f"{rule_number}: {left} -> {' '.join(right)}")
                rule_number += 1

        self.action_table = {i: {} for i in range(len(self.items))}
        self.goto_table = {i: {} for i in range(len(self.items))}

        # заполнение таблицы action-goto
        for (state, symbol), next_state in self.transitions.items():
            if symbol.islower():  # то есть терминал
                if symbol in self.action_table[state]:
                    if not self.action_table[state][symbol].startswith("shift"):
                        print(f"Конфликт перенос-свертка в состоянии {state} и символе '{symbol}'. Выбираем shift.")
                    self.action_table[state][symbol] = f"shift {next_state}"
                else:
                    self.action_table[state][symbol] = f"shift {next_state}"
            else:  # случаи для нетерминала
                self.goto_table[state][symbol] = next_state

        for state, reductions in self.reductions.items():
            for left, right in reductions:
                rule_number = rule_map[(left, right)]  # находим номер правила
                for symbol in ['a', 'b', 'c', '$']:  
                    if symbol in self.action_table[state]:
                        if not self.action_table[state][symbol].startswith("reduce"):
                            print(f"Конфликт свертка-свертка в состоянии {state} и символе '{symbol}'. Выбираем первое reduce.")
                        continue
                    self.action_table[state][symbol] = f"reduce {rule_number}"

        for state, item_set in enumerate(self.items):
            for item in item_set:
                left_side, right_side, dot_pos = item
                if left_side == self.start_symbol + "'" and dot_pos == len(right_side):
                    self.action_table[state] = {'$': "accept"}

    def print_action_goto_table(self):
        print(f"{'State':<8}| {'Action':<40}| {'Goto':<20}")
        print('-' * 80)
        for state in range(len(self.items)):
            actions = ", ".join(f"{k}: {v}" for k, v in self.action_table[state].items())
            gotos = ", ".join(f"{k}: {v}" for k, v in self.goto_table[state].items())
            print(f"{state:<8}| {actions:<40}| {gotos:<20}")

    def print_grammar(self):
        # выводим правила грамматики
        for left, right_side_list in self.rules.items():
            for right in right_side_list:
                print(f"{left} -> {' '.join(right)}")

    def print_states(self):
        # выводим множества состояний
        for idx, item_set in enumerate(self.items):
            print(f"Состояние {idx}:")
            for item in item_set:
                left_side, right_side, dot_pos = item
                print(f"  {left_side} -> {' '.join(right_side[:dot_pos])} • {' '.join(right_side[dot_pos:])}")
            if idx in self.reductions:
                # все возможные свертки для данного состояния
                for left, right in self.reductions[idx]:
                    print(f"  Reduce by: {left} -> {' '.join(right)}")
            print()

    def print_transitions(self):
        # переходы между состояниями
        for (state, symbol), next_state in self.transitions.items():
            if next_state is not None:
                print(f"({state}, '{symbol}', {next_state})")

# Класс для визуализации автомата, соответствующего парсеру LR(0)
class AutomatonVisualizer:
    def __init__(self, parser):
        self.parser = parser
        self.graph = Digraph(format='png')

    def _format_state(self, idx, items):
        """Форматируем содержимое состояния."""
        state_label = [f"Состояние {idx}"]
        for item in items:
            left, right, dot = item
            right_with_dot = list(right[:dot]) + ['•'] + list(right[dot:])
            state_label.append(f"{left} -> {' '.join(right_with_dot)}")
        if idx in self.parser.reductions:
            for reduction in self.parser.reductions[idx]:
                left = reduction[0]
                right = reduction[1] if len(reduction) > 1 else ()
                state_label.append(f"Reduce by: {left} -> {' '.join(right)}")
        return "\n".join(state_label)


    def build_graph(self):
        for idx, item_set in enumerate(self.parser.items):
            label = self._format_state(idx, item_set)
            self.graph.node(str(idx), label, shape='ellipse')

        for (state, symbol), next_state in self.parser.transitions.items():
            self.graph.edge(str(state), str(next_state), label=symbol)

    def render(self, filename="lr0_automaton"):
        """Визуализация графа"""
        self.build_graph()
        self.graph.render(filename, cleanup=True)


class PDAVisualizer:
    def __init__(self, parser):
        self.parser = parser
        self.graph = Digraph(format='png')
        self.added_transitions = set()  

    def _add_state(self, state_id, label, is_doublecircle=False):
        shape = "doublecircle" if is_doublecircle else "ellipse"
        self.graph.node(state_id, label=label, shape=shape)

    def _add_transition(self, from_state, to_state, label):
        transition_key = (from_state, to_state, label)
        if transition_key not in self.added_transitions:
            self.graph.edge(from_state, to_state, label=label)
            self.added_transitions.add(transition_key)

    def build_pda(self):
        """Создание PDA на основе LR(0) автомата."""
        # Добавляем состояния DFA
        for state_idx in range(len(self.parser.items)):
            self._add_state(str(state_idx), str(state_idx))

        # Добавляем сдвиги (shift) и переходы
        for (state, symbol), next_state in self.parser.transitions.items():
            if not symbol.islower():
                continue
            action = f"{symbol}, x / S_{next_state}x"
            self._add_transition(str(state), str(next_state), action)

        # добавляем свертки (reduce)
        for state, reductions in self.parser.reductions.items():
            unique_reductions = list(set(reductions))
            if unique_reductions:
                # берем только первое правило для обработки
                selected_reduction = unique_reductions[0]
                left, right = selected_reduction
                reduce_states = []
                for i, sym in enumerate(right):
                    reduce_state = f"reduce_{left}->{''.join(right)} ({i})"
                    reduce_states.append(reduce_state)
                    self._add_state(reduce_state, reduce_state)

                self._add_transition(str(state), reduce_states[0], f"ε, x / ε")

                # переходы между Reduce-состояниями
                for i in range(len(reduce_states) - 1):
                    self._add_transition(reduce_states[i], reduce_states[i + 1], "ε, x / ε")

                # Возврат после Reduce
                for target_state in range(len(self.parser.items)):
                    if (target_state, left) in self.parser.transitions:
                        next_state = self.parser.transitions[(target_state, left)]
                        self._add_transition(
                            reduce_states[-1],
                            str(next_state),
                            f"ε, S{target_state} / S{next_state}S{target_state}"
                        )

        # Добавляем начальное состояние
        self._add_state("start", "", False)
        self._add_transition("start", "0", "start")

        # Добавляем состояние accept
        for state, actions in self.parser.action_table.items():
            if "$" in actions and actions["$"] == "accept":
                self._add_state(str(state), str(state), True)

    def render(self, filename="pda_automaton"):
        """Рендерит и сохраняет PDA."""
        self.build_pda()
        self.graph.render(filename, cleanup=True)


grammar_rules = [
    "S -> a S b",
    "S -> a A",
    "S -> c",
    "A -> a A",
    "A -> c c"
]

parser = LR0Parser(grammar_rules)

print("Грамматика:")
parser.print_grammar()

parser._build_lr0_items()

print("\nСостояния:")
parser.print_states()

parser._build_action_goto_table()
print("\nУправляющая таблица:")
parser.print_action_goto_table()

visualizer = AutomatonVisualizer(parser)
visualizer.render("lr0_automaton")

# Визуализация PDA
pda_visualizer = PDAVisualizer(parser)
pda_visualizer.render("pda_automaton")
