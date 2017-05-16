# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2010 Joachim Hoessler <hoessler@gmail.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

import unittest
from trac.test import EnvironmentStub, Mock

from estimationtools.utils import EstimationToolsBase


class EstimationToolsBaseTestCase(unittest.TestCase):
    def test_disabled_without_estimation_field(self):
        class TestTool(EstimationToolsBase):
            pass

        env = EnvironmentStub(enable=['estimationtools.*'])
        messages = []
        env.log = Mock(error=lambda msg, *args: messages.append(msg % args))
        TestTool(env)
        self.assertEquals(False, env.is_enabled(TestTool))
        self.assertEquals(messages,
                          ['EstimationTools (TestTool): Estimation field not '
                           'configured. Component disabled.'])

    def test_enabled_with_estimation_field(self):
        class TestTool(EstimationToolsBase):
            pass

        env = EnvironmentStub()
        env.config.set('ticket-custom', 'hours_remaining', 'text')
        env.config.set('estimation-tools', 'estimation_field',
                       'hours_remaining')
        env.config.set('components', 'estimationtools.*', 'enabled')
        messages = []
        env.log = Mock(error=lambda msg, *args: messages.append(msg))
        TestTool(env)
        self.assertEquals(True, env.is_enabled(TestTool))
        self.assertEquals(messages, [])


def suite():
    return unittest.makeSuite(EstimationToolsBaseTestCase)


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
