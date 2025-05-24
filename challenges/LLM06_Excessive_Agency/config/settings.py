import os

class Config:
    BOX_CLIENT_ID = os.getenv('BOX_CLIENT_ID')
    BOX_CLIENT_SECRET = os.getenv('BOX_CLIENT_SECRET')
    BOX_ACCESS_TOKEN = os.getenv('BOX_ACCESS_TOKEN')
