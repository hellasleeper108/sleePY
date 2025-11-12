"""
Database base class and declarative base
"""
from sqlalchemy.ext.declarative import declarative_base

# Create declarative base for all models
Base = declarative_base()
