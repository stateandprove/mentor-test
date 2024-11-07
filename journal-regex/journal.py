import re
import csv

from dataclasses import dataclass


#  токен "Авторы:" ищет символы "Авторы:"
#  \s* означает от одного до бесконечности пробелов
#  группа ([^;]+) ищет как минимум один символ, отличный от ";"
#  токен ";" ищет закрывающую точку с запятой
authors_regex = r"Авторы:\s*([^;]+);"

# аналогично authors_regex, с опциональными пробелами в начале
title_regex = r"\s*Название:\s*([^;]+);"

# аналогично, \d{4} матчит цифру 4 раза, получется 4-значный год
years_regex = r"\s*Год:\s*(\d{4})"


@dataclass
class Article:
    authors: str
    title: str
    year: int


def parse_articles_from_journal(journal: str, regex: str) -> list[Article]:
    pattern = re.compile(regex, flags=re.IGNORECASE)
    entries = pattern.findall(journal)
    articles = [Article(*entry) for entry in entries]
    return articles


def extract_articles(journal: str) -> list[Article]:
    pattern = authors_regex + title_regex + years_regex
    articles = parse_articles_from_journal(journal, pattern)
    return articles


def get_all_articles_by_author(author: str, journal: str) -> list[Article]:
    # аналогично authors_regex, но ищем совпадения по имени
    # автора с произвольным количеством символов до и после
    pattern = rf"Авторы:\s*([^;]*\b{re.escape(author)}\b[^;]*);" + title_regex + years_regex
    articles = parse_articles_from_journal(journal, pattern)
    return articles


def get_all_articles_by_title(title: str, journal: str) -> list[Article]:
    # в этом случае мы ищем по точному совпадению названия статьи
    pattern = authors_regex + rf"\s*Название:\s*({re.escape(title)});" + years_regex
    articles = parse_articles_from_journal(journal, pattern)
    return articles


def get_articles_count(articles: list[Article]) -> dict:
    articles_count_by_year = dict()

    for article in articles:
        # считаем статьи по годам
        if not articles_count_by_year.get(article.year):
            articles_count_by_year[article.year] = 0
        articles_count_by_year[article.year] += 1

    articles_count = {
        "total": sum(articles_count_by_year.values()),  # сумма всех статей по годам
        "by_year": articles_count_by_year
    }

    return articles_count


def generate_csv_from_articles(articles: list[Article], file_name: str) -> None:
    file = open(file_name, mode='w', newline='', encoding='utf-8')
    writer = csv.writer(file)
    writer.writerow(["Авторы", "Название", "Год"])  # заголовки
    for article in articles:
        # заполняем данные
        writer.writerow([
            article.authors, article.title, article.year
        ])
    file.close()


def proceed_journal_data(author_name: str, title: str) -> None:
    input_file, output_file = 'journal.txt', 'journal.csv'

    try:
        file = open(input_file)
    except FileNotFoundError:
        print(f"Файл {input_file} не найден")
        return

    journal = file.read()
    file.close()

    articles_extracted = extract_articles(journal)

    if not articles_extracted:
        print(f"В файле {input_file} не найдено ни одной статьи. "
              f"Проверьте правильность формата данных.")
        return

    print(articles_extracted)

    articles_statistics = get_articles_count(articles_extracted)
    print(articles_statistics)

    articles_by_author = get_all_articles_by_author(author_name, journal)
    print(articles_by_author)

    articles_by_title = get_all_articles_by_title(title, journal)
    print(articles_by_title)

    generate_csv_from_articles(articles_extracted, output_file)


if __name__ == "__main__":
    proceed_journal_data("иван", "Основы программирования")
