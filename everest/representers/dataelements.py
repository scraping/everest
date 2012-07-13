"""
This file is part of the everest project.
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Data element classes.

Created on Apr 25, 2012
"""
from collections import OrderedDict
from everest.representers.base import data_element_tree_to_string
from everest.representers.converters import SimpleConverterRegistry
from everest.representers.interfaces import ICollectionDataElement
from everest.representers.interfaces import ILinkedDataElement
from everest.representers.interfaces import IMemberDataElement
from everest.representers.interfaces import IResourceDataElement
from everest.resources.attributes import ResourceAttributeKinds
from everest.resources.kinds import ResourceKinds
from everest.resources.utils import provides_collection_resource
from everest.resources.utils import provides_member_resource
from everest.url import resource_to_url
from everest.url import url_to_resource
from zope.interface import implements # pylint: disable=E0611,F0401
from zope.interface import providedBy as provided_by # pylint: disable=E0611,F0401

__docformat__ = 'reStructuredText en'
__all__ = ['CollectionDataElement',
           'DataElement',
           'DataElementAttributeProxy',
           'LinkedDataElement',
           'MemberDataElement',
           'SimpleCollectionDataElement',
           'SimpleLinkedDataElement',
           'SimpleMemberDataElement',
           ]


class DataElement(object):
    """
    Abstract base class for data element classes.

    Data elements manage value state during serialization and deserialization.
    Implementations may need to be adapted to the format of the external
    representation they manage.
    """

    implements(IResourceDataElement)

    #: Static attribute mapping.
    mapping = None

    @classmethod
    def create(cls):
        """
        Basic factory method.
        """
        inst = cls()
        return inst

    @classmethod
    def create_from_resource(cls, resource):
        """
        (Abstract) factory method taking a resource as input.
        """
        raise NotImplementedError('Abstract method.')

    def __str__(self):
        return data_element_tree_to_string(self)


class MemberDataElement(DataElement):
    """
    Abstract base class for member data element classes.
    """

    implements(IMemberDataElement)

    def get_mapped_terminal(self, attr):
        """
        Returns the value for the given mapped terminal resource attribute.

        :param attr: attribute to retrieve.
        :type attr: :class:`everest.representers.attributes.MappedAttribute`
        :returns: attribute value or `None` if no value is found for the given
            attribute name.
        """
        raise NotImplementedError('Abstract method.')

    def set_mapped_terminal(self, attr, value):
        """
        Sets the value for the given mapped terminal resource attribute.

        :type attr: :class:`everest.representers.attributes.MappedAttribute`
        :param value: value of the attribute to set.
        """
        raise NotImplementedError('Abstract method.')

    def get_mapped_nested(self, attr):
        """
        Returns the mapped nested resource attribute (either a member or a
        collection resource attribute).

        :type attr: :class:`everest.representers.attributes.MappedAttribute`
        :returns: object implementing `:class:IDataelement` or
          `None` if no nested resource is found for the given attribute name.
        """
        raise NotImplementedError('Abstract method.')

    def set_mapped_nested(self, attr, data_element):
        """
        Sets the value for the given mapped nested resource attribute (either
        a member or a collection resource attribute).

        :type attr: :class:`everest.representers.attributes.MappedAttribute`
        :param data_element: a :class:DataElement or :class:LinkedDataElement
          object containing nested resource data.
        """
        raise NotImplementedError('Abstract method.')


class CollectionDataElement(DataElement):
    """
    Abstract base class for collection data elements.
    """

    implements(ICollectionDataElement)

    def add_member(self, data_element):
        """
        Adds the given member data element to this collection data element.
        """
        raise NotImplementedError('Abstract method.')

    def get_members(self):
        """
        Returns all member data elements added to this collection data element.
        """
        raise NotImplementedError('Abstract method.')

    def __len__(self):
        """
        Returns the number of member data elements in this collection data
        element.
        """
        raise NotImplementedError('Abstract method.')


class _SimpleDataElementMixin(object):
    @classmethod
    def create_from_resource(cls, resource): # ignore resource pylint:disable=W0613,W0221
        return cls()


class SimpleMemberDataElement(_SimpleDataElementMixin, MemberDataElement):
    """
    Basic implementation of a member data element.
    """
    __data = None

    @property
    def terminals(self):
        if self.__data is None:
            self.__data = OrderedDict()
        return OrderedDict((k, v)
                           for (k, v) in self.__data.iteritems()
                           if not isinstance(v, DataElement))

    @property
    def nesteds(self):
        if self.__data is None:
            self.__data = OrderedDict()
        return OrderedDict((k, v)
                           for (k, v) in self.__data.iteritems()
                           if isinstance(v, DataElement))

    @property
    def data(self):
        if self.__data is None:
            self.__data = OrderedDict()
        return self.__data

    def get_terminal(self, attr_name):
        """
        Returns the (raw) value of the specified attribute.
        
        :param str attr_name: name of the attribute to retrieve.
        """
        return self.data.get(attr_name)

    def set_terminal(self, attr_name, value):
        """
        Sets the (raw) value of the specified attribute.

        :param str attr_name: name of the attribute to set.
        :param str value: value of the attribute to set.
        """
        self.data[attr_name] = value

    def get_nested(self, attr_name):
        """
        Returns the (raw) value of the specified attribute.
        
        :param str attr_name: name of the attribute to retrieve.
        """
        return self.data[attr_name]

    def set_nested(self, attr_name, data_element):
        """
        Sets the (raw) value of the specified attribute.

        :param str attr_name: name of the attribute to set.
        @param data_element: a :class:DataElement or :class:LinkedDataElement
          object containing nested resource data.
        """
        self.data[attr_name] = data_element

    def get_mapped_terminal(self, attr):
        rpr_val = self.data.get(attr.repr_name)
        return SimpleConverterRegistry.convert_from_representation(
                                                            rpr_val,
                                                            attr.value_type)

    def set_mapped_terminal(self, attr, value):
        rpr_val = SimpleConverterRegistry.convert_to_representation(
                                                            value,
                                                            attr.value_type)
        self.data[attr.repr_name] = rpr_val

    def get_mapped_nested(self, attr):
        return self.data.get(attr.repr_name)

    def set_mapped_nested(self, attr, data_element):
        self.data[attr.repr_name] = data_element


class SimpleCollectionDataElement(_SimpleDataElementMixin,
                                  CollectionDataElement):
    """
    Basic implementation of a collection data element.
    """
    __members = None

    def add_member(self, data_element):
        self.members.append(data_element)

    def get_members(self):
        return self.members

    @property
    def members(self):
        if self.__members is None:
            self.__members = []
        return self.__members

    def __len__(self):
        return len(self.__members)


class LinkedDataElement(DataElement):
    """
    Data element managing a linked resource during serialization and
    deserialization.
    """

    implements(ILinkedDataElement)

    @classmethod
    def create(cls, url, kind, relation=None, title=None, **options):
        raise NotImplementedError('Abstract method.')

    @classmethod
    def create_from_resource(cls, resource):
        raise NotImplementedError('Abstract method.')

    def get_url(self):
        raise NotImplementedError('Abstract method.')

    def get_kind(self):
        raise NotImplementedError('Abstract method.')

    def get_relation(self):
        raise NotImplementedError('Abstract method.')

    def get_title(self):
        raise NotImplementedError('Abstract method.')


class SimpleLinkedDataElement(LinkedDataElement):
    """
    Basic implementation of a linked data element.
    """
    __url = None
    __kind = None
    __relation = None
    __title = None

    @classmethod
    def create(cls, url, kind, relation=None, title=None, **options):
        inst = cls()
        inst.__url = url
        inst.__kind = kind
        inst.__relation = relation
        inst.__title = title
        return inst

    @classmethod
    def create_from_resource(cls, resource):
        if provides_member_resource(resource):
            kind = ResourceKinds.MEMBER
        elif provides_collection_resource(resource):
            kind = ResourceKinds.COLLECTION
        else:
            raise ValueError('"%s" is not a resource.' % resource)
        return cls.create(resource_to_url(resource), kind,
                          relation=resource.relation,
                          title=resource.title)

    def get_url(self):
        return self.__url

    def get_kind(self):
        return self.__kind

    def get_relation(self):
        return self.__relation

    def get_title(self):
        return self.__title


class DataElementAttributeProxy(object):
    """
    Convenience proxy for accessing data from data elements.
    
    The proxy allows you to transparently access terminal, member, and
    collection attributes. Nested access is also supported.
    
    Example: ::
    
    prx = DataElementAttributeProxy(data_element)
    de_id = prx.id                              # terminal access
    de_parent = prx.parent                      # member access
    de_child = prx.children[0]                  # collection access
    de_grandchild = prx.children[0].children[0] # nested collection access
    """
    def __init__(self, data_element):
        if ILinkedDataElement in provided_by(data_element):
            raise ValueError('Do not use data element proxies with linked '
                             'data elements.')
        self.__data_element = data_element
        attrs = data_element.mapping.attribute_iterator()
        self.__attr_map = dict([(attr.repr_name, attr) for attr in attrs])

    def __getattr__(self, name):
        try:
            attr = self.__attr_map[name]
        except KeyError:
            raise AttributeError(name)
        else:
            if attr.kind == ResourceAttributeKinds.TERMINAL:
                value = self.__data_element.get_mapped_terminal(attr)
            else:
                nested_data_el = self.__data_element.get_mapped_nested(attr)
                if nested_data_el is None:
                    value = None
                elif ILinkedDataElement in provided_by(nested_data_el):
                    try:
                        value = url_to_resource(nested_data_el.get_url())
                    except KeyError: # traversal did not find anything.
                        value = None
                elif attr.kind == ResourceAttributeKinds.MEMBER:
                    value = DataElementAttributeProxy(nested_data_el)
                else:
                    value = [DataElementAttributeProxy(mb_el)
                             for mb_el in nested_data_el.get_members()]
        return value