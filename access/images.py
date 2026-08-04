"""Image Access class used to get images for players."""

import os
from io import BytesIO
from pathlib import Path
from typing import Union

import requests
from dotenv import load_dotenv
from PIL import Image, ImageFile

class Images:
    def __init__(self, player_name: str):
        self.player_name = player_name

    def get_image(self) -> Union[str, ImageFile]:
        load_dotenv()
        api_key = str(os.getenv("IMAGES_API_KEY"))
        try:
            response = requests.get(
                "https://api.openwebninja.com/realtime-image-search/search",
                headers={
                    "x-api-key": api_key,
                },
                params={
                    "query": self.player_name,
                    'limit': 1,
                    'size': 'medium',
                    'safe_search': 'on'
                }
            )

            # Check if the download was successful
            if response.status_code == 200:
                image_json = response.json()
                image_url = image_json['data'][0]['thumbnail_url']
                image_data = requests.get(image_url)
                if image_data.content:
                    # Save the binary content into a file
                    image = Image.open(BytesIO(image_data.content))
                else:
                    image_path = Path('images.png')
                    image = Image.open(image_path)

                return image
            else:
                return f"Failed to retrieve image. Status code: {response.status_code}"
        except Exception as e:
            return e