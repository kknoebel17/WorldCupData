"""Single location for tests related to the image access class."""

import requests
import pytest
from PIL import ImageFile
from unittest.mock import Mock

from access.images import Images
from access.relational import SQLAccess

@pytest.mark.parametrize(
    "image_content", [
        b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
        None,
    ])
def test_image_access(monkeypatch, image_content):
    sa = SQLAccess()
    cursor = sa.create_connection()
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

    player_name = 'Vinicius Júnior'
    ia = Images(player_name)
    query_data = ia.get_image()

    # Clean up database
    cursor.execute("DELETE FROM worldcup26.images")
    sa.connection.commit()
    sa.close_connection(cursor)

    assert query_data is not None
    assert isinstance(query_data, ImageFile.ImageFile)
    assert mock_get.call_count == 2

def test_get_image_url():
    # Set up database
    player_name = 'Vinicius Júnior'
    player_id = str(184)
    image_url = "https://example.com"
    sa = SQLAccess()
    cursor = sa.create_connection()
    test_statement = (f"INSERT into worldcup26.images (image_url, player_id) VALUES (%s, %s)")
    record_to_insert = (image_url, player_id)
    cursor.execute(test_statement, record_to_insert)
    sa.connection.commit()
    # Test image class
    ia = Images(player_name)
    url = ia.get_image_url()
    # Test image written to database
    test_statement = ("SELECT * from worldcup26.images")
    cursor.execute(test_statement)
    sa.connection.commit()
    test_results = cursor.fetchall()

    # Clean up database
    cursor.execute("DELETE FROM worldcup26.images")
    sa.connection.commit()
    sa.close_connection(cursor)

    assert url[0][0] == image_url
    assert test_results is not None

def test_get_image_url_when_exists(monkeypatch):
    # Mock request for thumbnail url
    image_url = "https://example.com"
    image_content = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
    mock_json_data = {
        "data": [
            {"thumbnail_url": "https://fake_url.com"}
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
    # Set up database
    # Only add image url for Vinícius Júnior
    player_id = str(184)
    sa = SQLAccess()
    cursor = sa.create_connection()
    test_statement = (f"INSERT into worldcup26.images (image_url, player_id) VALUES (%s, %s)")
    record_to_insert = (image_url, player_id)
    cursor.execute(test_statement, record_to_insert)
    sa.connection.commit()
    # Test image class
    ia = Images('Vinicius Júnior')
    url = ia.get_image()

    # Clean up database
    cursor.execute("DELETE FROM worldcup26.images")
    sa.connection.commit()
    sa.close_connection(cursor)

    assert url == image_url

def test_write_image_url():
    player_name = 'Vinicius Júnior'
    player_id = 184
    image_url = "https://example.com"
    ia = Images(player_name)
    ia.write_image_url(image_url)

    sa = SQLAccess()
    cursor = sa.create_connection()
    test_statement = ("SELECT * from worldcup26.images")
    cursor.execute(test_statement)
    sa.connection.commit()
    test_results = cursor.fetchall()

    # Clean up database
    cursor.execute("DELETE FROM worldcup26.images")
    sa.connection.commit()
    sa.close_connection(cursor)

    assert test_results[0][1] == image_url
    assert test_results[0][2] == player_id