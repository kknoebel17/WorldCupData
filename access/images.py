"""Image Access class used to get images for players."""

import os
from io import BytesIO
from pathlib import Path
from typing import Union

import requests
from dotenv import load_dotenv
from PIL import Image, ImageFile

from access.relational import SQLAccess

class Images:
    def __init__(self, player_name: str):
        self.sa = SQLAccess()
        self.player_name = player_name

    def get_image_url(self) -> Union[None, str]:
        """Get image URL for given player_name."""
        # Check that image url does not already exist
        sql_statement = """
                        SELECT worldcup26.images.image_url
                        FROM worldcup26.images
                        JOIN worldcup26.players ON worldcup26.players.player_id = worldcup26.images.player_id
                        WHERE worldcup26.players.player = %s
                        """
        cursor = self.sa.create_connection()
        cursor.execute(sql_statement, (self.player_name,))
        results = cursor.fetchall()
        self.sa.close_connection(cursor)

        return results

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