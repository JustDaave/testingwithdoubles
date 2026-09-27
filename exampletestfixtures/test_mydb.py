import pytest
import os

from mydb import MyDB

todo = pytest.mark.skip(reason='todo: pending spec')

def describe_MyDB():

    def describe_initializer():

        def it_assigns_fname_attribute_value(mocker):
            mocker.patch("os.path.isfile", return_value=True)
            db = MyDB("somefilename")
            assert db.fname == "somefilename"


        def it_creates_empty_database_if_it_does_not_exist(mocker):
            mock_isfile = mocker.patch("os.path.isfile", return_value=False)
            mock_open = mocker.patch("builtins.open", mocker.mock_open())
            mock_dump = mocker.patch("pickle.dump")
            db = MyDB("somefilename")

            mock_isfile.assert_called_once_with("somefilename")
            mock_open.assert_called_once_with("somefilename", "wb")
            mock_dump.assert_called_once_with([], mock_open.return_value

        def it_does_not_create_database_if_it_already_exists(mocker):
            mock_isfile = mocker.patch("os.path.isfile", return_value=True)
            mock_open = mocker.patch("builtins.open", mocker.mock_open())
            mock_dump = mocker.patch("pickle.dump")
            db = MyDB("somefilename")
            mock_isfile.assert_called_once_with("somefilename")
            mock_open.assert_not_called()
            mock_dump.assert_not_called()

    @todo
    def describe_loadStrings():
        pass

    @todo
    def describe_saveStrings():
        pass

    @todo
    def describe_saveString():
        pass
