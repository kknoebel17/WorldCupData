"""Single location for tests related to the image access class."""

import requests
import pytest
from PIL import ImageFile
from unittest.mock import Mock

from access.images import Images

@pytest.mark.parametrize(
    "image_content", [
        b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
        None,
    ])
def test_image_access(monkeypatch, image_content):
    # Mock request for thumbnail url
    mock_json_data = {
        "data": [
            {"thumbnail_url": "https://example.com"}
        ]
    }
    mock_api_response = Mock()
    mock_api_response.status_code = 200
    mock_api_response.json.return_value = mock_json_data

    # Mock request for image
    mock_image_data_response = Mock()
    mock_image_data_response.status_code = 200
    mock_image_data_response.content = image_content

    mock_get = Mock(side_effect=[mock_api_response, mock_image_data_response])
    monkeypatch.setattr(requests, "get", mock_get)

    player_name = 'Vinicius Junior'
    ia = Images(player_name)
    query_data = ia.get_image()
    assert query_data is not None
    assert isinstance(query_data, ImageFile.ImageFile)
    assert mock_get.call_count == 2
