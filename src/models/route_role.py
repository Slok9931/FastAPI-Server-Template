from sqlalchemy import Table, Column, Integer, ForeignKey
from src.config.database import Base

# Association table for many-to-many relationship between roles and routes
route_roles = Table(
    'route_roles',
    Base.metadata,
    Column('route_id', Integer, ForeignKey('routes.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)