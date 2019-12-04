from django.conf import settings

from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.contrib.sites.models import Site
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string

User = get_user_model()


def full_url(path, query_dict={}, site_id=settings.SITE_ID):
    """Turn a relative URL into an absolute URL."""
    site = Site.objects.get(id=site_id)

    if query_dict:
        query = '?'+'&'.join(f'{k}={v}' for k,v in query_dict.items())
    else:
        query = ''

    return f'{site.domain}{path}{query}'


def render_email(subject, template_prefix, to_email, context, from_email=None):
    """
    Renders a template to an Email object.

    Check if a html version of the template exists, if so
    attaches that as an alternative.
    """

    from_email = from_email or settings.DEFAULT_FROM_EMAIL

    bodies = {}
    for ext in ['html', 'txt']:
        try:
            template_name = '{0}.{1}'.format(template_prefix, ext)
            bodies[ext] = render_to_string(template_name,
                                           context).strip()
        except TemplateDoesNotExist:
            pass

    if not bodies:
        raise TemplateDoesNotExist(f'A template with the prefix {template_prefix} does not exist.')

    if 'txt' in bodies:

        msg = EmailMultiAlternatives(subject,
                                     bodies['txt'],
                                     from_email,
                                     [to_email])
        if 'html' in bodies:
            msg.attach_alternative(bodies['html'], 'text/html')
    else:
        msg = EmailMessage(subject,
                           bodies['html'],
                           from_email,
                           [to_email])
        msg.content_subtype = 'html'
    return msg

