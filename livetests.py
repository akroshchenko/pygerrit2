#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The MIT License
#
# Copyright 2018 David Pursehouse. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Live server tests."""

import unittest
from pygerrit2.rest import GerritRestAPI, GerritReview
from requests.auth import HTTPBasicAuth
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class TestLiveServer(unittest.TestCase):
    """Test that GerritRestAPI behaves properly against a live server."""

    @wait_container_is_ready()
    def _connect(self, api):
        api.get("")

    def test_live_server(self):
        """Run tests against a server running in a Docker container."""
        gerrit = \
            DockerContainer("gerritcodereview/gerrit:2.14.8").\
            with_exposed_ports(8080)
        with gerrit:
            port = gerrit.get_exposed_port(8080)
            url = "http://localhost:%s" % port
            auth = HTTPBasicAuth("admin", "secret")
            api = GerritRestAPI(url=url, auth=auth)
            self._connect(api)
            self._run_tests(api)

    def _run_tests(self, api):
        """Run the tests."""
        # Create the project
        projectinput = {"create_empty_commit": "true"}
        api.put("/projects/test-project", json=projectinput)

        # Post with content as dict
        changeinput = {"project": "test-project",
                       "subject": "subject",
                       "branch": "master",
                       "topic": "topic"}
        change = api.post("/changes/", json=changeinput)
        id = change["id"]

        # Get
        api.get("/changes/" + id)

        # Put with content as string
        api.put("/changes/" + id + "/edit/foo", data="content")

        # Put with no content
        api.put("/changes/" + id + "/edit/foo")

        # Review by API
        rev = GerritReview()
        rev.set_message("Review from live test")
        rev.add_labels({"Code-Review": 1})
        api.review(id, "current", rev)


if __name__ == '__main__':
    unittest.main()