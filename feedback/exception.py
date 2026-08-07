from rest_framework.response import Response
from rest_framework import status


def feedback_not_found():

    return Response(
        {
            "success": False,
            "message": "Feedback not found"
        },
        status=status.HTTP_404_NOT_FOUND
    )