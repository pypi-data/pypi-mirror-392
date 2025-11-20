# Copyright (C) 2020  Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""Unit tests for the message schema."""

from jsonschema import ValidationError

import pytest

from pagure_messages.git_schema import GitReceiveV1

from .utils import PROJECT


@pytest.fixture
def body():
    return {
        "agent": "dummy-user",
        "forced": False,
        "repo": PROJECT,
        "old_commit": "hash_commit_old",
        "branch": "refs/heads/develop",
        "authors": [
            {
                "fullname": "Dummy User",
                "url_path": "user/dummy-user",
                "name": "dummy-user",
                "email": "dummy-user@example.com",
            }
        ],
        "total_commits": 42,
        "start_commit": "hash_commit_start",
        "end_commit": "hash_commit_stop",
    }


def test_minimal(body):
    """
    Assert the message schema validates a message with the required fields.
    """
    message = GitReceiveV1(body=body)
    message.validate()
    assert message.url == (
        "http://localhost.localdomain/fedora-infra/fedocal-messages"
        "/c/hash_commit_old..hash_commit_stop"
    )
    assert message.packages == []
    assert message.containers == []
    assert message.modules == []
    assert message.flatpaks == []


def test_minimal_short_branch(body):
    """
    Assert the message schema validates a message with the required fields.
    """
    body["branch"] = "develop"
    message = GitReceiveV1(body=body)
    message.validate()
    assert message.url == (
        "http://localhost.localdomain/fedora-infra/fedocal-messages/"
        "c/hash_commit_old..hash_commit_stop"
    )


def test_missing_fields(body):
    """Assert an exception is actually raised on validation failure."""
    del body["agent"]
    message = GitReceiveV1(body=body)
    with pytest.raises(ValidationError):
        message.validate()


def test_str(body):
    """Assert __str__ produces a human-readable message."""
    expected_str = (
        "Dummy User (dummy-user) pushed 42 commits on "
        "fedora-infra/fedocal-messages.\n"
        "Branch: develop\n"
    )
    message = GitReceiveV1(body=body)
    message.validate()
    assert expected_str == str(message)


def test_summary(body):
    """Assert the summary is correct."""
    expected_summary = (
        "dummy-user pushed 42 commits on "
        "fedora-infra/fedocal-messages (branch: develop)"
    )
    message = GitReceiveV1(body=body)
    message.validate()
    assert expected_summary == message.summary


def test_url_one_commit(body):
    """
    Assert the URL is correct when a single commit was received.
    """
    body["total_commits"] = 1
    message = GitReceiveV1(body=body)
    message.validate()
    assert message.url == (
        "http://localhost.localdomain/fedora-infra/fedocal-messages"
        "/c/hash_commit_stop"
    )


def test_patch_url(body):
    """
    Assert the patch URL is correct when a single commit was received.
    """
    body["total_commits"] = 1
    message = GitReceiveV1(body=body)
    message.validate()
    assert message.patch_url == (
        "http://localhost.localdomain/fedora-infra/fedocal-messages"
        "/c/hash_commit_stop.patch"
    )


def test_patch_url_multiple_commits(body):
    """
    Assert the patch URL is correct when a single commit was received.
    """
    message = GitReceiveV1(body=body)
    message.validate()
    assert message.patch_url is None


@pytest.mark.parametrize(
    "namespace,msg_attr",
    [
        ("rpms", "packages"),
        ("containers", "containers"),
        ("modules", "modules"),
        ("flatpaks", "flatpaks"),
    ],
)
def test_artifacts(namespace, msg_attr):
    """
    Assert the message has the correct artifacts set
    """
    body = {
        "agent": "dummy-user",
        "forced": False,
        "repo": PROJECT.copy(),
        "old_commit": "hash_commit_old",
        "branch": "refs/heads/develop",
        "authors": [
            {
                "fullname": "dummy-user",
                "url_path": "user/dummy-user",
                "name": "dummy-user",
                "email": None,
            }
        ],
        "total_commits": 42,
        "start_commit": "hash_commit_start",
        "end_commit": "hash_commit_stop",
    }
    body["repo"]["namespace"] = namespace
    message = GitReceiveV1(body=body)

    for test_attr in ("packages", "containers", "modules", "flatpaks"):
        expected = ["fedocal-messages"] if msg_attr == test_attr else []
        assert getattr(message, test_attr) == expected
