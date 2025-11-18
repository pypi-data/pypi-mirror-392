#!/usr/bin/env python
# -*- coding: utf-8 -*-

__docformat__ = "restructuredtext en"

# pylint: disable=protected-access,too-many-public-methods

import unittest
from unittest.mock import patch as Patch

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import assert_that
from hamcrest import has_property
from hamcrest import contains_string



from zope import interface

from zope.location.interfaces import IRoot
from zope.location.interfaces import ILocation
from zope.location.interfaces import IContained
from zope.location.interfaces import LocationError
from zope.location.traversing import LocationPhysicallyLocatable

from nti.traversal.traversal import path_adapter
from nti.traversal.traversal import resource_path
from nti.traversal.traversal import find_interface
from nti.traversal.traversal import find_nearest_site
from nti.traversal.traversal import normal_resource_path
from nti.traversal.traversal import is_valid_resource_path

from nti.traversal.traversal import DefaultAdapterTraversable
from nti.traversal.traversal import ContainerAdapterTraversable

from nti.traversal.tests import SharedConfiguringTestLayer


class TestTraversal(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_unicode_resource_path(self):

        @interface.implementer(IRoot)
        class Root(object):
            __parent__ = None
            __name__ = None

        @interface.implementer(ILocation)
        class Middle(object):
            __parent__ = Root()
            __name__ = 'Middle'

        @interface.implementer(ILocation)
        class Leaf(object):
            __parent__ = Middle()
            __name__ = '\u2019'

        @interface.implementer(ILocation)
        class Invalid(object):
            __parent__ = Leaf()
            __name__ = None

        assert_that(resource_path(Leaf()),
                    is_('/Middle/%E2%80%99'))

        assert_that(normal_resource_path(Leaf()),
                    is_('/Middle/%E2%80%99'))

        root = find_interface(Leaf(), IRoot, strict=True)
        assert_that(root, is_not(none()))

        root = find_interface(Leaf(), IRoot, strict=False)
        assert_that(root, is_not(none()))

        with self.assertRaises(TypeError):
            resource_path(Invalid())

    def test_traversal_no_root(self):
        from zope.testing.loggingsupport import InstalledHandler
        @interface.implementer(ILocation)
        class Middle(object):
            __parent__ = None
            __name__ = 'Middle'

        @interface.implementer(ILocation)
        class Leaf(object):
            __parent__ = Middle()
            __name__ = '\u2019'

        log_handler = InstalledHandler('nti.traversal.traversal')
        self.addCleanup(log_handler.uninstall)

        try:
            with self.assertRaises(TypeError):
                resource_path(Leaf())
            # pylint: disable=unbalanced-tuple-unpacking
            record, = log_handler.records
            assert_that(record.getMessage(),
                        contains_string(".Middle"))
        finally:
            log_handler.close()

    @Patch('nti.traversal.traversal.path_adapter', autospec=True)
    def test_adapter_traversable(self, mock_pa):
        mock_pa.return_value = None

        @interface.implementer(IContained)
        class Root(object):
            __parent__ = None
            __name__ = 'Root'

        @interface.implementer(ILocation)
        class Middle(object):
            __parent__ = Root()
            __name__ = 'Middle'

            def get(self, key, default=None):
                if key == 'root':
                    return self.__parent__
                return default

        @interface.implementer(IContained)
        class Leaf(object):
            __parent__ = Middle()
            __name__ = 'Leaf'

        mid = Middle()
        c = ContainerAdapterTraversable(mid)
        assert_that(c, has_property('context', is_(mid)))
        assert_that(c, has_property('_container', is_(mid)))
        c.context = None
        assert_that(c, has_property('context', is_(none())))
        assert_that(c, has_property('_container', is_(none())))

        mid = Middle()
        request = object()
        c = ContainerAdapterTraversable(mid, request)
        assert_that(c.traverse('root', ''),
                    is_(Root))

        with self.assertRaises(LocationError):
            c.traverse('leaf', '')

        mock_pa.return_value = Leaf()
        assert_that(c.traverse('Leaf', ''),
                    is_(Leaf))

    def test_is_valid_resource_path(self):
        assert_that(is_valid_resource_path('https://bleach.org'),
                    is_(True))

    def test_find_nearest_site(self):
        marker = object()
        assert_that(find_nearest_site('https://bleach.org', marker),
                    is_(marker))

        @interface.implementer(ILocation)
        class Middle(object):
            __parent__ = None
            __name__ = 'Middle'

        @interface.implementer(ILocation)
        class Leaf(object):
            __parent__ = Middle()
            __name__ = '\u2019'
        assert_that(find_nearest_site(Leaf(), marker, ignore=ILocation),
                    is_(marker))

        with self.assertRaises(TypeError):
            find_nearest_site(Leaf(), marker)

        class Context(object):
            pass
        context = Context()
        # pylint: disable=attribute-defined-outside-init
        context.target = LocationPhysicallyLocatable(Leaf())
        assert_that(find_nearest_site(context, marker),
                    is_(marker))

    @Patch('nti.traversal.traversal.path_adapter', autospec=True)
    def test_default_traversable(self, mock_pa):
        @interface.implementer(IContained)
        class Root(object):
            __parent__ = object()
            __name__ = None

        @interface.implementer(ILocation)
        class Middle(object):
            __parent__ = Root()
            __name__ = 'Middle'

        mock_pa.return_value = Root()
        d = DefaultAdapterTraversable(Middle(), object())
        assert_that(d.traverse('Root', ''),
                    is_(Root))

    def test_coverage(self):
        assert_that(path_adapter(None, None), is_(none()))
