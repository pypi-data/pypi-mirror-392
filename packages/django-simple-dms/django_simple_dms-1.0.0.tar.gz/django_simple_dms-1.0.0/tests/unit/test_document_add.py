from pathlib import Path

import pytest

from django_simple_dms.exceptions import ForbiddenException
from django_simple_dms.models import Document
from testutils.factories import TagGrantFactory, UserFactory
from contextlib import nullcontext as does_not_raise


@pytest.mark.parametrize(
    'doc',
    [
        pytest.param('file', id='pathname'),
        pytest.param('open', id='handle'),
        pytest.param('path', id='path'),
    ],
)
def test_document_add_local_file(doc, db) -> None:
    if doc == 'file':
        doc_obj = Document.add(document=doc)
    elif doc == 'path':
        doc_obj = Document.add(document=Path(__file__))
    else:
        with open(__file__, 'rb') as f:
            doc_obj = Document.add(document=f)

    assert doc_obj.id is not None


@pytest.mark.parametrize(
    'create, error',
    [
        pytest.param(True, False, id='ok'),
        pytest.param(False, True, id='nok'),
    ],
)
def test_create_with_tags(create, error, db) -> None:
    t1 = TagGrantFactory(create=create, defaults=['R', 'U'])
    t2 = TagGrantFactory(defaults=['D'])
    t3 = TagGrantFactory(create=create, defaults=[])  # will not create a DocumentGrant

    u = UserFactory()
    u.groups.add(t1.group)
    u.groups.add(t2.group)
    u.groups.add(t3.group)

    expectation = (
        pytest.raises(ForbiddenException, match=f'Unable to create document with tags: {t1.tag}, {t3.tag}')
        if error
        else does_not_raise()
    )

    with expectation:
        doc_obj = Document.add(actor=u, document=__file__, tags=[t1.tag, t2.tag.title.upper(), t3.tag])
        assert doc_obj.id is not None

        doc_grant_values = doc_obj.documentgrant_set.values_list('group', 'granted_permissions', 'grantor')
        assert list(doc_grant_values) == [
            (t1.group.id, ['R', 'U'], u.id),
            (t2.group.id, ['D'], u.id),
        ]
