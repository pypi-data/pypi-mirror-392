#!/usr/bin/env python
# -*- coding: utf-8 -*-


from repoze.lru import lru_cache

try:
    from pyramid.traversal import _segment_cache # pylint:disable=import-private-name
except ImportError:  # pragma: no cover
    _segment_cache = {}


PATH_SEGMENT_SAFE = "~!$&'()*+,;=:@"


def url_quote(val, safe=''):  # bw compat api
    import urllib.parse
    cls = val.__class__
    if cls is str:
        val = val.encode('utf-8')
    elif cls is not bytes:
        val = str(val).encode('utf-8')
    # pylint: disable=redundant-keyword-arg
    return urllib.parse.quote(val, safe=safe)


def native_(s, encoding='latin-1', errors='strict'):
    """
    If ``s`` is an instance of ``text_type``, return
    ``s``, otherwise return ``str(s, encoding, errors)``
    """
    if isinstance(s, str):
        return s
    return str(s, encoding, errors)

def quote_path_segment(segment, safe=PATH_SEGMENT_SAFE):
    """
    Return a quoted representation of a 'path segment'
    """
    try:
        return _segment_cache[(segment, safe)]
    except KeyError:
        if segment.__class__ not in (str, bytes):
            segment = str(segment)
        result = url_quote(native_(segment, 'utf-8'), safe)
        # we don't need a lock to mutate _segment_cache, as the below
        # will generate exactly one Python bytecode (STORE_SUBSCR)
        _segment_cache[(segment, safe)] = result
        return result


@lru_cache(1000)
def join_path_tuple(t):
    return '/'.join(quote_path_segment(x) for x in t) if t else '/'
