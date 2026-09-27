import json
from types import SimpleNamespace

import pytest

from exampletestfixtures.test_squirrel_server import FakeRequest
from squirrel_server import SquirrelServerHandler


@pytest.fixture
def make_request(mocker):
    mocker.patch.object(SquirrelServerHandler, "wbufsize", 1)
    database_class = mocker.patch("squirrel_server.SquirrelDB")
    database = database_class.return_value
    send_response = mocker.patch.object(SquirrelServerHandler, "send_response")
    send_header = mocker.patch.object(SquirrelServerHandler, "send_header")
    end_headers = mocker.patch.object(SquirrelServerHandler, "end_headers")

    def make(method, path, body=None, squirrel=None, squirrels=None):
        database.getSquirrel.return_value = squirrel
        database.getSquirrels.return_value = squirrels
        output = mocker.Mock()
        request = FakeRequest(output, method, path, body)
        SquirrelServerHandler(request, ("127.0.0.1", 80), None)
        return SimpleNamespace(
            database_class=database_class,
            database=database,
            send_response=send_response,
            send_header=send_header,
            end_headers=end_headers,
            output=output,
        )

    return make


def describe_SquirrelServerHandler():
    def describe_handleSquirrelsIndex():
        def it_creates_a_database(make_request):
            response = make_request("GET", "/squirrels", squirrels=[])
            response.database_class.assert_called_once_with()

        def it_queries_all_squirrels(make_request):
            response = make_request("GET", "/squirrels", squirrels=[])
            response.database.getSquirrels.assert_called_once_with()

        def it_returns_200(make_request):
            response = make_request("GET", "/squirrels", squirrels=[])
            response.send_response.assert_called_once_with(200)

        def it_sets_the_json_content_type(make_request):
            response = make_request("GET", "/squirrels", squirrels=[])
            response.send_header.assert_called_once_with("Content-Type", "application/json")

        def it_finishes_the_headers(make_request):
            response = make_request("GET", "/squirrels", squirrels=[])
            response.end_headers.assert_called_once_with()

        def it_writes_the_squirrels_as_json(make_request):
            squirrels = [{"id": 1, "name": "Chippy", "size": "small"}]
            response = make_request("GET", "/squirrels", squirrels=squirrels)
            response.output.write.assert_called_once_with(json.dumps(squirrels).encode("utf-8"))

        def it_writes_an_empty_list_when_there_are_no_squirrels(make_request):
            response = make_request("GET", "/squirrels", squirrels=[])
            response.output.write.assert_called_once_with(b"[]")

    def describe_handleSquirrelsRetrieve():
        @pytest.fixture
        def squirrel():
            return {"id": 12345, "name": "Chippy", "size": "small"}

        def it_looks_up_the_requested_id(make_request, squirrel):
            response = make_request("GET", "/squirrels/12345", squirrel=squirrel)
            response.database.getSquirrel.assert_called_once_with("12345")

        def it_returns_200_for_a_found_squirrel(make_request, squirrel):
            response = make_request("GET", "/squirrels/12345", squirrel=squirrel)
            response.send_response.assert_called_once_with(200)

        def it_sets_the_json_content_type(make_request, squirrel):
            response = make_request("GET", "/squirrels/12345", squirrel=squirrel)
            response.send_header.assert_called_once_with("Content-Type", "application/json")

        def it_finishes_the_headers(make_request, squirrel):
            response = make_request("GET", "/squirrels/12345", squirrel=squirrel)
            response.end_headers.assert_called_once_with()

        def it_writes_the_found_squirrel_as_json(make_request, squirrel):
            response = make_request("GET", "/squirrels/12345", squirrel=squirrel)
            response.output.write.assert_called_once_with(json.dumps(squirrel).encode("utf-8"))

        def it_returns_404_for_a_missing_squirrel(make_request):
            response = make_request("GET", "/squirrels/12345")
            response.send_response.assert_called_once_with(404)

    def describe_handleSquirrelsCreate():
        def it_creates_a_squirrel_from_the_request_body(make_request):
            response = make_request("POST", "/squirrels", body="name=Chippy&size=small")
            response.database.createSquirrel.assert_called_once_with("Chippy", "small")

        def it_decodes_url_encoded_form_values(make_request):
            response = make_request("POST", "/squirrels", body="name=Red+Squirrel&size=very%20small")
            response.database.createSquirrel.assert_called_once_with("Red Squirrel", "very small")

        def it_returns_201(make_request):
            response = make_request("POST", "/squirrels", body="name=Chippy&size=small")
            response.send_response.assert_called_once_with(201)

        def it_finishes_the_headers(make_request):
            response = make_request("POST", "/squirrels", body="name=Chippy&size=small")
            response.end_headers.assert_called_once_with()

    def describe_handleSquirrelsUpdate():
        def it_checks_whether_the_squirrel_exists(make_request):
            response = make_request("PUT", "/squirrels/12345", body="name=Chippy&size=large", squirrel={"id": 12345})
            response.database.getSquirrel.assert_called_once_with("12345")

        def it_updates_the_found_squirrel(make_request):
            response = make_request("PUT", "/squirrels/12345", body="name=Chippy&size=large", squirrel={"id": 12345})
            response.database.updateSquirrel.assert_called_once_with("12345", "Chippy", "large")

        def it_returns_204_after_an_update(make_request):
            response = make_request("PUT", "/squirrels/12345", body="name=Chippy&size=large", squirrel={"id": 12345})
            response.send_response.assert_called_once_with(204)

        def it_finishes_the_headers_after_an_update(make_request):
            response = make_request("PUT", "/squirrels/12345", body="name=Chippy&size=large", squirrel={"id": 12345})
            response.end_headers.assert_called_once_with()

        def it_returns_404_for_a_missing_squirrel(make_request):
            response = make_request("PUT", "/squirrels/12345")
            response.send_response.assert_called_once_with(404)

        def it_does_not_update_a_missing_squirrel(make_request):
            response = make_request("PUT", "/squirrels/12345")
            response.database.updateSquirrel.assert_not_called()

    def describe_handleSquirrelsDelete():
        def it_checks_whether_the_squirrel_exists(make_request):
            response = make_request("DELETE", "/squirrels/12345", squirrel={"id": 12345})
            response.database.getSquirrel.assert_called_once_with("12345")

        def it_deletes_the_found_squirrel(make_request):
            response = make_request("DELETE", "/squirrels/12345", squirrel={"id": 12345})
            response.database.deleteSquirrel.assert_called_once_with("12345")

        def it_returns_204_after_deletion(make_request):
            response = make_request("DELETE", "/squirrels/12345", squirrel={"id": 12345})
            response.send_response.assert_called_once_with(204)

        def it_finishes_the_headers_after_deletion(make_request):
            response = make_request("DELETE", "/squirrels/12345", squirrel={"id": 12345})
            response.end_headers.assert_called_once_with()

        def it_returns_404_for_a_missing_squirrel(make_request):
            response = make_request("DELETE", "/squirrels/12345")
            response.send_response.assert_called_once_with(404)

        def it_does_not_delete_a_missing_squirrel(make_request):
            response = make_request("DELETE", "/squirrels/12345")
            response.database.deleteSquirrel.assert_not_called()

    def describe_handle404():
        @pytest.mark.parametrize(
            "method,path",
            [
                ("GET", "/unknown"),
                ("POST", "/unknown"),
                ("POST", "/squirrels/12345"),
                ("PUT", "/unknown"),
                ("PUT", "/squirrels"),
                ("DELETE", "/unknown"),
                ("DELETE", "/squirrels"),
            ],
        )
        def it_returns_404_for_invalid_routes(make_request, method, path):
            response = make_request(method, path)
            response.send_response.assert_called_once_with(404)

        def it_sets_the_plain_text_content_type(make_request):
            response = make_request("GET", "/unknown")
            response.send_header.assert_called_once_with("Content-Type", "text/plain")

        def it_finishes_the_headers(make_request):
            response = make_request("GET", "/unknown")
            response.end_headers.assert_called_once_with()

        def it_writes_a_not_found_message(make_request):
            response = make_request("GET", "/unknown")
            response.output.write.assert_called_once_with(b"404 Not Found")
