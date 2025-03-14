# db/models/sqlalchemy_models.py

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.db_data import Data

# Проверяем наличие переменных окружения
Data.validate()
# Создаем движок SQLAlchemy
engine = create_engine(Data.DB_URL)
# Определяем базовый класс для моделей
Base = declarative_base()

# Определяем модель для таблицы postal_codes
class PostalCode(Base):
    __tablename__ = "postal_codes"

    post_code = Column(Integer, primary_key=True, Index=True)
    country = Column(String(60), nullable=False)
    country_abbreviation = Column(String(10), nullable=False)
    place_name = Column(String(100), nullable=False)
    longitude = Column(Float, nullable=False)
    state = Column(String(100), nullable=False)
    state_abbreviation = Column(String(10))
    latitude = Column(Float, nullable=False)

    def __repr__(self):
        return f"<PostalCode(postal_code='{self.postal_code}', place_name='{self.place_name}')>"

class PostalCodeRequestStatistics(Base):
    __tablename__ = "postal_codes_requests_statistics"

    postal_code = Column(Integer, primary_key=True, index=True)
    request_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<PostalCodeRequestStatistics(postal_code='{self.postal_code}', request_count={self.request_count})>"

Base.metadata.create_all(bind=engine)
# Создаем сессию
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция для получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()