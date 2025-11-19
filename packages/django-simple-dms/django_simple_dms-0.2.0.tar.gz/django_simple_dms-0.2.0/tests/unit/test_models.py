import pytest
from django.core.exceptions import ValidationError

from testutils.factories import UserGrantFactory, DocumentTagFactory, GroupFactory


def test_document_grant_lower_str_for_user_granted():
    grant = UserGrantFactory.build(granted_permissions=['R', 'U'])
    g_system = str(grant).split(':')[2]
    grant.granted_by_system = False
    g_user = str(grant).split(':')[2]

    assert g_system == g_user.upper()


def test_document_tag_to_lower(db):
    dt = DocumentTagFactory(title='aNy-_.woRld0.')
    assert str(dt) == 'any-_.world0'


def test_tag_grant_clean(db):
    with pytest.raises(ValidationError, match=r'.*Invalid permissions\: [Z0]{2}.*'):
        UserGrantFactory.build(granted_permissions=['z', '0', 'U']).save()

    with pytest.raises(ValidationError, match='.*Cannot set both user and group.*'):
        UserGrantFactory.build(group=GroupFactory()).save()

    with pytest.raises(ValidationError, match='.*Must set either user or group.*'):
        UserGrantFactory.build(user=None).save()
