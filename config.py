from dataclasses import dataclass
from dotenv import load_dotenv
import os
load_dotenv()

@dataclass
class Config:
    model: str
    api_key: str
    base_url: str

model_config=Config(
    model=os.getenv('MODEL_NAME'),
    api_key=os.getenv('API_KEY'),
    base_url=os.getenv('BASE_URL')
)