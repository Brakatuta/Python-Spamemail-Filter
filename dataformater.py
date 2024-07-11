import csv

# csv datei als dictionary laden (-> ermöglich wesentlich leichtere Interaktion mit dem Listen Kontent)
def get_data_from_csv(csv_file_dir : str):
    data_list = []
    with open(csv_file_dir, 'r') as file:
        csv_reader = csv.DictReader(file)
        data_list = [row for row in csv_reader]
    return data_list

# "Aufräumen" der csv-daten
def cleanup_data_list(data_list : list, values_to_correct : dict) -> list:
    for index, row in enumerate(data_list):
        data_list[index] = cleanup_dictionary(row, values_to_correct) # jede Zeile des Datensatzes berichtigen
    return data_list

# "Löschen von unnötigen charactern bei Parametern (z.B.: Lehrzeichen), Ändern von diversen Values in für den PC leichter verständliche (+ ermöglicht bessere Interaktion)"
# Bsp.: "Nein" -> False, "Ja" -> True
def cleanup_dictionary(dictionary : dict, values_to_correct : dict) -> dict:
    n_dictionary = {}
    for key in dictionary.keys():
        value = dictionary[key]
        if type(key) is str and key[0] == ' ':
            key = key.replace(' ', '', 1)
        if values_to_correct.keys().__contains__(value):
            n_dictionary[key] = values_to_correct[value]
        else:
            n_dictionary[key] = value
    return n_dictionary

# Ausfiltern von nicht rellevanten Zeilen (row = Zeile)
# Bsp.: nur Zeile behalten, wenn parameter "Spam" und korespondierende value == True sind
def get_only_data_rows_with_parameter_and_value(dictionary : dict, parameter, value) -> dict:
    data_list = []
    for row in dictionary:
        for key in row.keys():
            if key == parameter and row[key] == value:
                data_list.append(row)
    return data_list

# Sortieren der values innerhalb jeder Reihe in Spalten (jede Spalte mit ihrem Parameter enthällt alle values jeder Reihe, die zu diesem Parameter gehören)
# exclude_keys bestimmt, welche keys (Parameter) ignoriert werden sollen
# Bsp.: test_daten = [
#    {"a" : True, "b", "False", "c" : False},
#    {"a" : False, "b", "True", "c" : True},
#    {"a" : False, "b", "False", "c" : False},
# ]
#
# ↳ wird zu: {
#   "a" : [True, False, False],
#   "b" : [False, True, False],
#   "c" : [False, True, False]
# }
#
def sort_row_values_from_data_list_in_collums(dictionary : list, exclude_keys : list = []) -> dict:
    data_set_values = {}
    for row in dictionary:
        for key in row.keys():
            if not exclude_keys.__contains__(key):
                if not data_set_values.keys().__contains__(key):
                    data_set_values[key] = []
                data_set_values[key].append(row[key])

    return data_set_values

# Für jeden Parameter, der für einen Spam stehen kann, die Wahrscheimlichkeit ermittel
# value_to_check_probability bestimmt den value typ für den parameter, dessen Wahrscheinlichkeit bestimmt werden soll
# exclude_keys bestimmt, welche keys (Parameter) ignoriert werden sollen
def get_value_probability_for_data_parameter(sorted_row_values : dict, value_to_check_probability, exclude_keys : list = []) -> dict:
    probabilities = {}
    for key in sorted_row_values.keys():
        if not exclude_keys.__contains__(key):
            amount_value_to_check_in_row = sorted_row_values[key].count(value_to_check_probability)
            probability = amount_value_to_check_in_row / len(sorted_row_values[key])
            if probability > 0:
                probabilities[key] = probability
    return probabilities

# Prozentuale Häufigkeiten umgewandeln in "Weights" (Gewichtung der einzelnen Parameter)
def get_data_parameter_weights(probabilities : dict) -> dict:
    for key in probabilities.keys():
        probabilities[key] = round(probabilities[key] * 100)
    return probabilities

# Hilfsfunktion von "get_combined_value_probabilities_for_data_parameter" um zu überprüfen ob eine Kombination bereits vorhanden ist
# wenn eine Kombination bereits vorhanden ist, dann erhöht sich ihre rellative Häufigkeit um 1
def combination_exists_already(combinations : list, combination : dict):
    for com in combinations:
        if com == combination:
            com["rellative_probability"] += 1
            return True
    return False

# Ermittelt die rellative Häufigkeit verschiedener Kombinationen im Datensatz (Achtung!: Nur bools akzeptiert, außer zu exclude_keys gehörige)
# Rellative Häufigkeit wird mit 10 multipliziert um besser mit den Werten arbeiten zu können
def get_combined_value_probabilities_for_data_parameter(dictionary : dict, exclude_keys : list = []) -> dict:
    combinations = []
    for row in dictionary:
        combination = {}
        for key in row:
            if not exclude_keys.__contains__(key) and type(row[key]) is bool:
                combination[key] = row[key]
        combination["rellative_probability"] = 1
        if not combination_exists_already(combinations, combination):
            combinations.append(combination)
    for combination in combinations:
        combination["rellative_probability"] = combination["rellative_probability"] * 10
    return combinations

# Ermitteln der minimalen Anzahl an value_to_check_probability values innerhalb einer Reihe
# exclude_keys bestimmt, welche keys (Parameter) ignoriert werden sollen
def get_min_amount_positiv_value_appearance_for_data_parameter(data_list : dict, value_to_check_probability, exclude_keys : list = []) -> dict:
    min_amount = 0
    for row in data_list:
        amount = 0
        for key in row.keys():
            if row[key] == value_to_check_probability and not exclude_keys.__contains__(key):
                amount += 1
        if amount < min_amount or min_amount == 0:
            min_amount = amount
    return min_amount

# Ermitteln der maximalen Anzahl an value_to_check_probability values innerhalb einer Reihe
# exclude_keys bestimmt, welche keys (Parameter) ignoriert werden sollen
def get_max_amount_positiv_value_appearance_for_data_parameter(data_list : dict, value_to_check_probability, exclude_keys : list = []) -> dict:
    min_amount = 0
    for row in data_list:
        amount = 0
        for key in row.keys():
            if row[key] == value_to_check_probability and not exclude_keys.__contains__(key):
                amount += 1
        if amount > min_amount or min_amount == 0:
            min_amount = amount
    return min_amount