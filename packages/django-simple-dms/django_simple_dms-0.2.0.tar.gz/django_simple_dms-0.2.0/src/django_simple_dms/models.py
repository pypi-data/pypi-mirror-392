import typing

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.postgres.fields import DateRangeField, ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils.regex_helper import _lazy_re_compile

from django.utils.translation import gettext_lazy as _l


User = get_user_model()

if typing.TYPE_CHECKING:
    from django_simple_dms.models import Document
    from django.db.models.query import QuerySet


slug_re = _lazy_re_compile(r'^([-a-zA-Z0-9_]+(\.)?)+\Z')
validate_csslug = RegexValidator(
    slug_re,
    # Translators: "letters" means latin letters: a-z and A-Z.
    _l('Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.'),
    'invalid',
)


class DocumentTag(models.Model):
    title = models.CharField(
        help_text=_l('A dot-separated slug'),
        unique=True,
        validators=[validate_csslug],
    )

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self) -> None:
        self.title = self.title.lower().strip('.')


class DocumentGrant(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    granted_permissions = ArrayField(
        models.CharField(max_length=1), default=list, help_text=_l('one or more of R,U,D,S')
    )
    granted_by_system = models.BooleanField(default=True)
    document = models.ForeignKey('Document', on_delete=models.CASCADE)

    def __str__(self) -> str:
        prefix = f'U:{self.user}' if self.user else f'D:{self.group}'
        granted_permissions = ''.join(self.granted_permissions)
        if not self.granted_by_system:
            granted_permissions = granted_permissions.lower()
        return f'{prefix}:{granted_permissions}:{self.document}'

    def save(self, *args, **kwargs) -> None:
        if self.granted_permissions == []:
            self.granted_permissions = ['R']
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self) -> None:
        if self.user and self.group:
            raise ValidationError(_l('Cannot set both user and group'), '__all__')
        if not (self.user or self.group):
            raise ValidationError(_l('Must set either user or group'), '__all__')
        self.granted_permissions = [x.upper() for x in self.granted_permissions]
        if extra := (set(self.granted_permissions) - {'R', 'U', 'D', 'S'}):
            raise ValidationError(_l('Invalid permissions: %(extra)s') % {'extra': ''.join(extra)}, '__all__')


class TagGrant(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    create = models.BooleanField(default=True)
    defaults = ArrayField(models.CharField(max_length=1), default=list, help_text=_l('one or more of R,U,D,S'))
    granted_by_system = models.BooleanField(default=True)
    tag = models.ForeignKey('DocumentTag', on_delete=models.CASCADE)

    def __str__(self) -> str:
        create = 'C' if self.create else ''
        defaults = ''.join(self.defaults)
        return f'{self.tag}-{self.group}-{create}{defaults}'

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self) -> None:
        self.defaults = [x.upper() for x in self.defaults]
        if extra := (set(self.defaults) - {'R', 'U', 'D', 'S'}):
            raise ValidationError(_l('Invalid defaults: %(extra)s') % {'extra': ''.join(extra)}, '__all__')


class DocumentQuerySet(models.QuerySet):
    def accessible_by(self, user: User) -> 'QuerySet[Document]':
        return self.filter(Q(admin=user) | Q(documentgrant__user=user) | Q(documentgrant__group__user=user)).distinct()

    def can_grant_contains(self, user: User, cruds: list[str]) -> 'QuerySet[Document]':
        return self.filter(
            Q(admin=user)
            | Q(documentgrant__user=user, documentgrant__granted_permissions__contains=cruds)
            | Q(documentgrant__group__user=user, documentgrant__granted_permissions__contains=cruds)
        ).distinct()

    def can_read(self, user: User) -> 'QuerySet[Document]':
        return self.can_grant_contains(user, ['R'])

    def can_update(self, user: User) -> 'QuerySet[Document]':
        return self.can_grant_contains(user, ['U'])

    def can_delete(self, user: User) -> 'QuerySet[Document]':
        return self.can_grant_contains(user, ['D'])

    def can_share(self, user: User) -> 'QuerySet[Document]':
        return self.can_grant_contains(user, ['S'])


class Document(models.Model):
    document = models.FileField(upload_to='documents/%Y/%m/%d')
    upload_date = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)

    reference_period = DateRangeField(null=True, blank=True)

    objects = DocumentQuerySet.as_manager()

    def __str__(self) -> str:
        admin = f' ({self.admin})' if self.admin else ''
        return f'{self.document.name}{admin}'
