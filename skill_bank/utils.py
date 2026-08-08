"""
skill_bank/utils.py
Platform-wide utilities: standardised error responses, custom DRF exception handler.
"""

import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Returns a consistent JSON error shape for every DRF exception:
        {"error": {"code": "<str>", "message": "<str>", "details": {...}}}
    """
    response = exception_handler(exc, context)

    if response is not None:
        code = getattr(exc, 'default_code', 'error')
        message = str(exc)

        # Flatten DRF validation error details nicely
        details = response.data if isinstance(response.data, dict) else {'non_field': response.data}

        response.data = {
            'error': {
                'code': code,
                'message': message,
                'details': details,
            }
        }
    else:
        # Unhandled exception — log it, return generic 500
        logger.exception("Unhandled exception in %s", context.get('view', ''))
        response = Response(
            {
                'error': {
                    'code': 'server_error',
                    'message': 'An unexpected error occurred. Please try again later.',
                    'details': {},
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


def api_error(code: str, message: str, status_code=400, details=None):
    """
    Helper to return a standardised error Response from any view.
    Usage:
        return api_error('invalid_rating', 'Rating must be between 1 and 5.', 400)
    """
    return Response(
        {
            'error': {
                'code': code,
                'message': message,
                'details': details or {},
            }
        },
        status=status_code,
    )


def api_success(data, status_code=200):
    """Thin wrapper so all success responses are also consistent."""
    return Response(data, status=status_code)
