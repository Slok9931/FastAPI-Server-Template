from sqlalchemy import Table, Column, Integer, ForeignKey
from src.config.database import Base

# Association table for many-to-many relationship between roles and modules
module_roles = Table(
    'module_roles',
    Base.metadata,
    Column('module_id', Integer, ForeignKey('modules.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)