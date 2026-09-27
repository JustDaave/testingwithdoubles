import io
import json
import pytest
from squirrel_server import SquirrelServerHandler
from squirrel_db import SquirrelDB

todo = pytest.mark.skip(reason='TODO: pending spec')

class FakeRequest():
    def __init__(self, mock_wfile, method, path, body=None):
        self._mock_wfile = mock_wfile
        self._method = method
        self._path = path
        self._body = body

    def sendall(self, x):
        return

    def makefile(self, *args, **kwargs):
        if args[0] == 'rb':
            if self._body:
                headers = 'Content-Length: {}\r\n'.format(len(self._body))
                body = self._body
            else:
                headers = ''
                body = ''
            request = bytes('{} {} HTTP/1.0\r\n{}\r\n{}'.format(self._method, self._path, headers, body), 'utf-8')
            return io.BytesIO(request)
        elif args[0] == 'wb':
            return self._mock_wfile

def describe_SquirrelServerHandler():

    @pytest.fixture
    def mock_response_methods(mocker):
        mocker.patch.object(SquirrelServerHandler, 'wbufsize', 1)
        mock_send_response = mocker.patch.object(SquirrelServerHandler, 'send_response')
        mock_send_header = mocker.patch.object(SquirrelServerHandler, 'send_header')
        mock_end_headers = mocker.patch.object(SquirrelServerHandler, 'end_headers')
        return mock_send_response, mock_send_header, mock_end_headers

    @pytest.fixture
    def mock_get_squirrels_request(mocker):
        return FakeRequest(mocker.Mock(), 'GET', '/squirrels')

    @pytest.fixture
    def mock_get_squirrel_request(mocker):
        return FakeRequest(mocker.Mock(), 'GET', '/squirrels/12345')

    @pytest.fixture
    def mock_create_squirrel_request(mocker):
        return FakeRequest(mocker.Mock(), 'POST', '/squirrels', body='name=Chippy&size=small')

    @pytest.fixture
    def mock_client():
        return ('127.0.0.1', 80)

    @pytest.fixture
    def mock_server():
        return None

    def describe_GET_squirrels_collection():

        def it_queries_db_for_squirrels(mocker, mock_get_squirrels_request, mock_client, mock_server):
            mock_get_squirrels = mocker.patch.object(SquirrelDB, 'getSquirrels', return_value=["squirrel"])
            SquirrelServerHandler(mock_get_squirrels_request, mock_client, mock_server)

            mock_get_squirrels.assert_called_once()

        def it_returns_200_status_code(mocker, mock_response_methods, mock_get_squirrels_request, mock_client, mock_server):
            mocker.patch.object(SquirrelDB, 'getSquirrels', return_value=["squirrel"])
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

            SquirrelServerHandler(mock_get_squirrels_request, mock_client, mock_server)
            mock_send_response.assert_called_once_with(200)

        def it_returns_json_content_type_header(mocker, mock_response_methods, mock_get_squirrels_request, mock_client, mock_server):
            mocker.patch.object(SquirrelDB, 'getSquirrels', return_value=["squirrel"])
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

            SquirrelServerHandler(mock_get_squirrels_request, mock_client, mock_server)
            mock_send_header.assert_called_once_with("Content-Type", "application/json")

        def it_calls_end_headers(mocker, mock_response_methods, mock_get_squirrels_request, mock_client, mock_server):
            mocker.patch.object(SquirrelDB, 'getSquirrels', return_value=["squirrel"])
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

            SquirrelServerHandler(mock_get_squirrels_request, mock_client, mock_server)
            mock_end_headers.assert_called_once()

        def it_returns_response_body_with_squirrels_as_json_data(mocker, mock_response_methods, mock_get_squirrels_request, mock_client, mock_server):
            mocker.patch.object(SquirrelDB, 'getSquirrels', return_value=["squirrel"])

            response = SquirrelServerHandler(mock_get_squirrels_request, mock_client, mock_server)
            response.wfile.write.assert_called_once_with(bytes(json.dumps(["squirrel"]), "utf-8"))

    def describe_GET_squirrel_member():

        def it_queries_db_for_squirrel(mocker, mock_response_methods, mock_get_squirrel_request, mock_client, mock_server):
            mock_get_squirrel = mocker.patch.object(SquirrelDB, 'getSquirrel', return_value="squirrel")
            SquirrelServerHandler(mock_get_squirrel_request, mock_client, mock_server)

            mock_get_squirrel.assert_called_once_with("12345")

    def describe_POST_squirrels_collection():

        def it_queries_db_to_create_squirrel(mocker, mock_response_methods, mock_create_squirrel_request, mock_client, mock_server):
            mock_create_squirrel = mocker.patch.object(SquirrelDB, 'createSquirrel')

            SquirrelServerHandler(mock_create_squirrel_request, mock_client, mock_server)
            mock_create_squirrel.assert_called_once_with('Chippy', 'small')
