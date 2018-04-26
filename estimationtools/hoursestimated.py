# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2010 Joachim Hoessler <hoessler@gmail.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from trac.wiki.api import parse_args
from trac.wiki.macros import WikiMacroBase

from estimationtools.utils import EstimationToolsBase, execute_query


class HoursEstimated(EstimationToolsBase, WikiMacroBase):
    """Calculates estimated hours for the queried tickets.

    The macro accepts a comma-separated list of query parameters for the ticket selection,
    in the form "key=value" as specified in TracQuery#QueryLanguage.

    Example:
    {{{
        [[HoursEstimated(milestone=Sprint 1)]]
    }}}
    """

    def expand_macro(self, formatter, name, content):
        req = formatter.req
        _ignore, options = parse_args(content, strict=False)

        # we have to add custom estimated field to query so that field is added to
        # resulting ticket list
        options[self.estimation_field + "!"] = None

        tickets = execute_query(self.env, req, options)

        sum = 0.0
        for t in tickets:
            try:
                sum += float(t[self.estimation_field])
            except:
                pass

        return "%g" % round(sum, 2)
