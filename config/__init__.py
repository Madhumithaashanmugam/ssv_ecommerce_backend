import os
from dotenv import load_dotenv,find_dotenv
env_folder=find_dotenv()
load_dotenv(env_folder)

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA")

ALGORITHM=os.getenv("ALGORITHM")
SECRET_KEY=os.getenv("SECRET_KEY")