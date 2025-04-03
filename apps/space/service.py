import base64
import json
import os
import secrets

from django.conf import settings
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError


def generate_token(email_sender, email_receiver, slug_name, space_id):
    salt = secrets.token_hex(16)
    data = json.dumps(
        {
            "email_sender": email_sender,
            "email_receiver": email_receiver,
            "space_id": space_id,
            "slug_name": slug_name,
            "salt": salt,
        }
    )
    token = base64.b64encode(data.encode()).decode()
    return token


def decode_token(token):
    try:
        data = json.loads(base64.b64decode(token).decode())
        return (
            data.get("email_sender"),
            data.get("space_id"),
            data.get("email_receiver"),
            data.get("slug_name"),
        )
    except Exception:
        return None, None, None, None


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def render_email_format(sender, email_receiver, space_name, invite_url):
    try:
        image_path = os.path.join(settings.BASE_DIR, "static/images/logo.png")
        base64_image = f"data:image/png;base64,{encode_image_to_base64(image_path)}"
        html_message = render_to_string(
            "email_format.html",
            {
                "email_sender": sender,
                "space_name": space_name,
                "email_receiver": email_receiver,
                "base64_image": base64_image,
                "invite_url": invite_url,
            },
        )
        return html_message
    except Exception as e:
        raise ValidationError({"error": f"Error: {e}"})
