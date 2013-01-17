"""


This file is part of the everest project. 
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Jan 7, 2013.
"""
from everest.datastores.base import DataStore
from everest.datastores.orm.session import OrmSessionFactory
from everest.datastores.orm.utils import empty_metadata
from everest.datastores.utils import get_engine
from everest.datastores.orm.utils import get_metadata
from everest.datastores.utils import is_engine_initialized
from everest.datastores.orm.utils import is_metadata_initialized
from everest.datastores.orm.utils import map_system_entities
from everest.datastores.utils import set_engine
from everest.datastores.orm.utils import set_metadata
from sqlalchemy.engine import create_engine
from sqlalchemy.pool import StaticPool

__docformat__ = 'reStructuredText en'
__all__ = ['OrmDataStore',
           ]


class OrmDataStore(DataStore):
    """
    Data store connected to a relational database backend (through an ORM).
    """
    _configurables = DataStore._configurables \
                     + ['db_string', 'metadata_factory']

    def __init__(self, name,
                 autoflush=True, join_transaction=True, autocommit=False):
        DataStore.__init__(self, name, autoflush=autoflush,
                           join_transaction=join_transaction,
                           autocommit=autocommit)
        # Default to an in-memory sqlite DB.
        self.configure(db_string='sqlite://', metadata_factory=empty_metadata)

    def _initialize(self):
        # Manages an ORM engine and a metadata instance for this entity store.
        # Both are global objects that should only be created once per process
        # (for each ORM entity store), hence we use a global object manager.
        if not is_engine_initialized(self.name):
            engine = self.__make_engine()
            set_engine(self.name, engine)
            # Bind the engine to the session factory and the metadata.
            self.session_factory.configure(bind=engine)
        else:
            engine = get_engine(self.name)
        if not is_metadata_initialized(self.name):
            md_fac = self._config['metadata_factory']
            if self._config.get('messaging_enable', False):
                # Wrap the metadata callback to also call the mapping
                # function for system entities.
                reset_on_start = \
                    self._config.get('messaging_reset_on_start', False)
                def wrapper(engine, reset_on_start=reset_on_start):
                    metadata = md_fac(engine)
                    map_system_entities(engine, metadata, reset_on_start)
                    return metadata
                metadata = wrapper(engine)
            else:
                metadata = md_fac(engine)
            set_metadata(self.name, metadata)
        else:
            metadata = get_metadata(self.name)
        metadata.bind = engine

    def _make_session_factory(self):
        return OrmSessionFactory(self)

    def __make_engine(self):
        db_string = self._config['db_string']
        if db_string.startswith('sqlite://'):
            # Enable connection sharing across threads for pysqlite.
            kw = {'poolclass':StaticPool,
                  'connect_args':{'check_same_thread':False}
                  }
        else:
            kw = {}  # pragma: no cover
        return create_engine(db_string, **kw)
