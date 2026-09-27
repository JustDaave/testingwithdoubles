import pytest

from mydb import MyDB


@pytest.fixture
def db():
    # Skip __init__ so tests for the other methods only exercise that method.
    database = MyDB.__new__(MyDB)
    database.fname = "somefilename"
    return database


def describe_MyDB():
    def describe_initializer():
        def it_saves_the_filename(mocker):
            mocker.patch("mydb.os.path.isfile", return_value=True)

            database = MyDB("somefilename")

            assert database.fname == "somefilename"

        def it_checks_whether_the_file_exists(mocker):
            isfile = mocker.patch("mydb.os.path.isfile", return_value=True)

            MyDB("somefilename")

            isfile.assert_called_once_with("somefilename")

        def it_creates_an_empty_database_when_the_file_is_missing(mocker):
            mocker.patch("mydb.os.path.isfile", return_value=False)
            save_strings = mocker.patch.object(MyDB, "saveStrings")

            MyDB("somefilename")

            save_strings.assert_called_once_with([])

        def it_does_not_save_when_the_file_exists(mocker):
            mocker.patch("mydb.os.path.isfile", return_value=True)
            save_strings = mocker.patch.object(MyDB, "saveStrings")

            MyDB("somefilename")

            save_strings.assert_not_called()

    def describe_loadStrings():
        def it_opens_the_database_for_reading(db, mocker):
            opened = mocker.patch("builtins.open", mocker.mock_open())
            mocker.patch("mydb.pickle.load", return_value=[])

            db.loadStrings()

            opened.assert_called_once_with("somefilename", "rb")

        def it_loads_from_the_open_file(db, mocker):
            opened = mocker.patch("builtins.open", mocker.mock_open())
            load = mocker.patch("mydb.pickle.load", return_value=[])

            db.loadStrings()

            load.assert_called_once_with(opened.return_value.__enter__.return_value)

        def it_returns_the_loaded_strings(db, mocker):
            mocker.patch("builtins.open", mocker.mock_open())
            strings = ["acorn", "walnut"]
            mocker.patch("mydb.pickle.load", return_value=strings)

            result = db.loadStrings()

            assert result is strings

    def describe_saveStrings():
        def it_opens_the_database_for_writing(db, mocker):
            opened = mocker.patch("builtins.open", mocker.mock_open())
            mocker.patch("mydb.pickle.dump")

            db.saveStrings(["acorn"])

            opened.assert_called_once_with("somefilename", "wb")

        def it_dumps_the_strings_to_the_open_file(db, mocker):
            opened = mocker.patch("builtins.open", mocker.mock_open())
            dump = mocker.patch("mydb.pickle.dump")
            strings = ["acorn", "walnut"]

            db.saveStrings(strings)

            dump.assert_called_once_with(strings, opened.return_value.__enter__.return_value)

    def describe_saveString():
        def it_loads_the_existing_strings(db, mocker):
            load_strings = mocker.patch.object(db, "loadStrings", return_value=[])
            mocker.patch.object(db, "saveStrings")

            db.saveString("acorn")

            load_strings.assert_called_once_with()

        def it_appends_the_new_string(db, mocker):
            mocker.patch.object(db, "loadStrings", return_value=["acorn"])
            save_strings = mocker.patch.object(db, "saveStrings")

            db.saveString("walnut")

            save_strings.assert_called_once_with(["acorn", "walnut"])

        def it_saves_an_empty_database_with_its_first_string(db, mocker):
            mocker.patch.object(db, "loadStrings", return_value=[])
            save_strings = mocker.patch.object(db, "saveStrings")

            db.saveString("acorn")

            save_strings.assert_called_once_with(["acorn"])
