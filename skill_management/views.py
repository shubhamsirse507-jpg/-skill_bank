from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Skill
from .serializers import SkillSerializer


# ----------------------------
# Get all skills / Create skill
# ----------------------------
@api_view(['GET', 'POST'])
def skill_list(request):

    if request.method == 'GET':
        skills = Skill.objects.all()
        serializer = SkillSerializer(skills, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SkillSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Skill created successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


# --------------------------------------
# Get, Update and Delete a single skill
# --------------------------------------
@api_view(['GET', 'PUT', 'DELETE'])
def skill_detail(request, pk):

    try:
        skill = Skill.objects.get(pk=pk)

    except Skill.DoesNotExist:
        return Response(
            {
                "error": "Skill not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        serializer = SkillSerializer(skill)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = SkillSerializer(skill, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Skill updated successfully",
                    "data": serializer.data
                }
            )

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        skill.delete()

        return Response(
            {
                "message": "Skill deleted successfully"
            },
            status=status.HTTP_204_NO_CONTENT
        )