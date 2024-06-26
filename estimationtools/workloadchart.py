# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2010 Joachim Hoessler <hoessler@gmail.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

import copy
from datetime import timedelta

from trac.util.html import html as tag
from trac.util.text import unicode_quote, unicode_urlencode, \
    obfuscate_email_address
from trac.wiki.macros import WikiMacroBase

from estimationtools.utils import parse_options, execute_query, \
    get_estimation_suffix, get_closed_states, \
    get_serverside_charts, EstimationToolsBase

DEFAULT_OPTIONS = {'width': '400', 'height': '100', 'color': 'ff9900'}


class WorkloadChart(EstimationToolsBase, WikiMacroBase):
    """Creates workload chart for the selected tickets.

    This macro creates a pie chart that shows the remaining estimated workload
    per ticket owner, and the remaining work days.

    It has the following parameters:
     * a comma-separated list of query parameters for the ticket selection, in
       the form "key=value" as specified in TracQuery#QueryLanguage.
     * `width`: width of resulting diagram (defaults to 400)
     * `height`: height of resulting diagram (defaults to 100)
     * `color`: color specified as 6-letter string of hexadecimal values in
       the format `RRGGBB`. Defaults to `ff9900`, a nice orange.

    Examples:
    {{{
    [[WorkloadChart(milestone=Sprint 1)]]
    [[WorkloadChart(milestone=Sprint 1, width=600, height=100, color=00ff00)]]
    }}}
    """

    estimation_suffix = get_estimation_suffix()
    closed_states = get_closed_states()
    serverside_charts = get_serverside_charts()

    def expand_macro(self, formatter, name, content, args=None):
        req = formatter.req
        # prepare options
        options, query_args = parse_options(self.env, content,
                                            copy.copy(DEFAULT_OPTIONS))

        query_args[self.remaining_field + "!"] = None
        tickets = execute_query(self.env, req, query_args)

        sum = 0.0
        estimations = {}
        for ticket in tickets:
            if ticket['status'] in self.closed_states:
                continue
            try:
                estimation = float(ticket[self.remaining_field])
                owner = ticket['owner']
                sum += estimation
                if owner in estimations:
                    estimations[owner] += estimation
                else:
                    estimations[owner] = estimation
            except:
                pass

        estimations_string = []
        labels = []
        for owner, estimation in estimations.iteritems():
            # Note: Unconditional obfuscation of owner in case it represents
            # an email adress, and as the chart API doesn't support SSL
            # (plain http transfer only, from either client or server).
            labels.append("%s %g%s" % (obfuscate_email_address(owner),
                                       round(estimation, 2),
                                       self.estimation_suffix))
            estimations_string.append(str(int(estimation)))

        # Title
        title = 'Workload'

        # calculate remaining work time
        if options.get('today') and options.get('enddate'):
            currentdate = options['today']
            day = timedelta(days=1)
            days_remaining = 0
            while currentdate <= options['enddate']:
                if currentdate.weekday() < 5:
                    days_remaining += 1
                currentdate += day
            title += ' %g%s (~%s workdays left)' % (round(sum, 2),
                                                    self.estimation_suffix,
                                                    days_remaining)

        chart_args = unicode_urlencode(
            {'chs': '%sx%s' % (options['width'], options['height']),
             'chf': 'bg,s,00000000',
             'chd': 't:%s' % ",".join(estimations_string),
             'cht': 'p3',
             'chtt': title,
             'chl': "|".join(labels),
             'chco': options['color']})
        self.log.debug("WorkloadChart data: %s", chart_args)
        if self.serverside_charts:
            return tag.image(
                src="%s?data=%s" % (req.href.estimationtools('chart'),
                                    unicode_quote(chart_args)),
                alt="Workload Chart (server)")
        else:
            return tag.image(
                src="https://image-charts.com/chart?%s" % chart_args,
                alt="Workload Chart (client)")
