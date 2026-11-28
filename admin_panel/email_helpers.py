"""
admin_panel/email_helpers.py
Brevo email helper reused from authentication/views.py pattern.
Sends arbitrary subject/html/plain to any email address (no User object required).
"""
import json
import logging
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)


def send_brevo_email(to_email: str, to_name: str, subject: str,
                     html_content: str, plain_text: str) -> bool:
    """
    Send a transactional email via Brevo HTTPS API.
    Returns True on success, False on failure.
    Never logs the email body (may contain sensitive links).
    """
    brevo_api_key = getattr(settings, 'BREVO_API_KEY', '').strip()
    if not brevo_api_key:
        logger.warning("[Email] BREVO_API_KEY not configured — email not sent to %s", to_email)
        return False

    sender_email = (
        getattr(settings, 'BREVO_SENDER_EMAIL', '').strip()
        or getattr(settings, 'EMAIL_HOST_USER', '').strip()
        or 'noreply@skill-verse.com'
    )
    sender_name = getattr(settings, 'BREVO_SENDER_NAME', 'Skill-Verse').strip() or 'Skill-Verse'
    timeout_sec = int(getattr(settings, 'EMAIL_TIMEOUT', 15))

    payload = json.dumps({
        'sender': {'name': sender_name, 'email': sender_email},
        'to': [{'email': to_email, 'name': to_name}],
        'subject': subject,
        'htmlContent': html_content,
        'textContent': plain_text,
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.brevo.com/v3/smtp/email',
        data=payload,
        headers={
            'accept': 'application/json',
            'content-type': 'application/json',
            'api-key': brevo_api_key,
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            if 200 <= resp.status < 300:
                logger.info("[Email] Brevo delivered to %s subject='%s'", to_email, subject)
                return True
            logger.error("[Email] Brevo status %s for %s", resp.status, to_email)
    except urllib.error.HTTPError as err:
        body = err.read().decode('utf-8', 'ignore')
        logger.error("[Email] Brevo HTTP %s for %s: %s", err.code, to_email, body)
    except Exception as exc:
        logger.error("[Email] Brevo request failed for %s: %s", to_email, exc, exc_info=True)
    return False

