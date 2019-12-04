from django.contrib.auth import get_user_model

from config import celery_app
from website.core.utils   import full_url, render_email
from website.users.models import OneTimeToken


User = get_user_model()


@celery_app.task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return User.objects.count()


def send_password_email(email):
    """Sends an email to the user"""
    if User.objects.filter(email__exact=email['email']).exists():
        user = User.objects.get(email__exact=email['email'])
        query_dict = {'token': OneTimeToken(user).key}
        url = full_url('/password/', query_dict=query_dict)
        context = {
            'url': url
        }
        subject = _('website: New password')
        template_prefix = 'users/emails/new_user_password'
        msg = render_email(subject, template_prefix, email['email'], context)
        msg.send()
    else:
        subject = _('website: No Account')
        template_prefix = 'users/emails/no_account'
        msg = render_email(subject, template_prefix, email['email'], None)
        msg.send()
    return None
