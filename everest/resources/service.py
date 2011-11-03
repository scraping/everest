"""
This file is part of the everest project. 
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Service class.

Created on Jul 27, 2011.
"""

from everest.resources.base import RELATION_BASE_URL
from everest.resources.base import Resource
from everest.resources.interfaces import IService
from everest.resources.utils import get_collection
from zope.component import getUtility as get_utility # pylint: disable=E0611,F0401
from zope.interface import Interface # pylint: disable=E0611,F0401
from zope.interface import implements # pylint: disable=E0611,F0401

__docformat__ = 'reStructuredText en'
__all__ = ['Service',
           ]


class Service(Resource):
    """
    Class for the document describing the Atompub service.

    A service is a collection of collections and always returns a
    clone of its contents.
    """
    implements(IService)

    relation = RELATION_BASE_URL

    def __init__(self, name):
        Resource.__init__(self)
        self.__name__ = name
        self.__collections = {}

    def __getitem__(self, key):
        """
        Overrides __getitem__ to return a clone of the contained resource.

        :param key: collection interface or name.
        :returns: instance of :class:`everest.resources.Collection`.
        """
        coll = self.__collections[key]
        return coll.clone()

    def __len__(self):
        return len(self.__collections) / 2

    def __iter__(self):
        for key, value in self.__collections.iteritems():
            if isinstance(key, basestring):
                yield value

    def add(self, collection):
        if isinstance(collection, type(Interface)):
            collection = get_utility(collection, 'collection-class')
        if collection in self.__collections:
            raise ValueError('Root collection for collection interface %s '
                             ' already exists.' % collection.__name__)
        coll = get_collection(collection)
        if coll.__name__ in self.__collections:
            raise ValueError('Root collection with name %s already exists.' %
                             coll.__name__)
        coll.__parent__ = self
        # Allow access by collection class and name.
        self.__collections[collection] = coll
        self.__collections[coll.__name__] = coll

    def remove(self, collection):
        if isinstance(collection, type(Interface)):
            collection = get_utility(collection, 'collection-class')
        if not collection in self.__collections:
            raise ValueError('Root collection for collection interface %s '
                             'is not in this service.' % collection.__name__)
        coll = self.__collections[collection]
        del self.__collections[coll]
        del self.__collections[coll.__name__]

    def get(self, name, default=None):
        try:
            coll = self.__getitem__(name)
        except KeyError:
            coll = default
        return coll

