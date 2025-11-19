from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from django_simple_dms.models import DocumentTag


def solve_tags(tags: list[str | DocumentTag] = None) -> list[DocumentTag]:
    from django_simple_dms.models import DocumentTag

    if tags is None:
        return []

    return [DocumentTag.objects.get(title=tag.lower()) if isinstance(tag, str) else tag for tag in tags]
