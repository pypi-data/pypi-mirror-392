#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generic traversal functions (and adapters).
"""

import warnings
import logging

from zope.interface import implementer
from zope.component import queryMultiAdapter

from zope.location import LocationIterator

from zope.location.interfaces import IContained
from zope.location.interfaces import ILocationInfo

from zope.traversing.adapters import DefaultTraversable as _DefaultTraversable

from zope.traversing.interfaces import IPathAdapter
from zope.traversing.interfaces import ITraversable

from zope.traversing.namespace import adapter

from nti.traversal.compat import join_path_tuple

from nti.traversal.location import find_interface as _p_find_interface

logger = logging.getLogger(__name__)

__all__ = [
    'resource_path',
    'normal_resource_path',
    'is_valid_resource_path',
    'find_nearest_site',
    'find_interface',
    # TODO: The adapters should go in adapters.py
    'path_adapter',
    'adapter_request',
    'ContainerAdapterTraversable',
    'DefaultAdapterTraversable',
]
# pylint:disable=assignment-from-no-return

try:
    from zope.container.traversal import ContainerTraversable as _ContainerTraversable
except ModuleNotFoundError:
    from zope.traversing.interfaces import TraversalError
    _marker = object()
    @implementer(ITraversable)
    class _ContainerTraversable:
        """Traverses containers via `getattr` and `get`."""

        def __init__(self, container):
            self._container = container

        def traverse(self, name, furtherPath): # pylint: disable=unused-argument
            container = self._container

            v = container.get(name, _marker)
            if v is _marker:
                try:
                    # Note that if name is a unicode string, getattr will
                    # implicitly try to encode it using the system
                    # encoding (usually ascii). Failure to encode means
                    # invalid attribute name.
                    v = getattr(container, name, _marker)
                except UnicodeEncodeError:
                    raise TraversalError(container, name) from None
                if v is _marker:
                    raise TraversalError(container, name)

            return v

def resource_path(res):
    # This function is somewhat more flexible than Pyramid's, and
    # also more strict. It requires strings (not None, for example)
    # and bottoms out at an IRoot. This helps us get things right.
    # It is probably also a bit slower.
    # Could probably use a __traceback_supplement__ for this
    _known_parents = []

    # Ask for the parents; we do this instead of getPath() and url_quote
    # to work properly with unicode paths through the magic of pyramid
    loc_info = ILocationInfo(res)
    try:
        # pylint: disable=too-many-function-args
        parents = loc_info.getParents()
    except TypeError:  # "Not enough context information to get all parents"
        # This is a programming/design error: some object is not where it
        # should be
        _known_parents.extend(LocationIterator(res))
        logger.exception("Failed to get all parents of %r; known parents: %s",
                         res, _known_parents)
        raise

    if parents:
        # Take the root off, it's implicit and has a name of None
        parents.pop()

    # Put it in the order pyramid expects, root first
    # (root is added only to the names to avoid prepending)
    parents.reverse()
    parents.append(res)
    # And let pyramid construct the URL, doing proper escaping and
    # also caching.
    names = ['']  # Bottom out at the root
    for p in parents:
        name = p.__name__
        if name is None:
            __traceback_info__ = p
            raise TypeError("Element in the hierarchy is missing __name__")
        names.append(name)
    return join_path_tuple(tuple(names))


def normal_resource_path(res):
    """
    :return: The result of traversing the containers of `res`,
    but normalized by removing double slashes. This is useful
    when elements in the containment hierarchy do not have
    a name; however, it can hide bugs when all elements are expected
    to have names.
    """
    # If this starts to get complicated, we can take a dependency
    # on the urlnorm library
    result = resource_path(res)
    result = result.replace('//', '/')
    # Our LocalSiteManager is sneaking in here, which we don't want...
    # result = result.replace( '%2B%2Betc%2B%2Bsite/', '' )
    return result


def is_valid_resource_path(target):
    # We really want to check if this is a valid HTTP URL path. How best to do that?
    # Not documented until we figure it out.
    return isinstance(target, str) and (target.startswith('/') or
                                        target.startswith('http://') or
                                        target.startswith('https://'))


def find_nearest_site(context, root=None, ignore=None):
    """
    Find the nearest :class:`ISite` in the lineage of *context*.

    :param context: The object whose lineage to search.
        If this object cannot be adapted to `ILocationInfo`, then we attempt
        to adapt ``context.target`` and get its site; failing that, we return the
        *root*.
    :param ignore: If the `ILocationInfo` of the *context* can be
       retrieved, but the :meth:`.ILocationInfo.getNearestSite` cannot, then,
       if *ignore* is given, and *context* provides that interface,
       return the *root*. This makes no sense and is deprecated.
    :return: The nearest site. Possibly the root site.

    .. deprecated:: 1.0
       Relying on the fallback to ``context.target`` and *root* is deprecated;
       the *ignore* parameter is deprecated. All of these things signal a broken
       resource tree.
    """
    try:
        loc_info = ILocationInfo(context)
    except TypeError:
        # Not adaptable (not located). What about the target?
        try:
            # pylint: disable=too-many-function-args
            loc_info = ILocationInfo(context.target)
            warnings.warn(
                "Relying on ``context.target`` is deprecated. "
                "Register an ILocationInfo adapter for ``context`` instead.",
                FutureWarning,
                stacklevel=2
            )
            nearest_site = loc_info.getNearestSite()
        except (TypeError, AttributeError):
            # Nothing. Assume the main site/root
            nearest_site = root
    else:
        # Located. Better be able to get a site, otherwise we have a
        # broken chain.
        try:
            # pylint: disable=too-many-function-args
            nearest_site = loc_info.getNearestSite()
        except TypeError:
            # Convertible, but not located correctly.
            if ignore is None or not ignore.providedBy(context):
                raise
            warnings.warn(
                "The ignore argument is deprecated. "
                "Register an appropriate ILocationInfo instead.",
                FutureWarning,
                stacklevel=2
            )
            nearest_site = root

    return nearest_site



def find_interface(resource, interface, strict=True): # pylint:disable=inconsistent-return-statements
    """
    Given an object, find the first object in its lineage providing
    the given interface.

    This is similar to :func:`nti.traversal.location.find_interface`,
    but, as with :func:`resource_path` requires the strict adherence
    to the resource tree, unless ``strict`` is set to ``False``.

    :keyword bool strict: Deprecated. Do not use. Non-strict
        lineage is broken lineage.
    """
    if not strict:
        return _p_find_interface(resource, interface)
    # pylint: disable=too-many-function-args
    lineage = ILocationInfo(resource).getParents()
    lineage.insert(0, resource)
    for item in lineage:
        if interface.providedBy(item):
            return item



def path_adapter(context, request, name=''):
    return queryMultiAdapter((context, request), IPathAdapter,
                             name)


class adapter_request(adapter):
    """
    Implementation of the adapter namespace that attempts to pass the
    request along when getting an adapter.
    """

    def __init__(self, context, request=None):
        super().__init__(context, request)
        self.request = request

    def traverse(self, name, ignored):
        result = None
        if self.request is not None:
            result = path_adapter(self.context, self.request, name)

        if result is None:
            # Look for the single-adapter. Or raise location error
            result = super().traverse(name, ignored)

        # Some sanity checks on the returned object
        # pylint: disable=unused-variable
        __traceback_info__ = result, self.context, result.__parent__, result.__name__

        assert IContained.providedBy(result) # pylint:disable=no-value-for-parameter
        assert result.__parent__ is not None

        if result.__name__ is None:
            result.__name__ = name
        assert result.__name__ == name

        return result


@implementer(ITraversable)
class ContainerAdapterTraversable(_ContainerTraversable):
    """
    A :class:`ITraversable` implementation for containers that also
    automatically looks for named path adapters *if* the container
    has no matching key.

    You may subclass this traversable or register it in ZCML
    directly. It is usable both with and without a request.
    """

    context = property(lambda self: getattr(self, "_container"),
                       lambda self, nv: setattr(self, "_container", nv))

    def __init__(self, context, request=None):
        super().__init__(context)
        self.context = context
        self.request = request

    def traverse(self, key, remaining_path):  # pylint: disable=arguments-renamed
        try:
            return super().traverse(key, remaining_path)
        except KeyError:
            # Is there a named path adapter?
            adapted = adapter_request(self.context, self.request)
            return adapted.traverse(key, remaining_path)


@implementer(ITraversable)
class DefaultAdapterTraversable(_DefaultTraversable):
    """
    A :class:`ITraversable` implementation for ordinary objects that also
    automatically looks for named path adapters *if* the traversal
    found no matching path.

    You may subclass this traversable or register it in ZCML
    directly. It is usable both with and without a request.
    """

    def __init__(self, context, request=None):
        super().__init__(context)
        self.context = context
        self.request = request

    def traverse(self, key, remaining_path):  # pylint: disable=arguments-renamed
        try:
            return super().traverse(key, remaining_path)
        except KeyError:
            # Is there a named path adapter?
            adapted = adapter_request(self.context, self.request)
            return adapted.traverse(key, remaining_path)
