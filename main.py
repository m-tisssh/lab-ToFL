import requests
import json
from collections import defaultdict
from flask import Flask, request, jsonify
from save_table import save_table_as_image

app = Flask(__name__)

class LStarAlgorithm:
    def __init__(self, alphabet, max_depth, server_mode=False, server_url="http://localhost:8095"):
        self.alphabet = alphabet
        self.S = [''] 
        self.E = ['']  
        self.table = defaultdict(dict) 
        self.checked_words = []  
        self.max_depth = max_depth
        self.server_mode = server_mode
        self.server_url = server_url 

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

    def manual_membership(self, word):
        for checked_word, result in self.checked_words:
            if checked_word == word:
                return result
        
        result = input(f"Is \"{word}\" part of the language? (+/-): ").strip().lower() == "+"
        self.checked_words.append((word, result))
        return result

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

    def manual_equivalence(self):
        self.display_observation_table()  
        is_equivalent = input("Is it equivalent (yes/no)? ").strip().lower() == "yes"
        if is_equivalent:
            save_table_as_image(self)  
            return True, ""
        else:
            counter_example = input("Enter counter example: ")
            return False, counter_example

    def update_table(self):
        new_words = {s + a for s in self.S for a in self.alphabet if len(s + a) <= self.max_depth}
        all_words = set(self.S) | new_words

        if "" not in all_words:
            all_words.add("")  

        for word in all_words:
            for e in self.E:
                word_representation = word if word else "ε"
                if word not in self.table or e not in self.table[word]:
                    self.table[word][e] = self.check_membership(word + e)
                    print(f"Updated table for '{word_representation}' with suffix '{e}'")

    def is_closed(self):
        upper_rows = [self.table[s] for s in self.S]
        low_s = [s + a for s in self.S for a in self.alphabet if s + a not in self.S and len(s + a) <= self.max_depth]
        for s in low_s:
            if self.table[s] not in upper_rows:
                return False, s
        return True, None

    def is_consistent(self):
        for s1 in self.S:
            for s2 in self.S:
                if s1 != s2 and self.table[s1] == self.table[s2]:
                    for a in self.alphabet:
                        if self.table[s1 + a] != self.table[s2 + a]:
                            for e in self.E:
                                if self.table[s1 + a].get(e) != self.table[s2 + a].get(e):
                                    return False, a + e
        return True, None
    
    def add_distinguishing_suffixes(self, inconsistency):
        for suffix in self.alphabet:
            candidate_suffix = inconsistency + suffix
            if candidate_suffix not in self.E:
                print(f"Adding distinguishing suffix: {candidate_suffix}")
                self.E.append(candidate_suffix)

    def display_observation_table(self):
        header = f"{'S/E'.center(10)} | " + " | ".join(e.center(10) for e in self.E)
        print(header)
        print("-" * len(header))

        for s in self.S:
            row_prefix = s if s else "ε"
            row = f"{row_prefix.center(10)} | " + " | ".join(str(self.table[s].get(e, '')).center(10) for e in self.E)
            print(row)

        print("=" * len(header))

        low_s = [s + a for s in self.S for a in self.alphabet if s + a not in self.S]
        for s in low_s:
            row_prefix = s if s else "ε"
            row = f"{row_prefix.center(10)} | " + " | ".join(str(self.table[s].get(e, '')).center(10) for e in self.E)
            print(row)
        print("-" * len(header))

        save_table_as_image(self) 

    def run(self):
        self.update_table()

        while True:
            is_closed, s = self.is_closed()
            if not is_closed:
                self.S.append(s)
                self.update_table()
                continue

            is_consistent, ae = self.is_consistent()
            if not is_consistent:
                self.add_distinguishing_suffixes(ae)
                self.update_table()
                continue

            is_equivalent, counter_example = self.check_equivalence()
            if not is_equivalent:
                for i in range(len(counter_example)):
                    suffix = counter_example[i:]
                    if suffix not in self.E:
                        print(f"Adding counterexample suffix: {suffix}")
                        self.E.append(suffix)
                self.update_table()
                continue

            return self.display_observation_table()

def read_parameters(filename):
    with open(filename, 'r') as file:
        params = json.load(file)
    max_depth = params["max_depth"]
    exit_count = params["exit_count"]
    return max_depth, exit_count

def lstar(alphabet):
    max_depth, exit_count = read_parameters("parameters.json")
    server_mode = input("Use server mode? (yes/no): ").lower() == "yes"
    lstar_algorithm = LStarAlgorithm(alphabet, max_depth, server_mode)
    lstar_algorithm.run()

if __name__ == "__main__":
    lstar({'L', 'R'})
