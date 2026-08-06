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
        self.cursor = self.sa.create_connection()
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
        self.cursor.execute(sql_statement, (self.player_name,))
        results = self.cursor.fetchall()

        return results

    def write_image_url(self, image_url: str) -> None:
        """Write image URL to database for given player_name."""
        # Get player id
        id_sql_statement = """
                        SELECT worldcup26.players.player_id FROM worldcup26.players
                        WHERE worldcup26.players.player = %s \
                        """
        self.cursor.execute(id_sql_statement, (self.player_name,))
        results = self.cursor.fetchall()
        player_id = results[0][0]
        # Write image_url
        if image_url:
            insert_sql_statement = """
            INSERT INTO worldcup26.images (image_url, player_id)
            values (%s, %s)
            """
            try:
                self.cursor.execute(insert_sql_statement, (image_url, player_id))
                self.sa.connection.commit()
            except Exception as e:
                print(e)
        else:
            print(f"Image from {image_url} is empty.")


    def get_image(self) -> Union[str, ImageFile]:
        load_dotenv()
        api_key = str(os.getenv("IMAGES_API_KEY"))
        image_url = self.get_image_url()
        if image_url:
            return image_url[0][0]
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
                    # Write image url to database
                    self.write_image_url(image_url)
                else:
                    image_path = Path('images.png')
                    image = Image.open(image_path)

                self.sa.close_connection(self.cursor)

                return image
            else:
                self.sa.close_connection(self.cursor)
                return f"Failed to retrieve image. Status code: {response.status_code}"
        except Exception as e:
            self.sa.close_connection(self.cursor)
            return e