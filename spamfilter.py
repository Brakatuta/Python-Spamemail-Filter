from dataformater import get_data_from_csv
from dataformater import cleanup_dictionary
from dataformater import cleanup_data_list
from dataformater import get_only_data_rows_with_parameter_and_value
from dataformater import sort_row_values_from_data_list_in_collums
from dataformater import get_value_probability_for_data_parameter
from dataformater import get_combined_value_probabilities_for_data_parameter
from dataformater import get_min_amount_positiv_value_appearance_for_data_parameter
from dataformater import get_max_amount_positiv_value_appearance_for_data_parameter
from dataformater import get_data_parameter_weights

# --------------------------- Ermitteln von benötigten Parametern, Gewischtung und Mustern------------------------------

# Rohdaten
csv_file_dir = r'C:\Users\MaxScho0408\Desktop\spamfilter\spam_data.csv'

# Rohdaten als dictionary
test_data_dict : dict = get_data_from_csv(csv_file_dir)

# Parameter values, die in der daten dictionary verändert werden müssen (nur bool values)
# Annahme, dass positive bool parameter "unbekannter Absender (True)", "Ansprache (anonym -> True)", "Betreff (True)", "Verlinkungen (True)", "Anhang (True)", "Fremdsprache (True)" in diverser Gewischtung und
# Kombination ausschlaggebend für Spam sind
values_to_correct = {
    "Ja" : True, "Nein" : False, "anonym" : True, "Name" : False
}

# "Aufräumen" der dictionary durch Korigieren von Werten (besser lesbar für PC) und entfernen von Lehrzeichen vor Parameter strings (warum auch immer sind da Lehrzeichen in den Roh-Testdaten)
test_data_dict : dict = cleanup_data_list(test_data_dict, values_to_correct)

# Bessere Daten Liste
#print(test_data_dict) 

# Filtern aller Emails, die als Spam identifiziert wurden
test_data_dict : dict = get_only_data_rows_with_parameter_and_value(test_data_dict, "Spam", True)

# Nur noch Spam-Emails
#print(test_data_dict)

# Identifizieren der Gewichtung für jede Wert Kombination, die in einer Email auftauchen kann
# Bsp.:
# k1 = [True, False, True, True, False, False]
# k1 = [False, False, True, True, True, False]
# Gewichtung wird durch Häufigkeit der Kombination ermittelt
# Bsp.:
# k1 = 10
# k2 = 20
# k3 = 30
# k4 = 10
# usw.
combination_weights : dict = get_combined_value_probabilities_for_data_parameter(test_data_dict, ["Spam"])

# mögliche Kombination die zu Spam führen
#print(combination_weights)

# Ermitteln Wie ein True statements für potentiell für Spam ausschlaggebende Parameter mindestens / maximal benötigt werden
minimum_amount_values = get_min_amount_positiv_value_appearance_for_data_parameter(test_data_dict, True, ["Spam"])
maximum_amount_values = get_max_amount_positiv_value_appearance_for_data_parameter(test_data_dict, True, ["Spam"])

# Minimal-, und Maximalwert für True statements
#print(minimum_amount_values)
#print(maximum_amount_values)

# Jedem Parameter werden alle Werte (True oder False) aller Zeilen hinzugefügt
# Exemplarisches Bsp.: 
# test_daten = [
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
test_data_dict : dict = sort_row_values_from_data_list_in_collums(test_data_dict, ["Spam"])

# sortierte Daten
#print(test_data_dict)

# Ermitteln der prozentualen Gewischtung einzelner Parameter für Spam
value_probabilities : dict = get_value_probability_for_data_parameter(test_data_dict, True, ["Spam"])

# Prozentuale Gewischtung der Parameter
print(value_probabilities)

# Gewichtung der Parameter als ganzzahlige Werte (kann dann z.B besser veranschaulicht werden bzw. für spätere Algorythmen besser verwendet werden)
parameter_weights = get_data_parameter_weights(value_probabilities)

print(parameter_weights)

# Ermitteln des durchschnittlichen "Email-Gewichts"
average_email_weight = 0

for parameter in parameter_weights.keys():
    average_email_weight += parameter_weights[parameter]
divisor = 0
for value in parameter_weights.values():
    if value != 0:
        divisor += 1
average_email_weight = average_email_weight / divisor

# Durchschnittliches "Email-Gewicht"
print(average_email_weight)

# Hilfsfunktion von "is_email_spam" um das Gewicht dieser spezifischen Email-Parameter-Werte-Kombination (combination) zu ermitteln
# Durch abggleichen mit allen möglichen Kombinationen wird das Gewicht ermittelt
def get_valid_combination_weight(combination : dict):
    for combination_weight in combination_weights:
        combination["rellative_probability"] = combination_weight["rellative_probability"]
        if combination == combination:
            return combination_weight["rellative_probability"]
    return 0

# Funktion zum ermitteln ob Email Spam ist oder nicht
def is_email_spam(email : dict, filter_value : bool, adjustable_weight_param : float):
    formated_email = cleanup_dictionary(email, values_to_correct)
    email_amount_valid_spam_params : int = 0
    email_value : int = 0
    combination = {}

    # Erstellen der Kombination der Werte diser spezifischen Email
    for parameter in formated_email.keys():
        if formated_email[parameter] == filter_value:
            if parameter != "Spam": # <- wird ignoriert, weil ist nur "Checkparameter"
                email_amount_valid_spam_params += 1
                parameter_weight = parameter_weights[parameter]
                email_value += parameter_weight
        if type(formated_email[parameter]) is bool:
            combination[parameter] = formated_email[parameter]
    
    # Kombinationsgewischt dieser Email
    combination_weight = get_valid_combination_weight(combination)

    # Threshold bzw. Grenzwert des Emailgewichts für diese Email
    # adjustable_weight_param: Anpassbarer Parameter
    email_weight_treshold = (float(average_email_weight) + float(combination_weight)) * adjustable_weight_param
    if combination_weight == 0: # <- wenn Kombination nicht in möglichen Kombinationen für Spam existiert, ist kein Spam vorhanden
        return False

    # Wenn der Gwichtungswert dieser Email über / auf dem für dise Email ermittelten tresholds liegt und die Anzahl an valider Parameter zwischen / auf dem Minimum und Maximum liegt, dann liegt Spam vor
    if float(email_value) >= email_weight_treshold and email_amount_valid_spam_params >= minimum_amount_values and email_amount_valid_spam_params <= maximum_amount_values:
        return True
    else:
        return False

# Formatiren der Testdaten Liste zum Anpassen/ Trainieren des Algorythmus
test_data_dict = get_data_from_csv(csv_file_dir)
test_data_dict = cleanup_data_list(test_data_dict, values_to_correct)

# Anzahl der Emails im Test-Datensatz
amount_isg_rows = 200

# 1 Trainingszyklos, gibt Anzahl korekt eigestufter Emails zurück
def train_algorythm(parameter : float):
    correct_ones : int = 0
    for row in test_data_dict:
        email_is_spam_real = row["Spam"]
        email_is_spam_algo = is_email_spam(row, True, parameter)
        #print(email_is_spam_real, " | real")
        #print(email_is_spam_algo, " | alogorythm calculated")
        if email_is_spam_real == email_is_spam_algo:
            correct_ones += 1
    print(correct_ones, " correct ones out of ", amount_isg_rows, " with parameter a value of ", parameter)
    return correct_ones

# Definieren des Start-"Trainings"-Parameters zum Anpassen, des Algorythmus
train_parameter : float = 2
# Definieren der Parameteränderung pro Trainingszyklos
train_param_add_per_period : float = 0.0005

# Trainingsergebnisse
results = []

# Ermitteln des besten Trainingsergebnisses, gibt besten anpassbaren Parameter zurück
def get_best_parameter():
    best_parameter = 0
    best_ratio = 0
    for result in results:
        ratio = result[0]
        parameter = result[1]
        if ratio > best_ratio:
            best_ratio = ratio
            best_parameter = parameter
    return best_parameter

# Trainingsfunktion
def train(periods : int):
    global results
    global train_parameter
    for i in range(0, periods):
        correct_ones = train_algorythm(train_parameter)
        ratio = correct_ones/ amount_isg_rows
        results.append([ratio, train_parameter])
        train_parameter += train_param_add_per_period       

# Wie viele Trainings-Zyklen sollen ablaufen
train(2000)

# Der anpassbare Parameter, welcher beim Überprüfen aller Emails zum besten Ergebnis führt
best_parameter = get_best_parameter()

print(best_parameter)

# Gibt die Erfolgsrate des Algorythmus, nach dem Training an
correct_ones = train_algorythm(best_parameter)
print(correct_ones)
print("Success Rate: ",  100 * (correct_ones / amount_isg_rows), "%")

# Testdatensätzte zum Überprüfen
test_data = {
    "unbekannter Absender" : "Nein", "Ansprache" : "anonym", "Betreff" : "Nein", "Verlinkungen" : "Ja", "Anhang" : "Ja", "Fremdsprache" : "Ja", "Länge" : 450, "Fehlerquote" : 0.02
}

test_data2 = {
    "unbekannter Absender" : "Ja", "Ansprache" : "Name", "Betreff" : "Nein", "Verlinkungen" : "Nein", "Anhang" : "Ja", "Fremdsprache" : "Nein", "Länge" : 450, "Fehlerquote" : 0.02
}

print(is_email_spam(test_data2, True, best_parameter))