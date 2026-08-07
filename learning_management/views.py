from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Learning
from .serializers import LearningSerializer


@api_view(['GET', 'POST'])
def learning_list(request):

    if request.method == 'GET':
        learnings = Learning.objects.all()
        serializer = LearningSerializer(learnings, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = LearningSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Enrollment created successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def learning_detail(request, pk):

    try:
        learning = Learning.objects.get(pk=pk)

    except Learning.DoesNotExist:
        return Response(
            {"error": "Enrollment not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        serializer = LearningSerializer(learning)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = LearningSerializer(learning, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "Learning progress updated successfully",
                    "data": serializer.data
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        learning.delete()

        return Response(
            {"message": "Enrollment deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )