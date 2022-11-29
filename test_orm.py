import os
import sqlite3
import pytest
import inspect


from my_orm import Database, Table, Column, ForeignKey

# fixtures
def test_create_db(db):
    assert isinstance(db.conn, sqlite3.Connection)
    assert db.tables == []

def test_define_tables(Author,Book):
    assert Author.name.type == str
    assert Book.author.table == Author

    assert Author.name.sql_type == "TEXT"
    assert Author.age.sql_type == "INTEGER"


def test_create_tables(db, Author, Book):
    db.create(Author)
    db.create(Book)

    assert Author._get_create_sql() ==\
        "CREATE TABLE IF NOT EXISTS author (id INTEGER PRIMARY KEY AUTOINCREMENT, age INTEGER, name TEXT);"

    assert Book._get_create_sql() ==\
        "CREATE TABLE IF NOT EXISTS book (id INTEGER PRIMARY KEY AUTOINCREMENT, author_id INTEGER, published INTEGER, title TEXT);"

    for table in ("author", "book"):
        assert table in db.tables


def test_create_author(db, Author):
    db.create(Author)
    name_ = "John Doe"
    age = 35

    print(inspect.getmro(Author))

    author_entry = Author(name = name_, age = age)

    assert author_entry.name == name_
    assert author_entry.age == age
    assert author_entry.id is None


def test_save_author_instances(db, Author):
    db.create(Author)

    john = Author(name="John Doe", age=23)
    db.save(john)
    assert john._get_insert_sql() == (
        "INSERT INTO author (age, name) VALUES (?, ?);",
        [23, "John Doe"]
    )
    assert john.id == 1

    ralph = Author(name="Ralph Tungol", age=28)
    db.save(ralph)
    assert ralph.id == 2

    lucas = Author(name="Lucas Friedmann", age=43)
    db.save(lucas)
    assert lucas.id == 3

    kendra = Author(name="Kendra Yoshizawa", age=39)
    db.save(kendra)
    assert kendra.id == 4


def test_query_all_authors(db, Author):
    db.create(Author)
    darlene = Author(name="Darlene", age=23)
    jak = Author(name="jak", age=34)
    db.save(darlene)
    db.save(jak)

    authors = db.all(Author)

    assert Author._get_select_all_sql() == (
        "SELECT id, age, name FROM author;",
        ["id", "age", "name"]
    )

    assert len(authors) == 2
    assert type(authors[0]) == Author
    assert {a.age for a in authors} == {23,34}
    assert {a.name for a in authors} == {"Darlene", "jak"}