from random import randint


# словарь, в котором ключи - первая буква города, а значения - список городов на эту букву
cities_by_first_letter = {}

# множество со всеми городами (для скорости)
all_cities = set()

# кортеж с выбранными городами (для сохранения порядка)
picked_cities = tuple()

f = open('cities.txt')

# формируем словарь cities_by_first_letter и множество all_cities из строк файла
for line in f:
    city_name = line.strip().lower()  # мы хотим, чтобы слова были нечувствительны к регистру
    first_letter = city_name[0]
    cities_starting_from_this_letter = cities_by_first_letter.get(first_letter)

    if not cities_starting_from_this_letter:
        cities_by_first_letter[first_letter] = []

    all_cities.add(city_name)
    cities_by_first_letter[first_letter].append(city_name)

f.close()

# список всех букв, на которые начинаются города
letters = list(cities_by_first_letter.keys())

# берем из списка букв случайную букву
random_letter = letters[randint(0, len(letters) - 1)]

# получаем список городов, начинающихся на эту букву
random_first_letter_cities = cities_by_first_letter[random_letter]

# выбираем случайный город из этого списка и удаляем его из выборки
random_index = randint(0, len(random_first_letter_cities) - 1)
random_city = random_first_letter_cities[random_index]
random_first_letter_cities.pop(random_index)

# заводим переменную current_city для цикла, добавляем город в кортеж выбранных
current_city = random_city
picked_cities += (current_city,)

print(f"Город {current_city.title()}. Ваш ход.")
failures_count = 5

# начало игры
while failures_count > 0:
    print(f"Попыток осталось: {failures_count}")

    city_input = input()

    if not city_input:
        print("Введите название города")
        continue

    city_input_lower = city_input.lower()  # для нечувствительности к регистру

    if city_input_lower not in all_cities:
        print("Такого города нет")
        failures_count -= 1
        continue

    input_city_first_letter = city_input_lower[0]
    input_city_last_letter = city_input_lower[-1]
    current_city_first_letter = current_city[0]
    current_city_last_letter = current_city[-1]

    # по умолчанию сравниваем первую букву введенного слова с последней буквой загаданного
    input_city_letter_to_compare = input_city_first_letter
    current_city_letter_to_compare = current_city_last_letter

    # если нету городов, которые начинаются на первую букву
    # введенного слова, то используем для сравнения последнюю
    if not cities_by_first_letter.get(input_city_letter_to_compare):
        input_city_letter_to_compare = input_city_last_letter

    # если нету городов, которые начинаются на последнюю букву
    # загаданного слова, то используем для сравнения первую
    if not cities_by_first_letter.get(current_city_letter_to_compare):
        current_city_letter_to_compare = current_city_first_letter

    # сравниваем интересующие нас буквы
    if input_city_letter_to_compare != current_city_letter_to_compare:
        print(f"Город должен начинаться на букву {current_city_letter_to_compare}")
        failures_count -= 1
        continue

    if city_input_lower in picked_cities:
        print("Этот город уже назывался")
        failures_count -= 1
        continue

    # удаляем введенный город из выборки, добавляем в кортеж выбранных городов
    input_letter_cities_list = cities_by_first_letter.get(input_city_letter_to_compare)
    input_city_index = input_letter_cities_list.index(city_input_lower)
    input_letter_cities_list.pop(input_city_index)
    picked_cities += (city_input_lower,)

    # определяем первую букву следующего города как последнюю букву предыдущего
    next_city_first_letter = input_city_last_letter

    # если нет городов на последнюю букву предыдущего города, то используем первую
    if not cities_by_first_letter.get(next_city_first_letter):
        next_city_first_letter = input_city_first_letter

    # получаем список городов, начинающихся на интересующую нас букву введенного слова
    new_cities_list = cities_by_first_letter.get(next_city_first_letter)

    # если таких городов нет - выходим из цикла, заканчиваем игру
    if not new_cities_list:
        print("Вы выиграли!")
        break

    # берем новый случайный город из списка, убираем его из выборки, добавляем к уже выбранным
    random_index = randint(0, len(new_cities_list) - 1)
    current_city = new_cities_list[random_index]
    new_cities_list.pop(random_index)
    picked_cities += (current_city,)

    # продолжаем цикл
    print(f"Город {current_city.title()}. Ваш ход.")
    failures_count = 5

if failures_count == 0:
    print("Вы проиграли!")

# записываем историю ходов
f = open('answers.txt', 'w')
for city in picked_cities:
    f.write(city.title() + '\n')
f.close()
