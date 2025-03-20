# models/sqlalchemy_models.py

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

# Определяем базовый класс для моделей
Base = declarative_base()

class PostalCode(Base):
    """Модель для таблицы postal_codes в базе данных.

    Эта модель представляет информацию о почтовых кодах, включая страну,
    название места, координаты и другую связанную информацию."""
    __tablename__ = "postal_codes"

    post_code = Column(String(10), primary_key=True)
    country = Column(String(60), nullable=False)
    country_abbreviation = Column(String(10), nullable=False)
    place_name = Column(String(100), nullable=False)
    longitude = Column(Float, nullable=False)
    state = Column(String(100), nullable=False)
    state_abbreviation = Column(String(10))
    latitude = Column(Float, nullable=False)


class PostalCodeRequestStatistics(Base):
    """Модель для таблицы postal_codes_requests_statistics в базе данных.

    Эта модель хранит статистику запросов по почтовым кодам,
    включая количество запросов для каждого почтового кода."""
    __tablename__ = "postal_codes_requests_statistics"

    post_code = Column(String(10), primary_key=True)
    request_count = Column(Integer, default=0)

def create_tables(engine):
    """Метод создает таблицы в базе данных, если они еще не существуют."""
    # Создаем движок SQLAlchemy
    # engine = create_engine(Data.DB_URL)
    Base.metadata.create_all(bind=engine, checkfirst=True)

