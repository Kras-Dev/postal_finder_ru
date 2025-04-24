# Postal RU Finder Project

Title: Postal Indexer

## Description
This project is a console application that allows users to search for information about a name by postcode.
The application interacts with the PostgreSQL database using two approaches: through the psycopg2 driver and the
SQLAlchemy ORM. The Alembic tool is used to create and update the database structure. The project is implemented using
an object-oriented approach and automatically updates the database via the API. Includes tests using pytest and
unittest.mock.

## Technologies:
* psycopg2 and SQLAlchemy: For interaction with the PostgreSQL database. psycopg2 provides low-level access to 
    PostgreSQL, while SQLAlchemy offers an ORM for higher-level, object-oriented database interactions.
* Alembic: Used to manage database migrations and create or update the database structure.
* requests: Utilized for making HTTP GET requests to external APIs (e.g., Zippopotam API) to fetch postal code details.
* Pytest and Mock: For unit testing and mocking external dependencies.

## Resources
[Zippopotam API](https://api.zippopotam.us/): Used for API fetching data.

## Database Structure
* postal_codes: Stores information about postal codes.
* postal_codes_requests_statistics: Tracks statistics of requests.

## How to start

1. Clone the repository to your local computer.
2. Install the required dependencies.
```pip install -r requirements.txt```
3. Create database structures:
```alembic upgrade head```
4. Launching the application:
```python main.py```
5. Testing:
```python -m pytest```