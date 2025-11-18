#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module is deprecated. It contains functions that
ignore errors in the location hierarchy. That can be a serious
problem and must not be ignored.

Prefer the functions in :mod:`nti.traversal.traversal`.
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope.interface.interfaces import IInterface

logger = __import__('logging').getLogger(__name__)


def lineage(resource):
    """
    Return all the parents of *resource*.

    Deprecated, do not use.

    .. deprecated:: 1.0
       This doesn't use the :class:`zope.location.interfaces.ILocationInfo`
       interface, and hence doesn't let the *resource* have customizations
       and ignores problems in the resource tree.
    """
    while resource is not None:
        yield resource
        try:
            resource = resource.__parent__
        except AttributeError:
            resource = None


def find_interface(resource, class_or_interface): # pylint:disable=inconsistent-return-statements
    """
    Search for an object implementing *class_or_interface* in the
    :func:`lineage` of the *resource*.

    :param class_or_interface: Can be an interface or a
       concrete class to check with :func:`isinstance`.


    Deprecated, do not use.

    .. deprecated:: 1.0
       This doesn't use the :class:`zope.location.interfaces.ILocationInfo`
       interface, and hence doesn't let the *resource* have customizations
       and ignores problems in the resource tree.
    """
    if IInterface.providedBy(class_or_interface):
        test = class_or_interface.providedBy
    else:
        def test(arg):
            return isinstance(arg, class_or_interface)

    for location in lineage(resource):
        if test(location):
            return location
