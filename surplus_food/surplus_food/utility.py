import random

import string

from django.core.mail import EmailMultiAlternatives

from django.template.loader import render_to_string

from decouple import config

def generate_otp():

    return ''.join(random.choices(string.digits, k=4))


def send_email(subject, recipient, template, context):

    sender = config('EMAIL_HOST_USER')

    email_obj = EmailMultiAlternatives(subject, from_email=sender, to=[recipient])

    content = render_to_string(template, context)

    email_obj.attach_alternative(content, mimetype='text/html')

    email_obj.send()