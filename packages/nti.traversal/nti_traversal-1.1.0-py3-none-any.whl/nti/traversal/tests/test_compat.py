#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods
import unittest

from hamcrest import is_
from hamcrest import assert_that

from nti.traversal.compat import native_
from nti.traversal.compat import url_quote
from nti.traversal.compat import quote_path_segment

from nti.traversal.tests import SharedConfiguringTestLayer


class TestCompat(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_url_quote(self):
        assert_that(url_quote('ichigo and azien'),
                    is_('ichigo%20and%20azien'))

        assert_that(url_quote('ichigo and azien'),
                    is_('ichigo%20and%20azien'))

        assert_that(url_quote(b'ichigo and azien'),
                    is_('ichigo%20and%20azien'))

        class Bleach(object):
            def __str__(self):
                return 'ichigo and azien'

        assert_that(url_quote(Bleach()),
                    is_('ichigo%20and%20azien'))

    def test_native(self):
        assert_that(native_('Ichigo', 'utf-8'),
                    is_('Ichigo'))
        assert_that(native_(b'Ichigo', 'utf-8'),
                    is_('Ichigo'))

    def test_quote_path_segment(self):
        assert_that(quote_path_segment('aizen'),
                    is_('aizen'))

        assert_that(quote_path_segment(b'ichigo'),
                    is_('ichigo'))

        assert_that(quote_path_segment('ichigo'),
                    is_('ichigo'))

        class Bleach(object):
            def __str__(self):
                return 'bleach'

        assert_that(quote_path_segment(Bleach()),
                    is_('bleach'))
