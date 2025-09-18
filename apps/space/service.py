import base64

from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def render_email_format(sender, email_receiver, space_name, invite_url):
    try:
        html_message = render_to_string(
            "email_format.html",
            {
                "sender_name": sender,
                "space_name": space_name,
                "email_receiver": email_receiver,
                "invite_url": invite_url,
            },
        )
        return html_message
    except Exception as e:
        raise ValidationError({"error": f"Error: {e}"})
