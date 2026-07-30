import os
from sqlalchemy import create_engine

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://sentra:sentra_pass@localhost:5432/sentra_os"
)

engine = create_engine(DATABASE_URL, future=True)
