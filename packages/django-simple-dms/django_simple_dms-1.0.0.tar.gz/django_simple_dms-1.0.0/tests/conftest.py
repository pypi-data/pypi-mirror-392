import pytest

from testutils.factories import DocumentTagFactory


@pytest.fixture
def document_tags(db):
    return [
        DocumentTagFactory(),
        DocumentTagFactory(),
        DocumentTagFactory(),
    ]
