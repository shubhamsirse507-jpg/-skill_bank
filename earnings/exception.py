from rest_framework.response import Response
from rest_framework import status


def earning_not_found():

    return Response(
        {
            "success": False,
            "message": "Earning record not found"
        },
        status=status.HTTP_404_NOT_FOUND
    )