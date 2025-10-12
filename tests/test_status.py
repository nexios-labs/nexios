import warnings

import nexios.status


def test_http_status_constants():
    assert nexios.status.HTTP_200_OK == 200
    assert nexios.status.HTTP_404_NOT_FOUND == 404
    assert nexios.status.HTTP_500_INTERNAL_SERVER_ERROR == 500


def test_websocket_status_constants():
    assert nexios.status.WS_1000_NORMAL_CLOSURE == 1000
    assert nexios.status.WS_1011_INTERNAL_ERROR == 1011


def test_deprecated_ws_status_warns():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        val = getattr(nexios.status, "WS_1004_NO_STATUS_RCVD")
        assert val == 1004
        assert any("deprecated" in str(warn.message) for warn in w)
