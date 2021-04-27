import dotenv
import os

from core import Associator, internal_download

dotenv.load_dotenv('./config.env')

if __name__ == '__main__':
    
    client = Associator(os.getenv('ANIME_URL', None), os.getenv('ANIME_FILLER_LIST_URL', None))
    internal_download(os.getenv('FOLDER_NAME', 'AnimDL Download'), client.fetch_appropriate(start=int(os.getenv('START') or 0) or None, end=int(os.getenv('END') or 0) or None, offset=int(os.getenv('ANIME_FILLER_LIST_OFFSET', 0) or 0), canon=bool(int(os.getenv('CANONS') or 0)), fillers=bool(int(os.getenv('FILLERS') or 0)), mixed_canon=bool(int(os.getenv('MIXED_CANONS_AND_FILLERS') or 0))))