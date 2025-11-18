#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods,inherit-non-class

import unittest

from hamcrest import is_
from hamcrest import has_length
from hamcrest import assert_that

from zope import interface

from zope.interface import Interface
from zope.interface import directlyProvides

from zope.location.interfaces import ILocation

from nti.traversal.location import lineage
from nti.traversal.location import find_interface

from nti.traversal.tests import SharedConfiguringTestLayer


class Root(object):
    pass


@interface.implementer(ILocation)
class Location(object):
    __name__ = __parent__ = None


class TestLineage(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def _callFUT(self, context):
        return lineage(context)

    def test_lineage(self):
        o1 = Location()
        o2 = Location()
        o2.__parent__ = o1
        o3 = Location()
        o3.__parent__ = o2
        o4 = Location()
        o4.__parent__ = o3
        result = list(self._callFUT(o3))
        assert_that(result, is_([o3, o2, o1]))
        result = list(self._callFUT(o1))
        assert_that(result, is_([o1]))

        assert_that(list(self._callFUT(Root())),
                    has_length(1))

class DummyContext(object):

    __parent__ = None

    def __init__(self, next_=None, name=None):
        self.next = next_
        self.__name__ = name


class TestFindInterface(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def _callFUT(self, context, iface):
        return find_interface(context, iface)

    def test_it_interface(self):
        # pylint:disable=blacklisted-name
        baz = DummyContext()
        bar = DummyContext(baz)
        foo = DummyContext(bar)
        root = DummyContext(foo)
        root.__parent__ = None
        root.__name__ = 'root'
        foo.__parent__ = root
        foo.__name__ = 'foo'
        bar.__parent__ = foo
        bar.__name__ = 'bar'
        baz.__parent__ = bar
        baz.__name__ = 'baz'

        class IFoo(Interface):
            pass
        directlyProvides(root, IFoo)
        result = self._callFUT(baz, IFoo)
        self.assertEqual(result.__name__, 'root')

        result = self._callFUT(baz, DummyContext)
        self.assertEqual(result.__name__, 'baz')
