import base64
import json
import secrets

from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError


def generate_token(email_receiver, org_slug_name, space_role_user_id):
    salt = secrets.token_hex(16)
    data = json.dumps(
        {
            "email_receiver": email_receiver,
            "org_slug_name": org_slug_name,
            "space_role_user_id": str(space_role_user_id),
            "salt": salt,
        }
    )
    token = base64.b64encode(data.encode()).decode()
    return token


def decode_token(token):
    try:
        data = json.loads(base64.b64decode(token).decode())
        return (
            data.get("email_receiver"),
            data.get("org_slug_name"),
            data.get("space_role_user_id"),
        )
    except Exception:
        return None, None, None, None


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
