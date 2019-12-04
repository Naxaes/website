import uuid

from django.conf import settings
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.core import signing
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import BooleanField, CharField, DateTimeField, EmailField, UUIDField

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from website.users.managers import CustomUserManager


class AbstractUser(AbstractBaseUser, PermissionsMixin):

    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """

    username = CharField(
        _('username'),
        max_length=150,
    )
    email = EmailField(_('email address'), unique=True)

    is_staff = BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Decides if the user has access to the admin'),
    )
    is_active = BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Decides if the user should be concidered active. Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = DateTimeField(_('Date of joining.'), default=timezone.now)
    first_name = CharField(blank=True, max_length=30, verbose_name="first name")
    last_name = CharField(blank=True, max_length=150, verbose_name="last name")

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = CharField(_("Name of User"), blank=True, max_length=255)
    uid = UUIDField(default=uuid.uuid4, help_text=_('Unique ID for this model'))


class OneTimeToken:
    """
    A token that can be used to login directly to the site, as long as check_payload is valid.

    Once check_payload returns False, in this case when the payouts are accepted, it can no longer
    be used.
    """

    expire_days = settings.ONE_TIME_TOKEN_EXPIRE_DAYS
    DoesNotExist = ObjectDoesNotExist

    def __init__(self, user):
        self.user = user

    @classmethod
    def from_key(cls, key):
        """
        Recreate a OneTimeToken from its key.

        If the signing is invalid, it has expired or already been
        used: raise Object.DoesNotExist.
        """
        try:
            max_age = (
                    60 * 60 * 24 * cls.expire_days
            )
            user_id = signing.loads(
                key, max_age=max_age,
                salt=settings.ONE_TIME_TOKEN_SALT
            )
            user = cls.check_user(user_id)
        except (signing.SignatureExpired,
                signing.BadSignature,
                ObjectDoesNotExist):
            raise cls.DoesNotExist
        else:
            return OneTimeToken(user)

    @staticmethod
    def check_user(user_id):
        """Try to get user"""
        return User.objects.get(id=user_id)

    @property
    def key(self):
        return signing.dumps(
            obj=self.user.id,
            salt=settings.ONE_TIME_TOKEN_SALT)
