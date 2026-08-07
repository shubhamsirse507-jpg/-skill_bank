from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Feedback
from .serializers import FeedbackSerializer
from .services import FeedbackService


class FeedbackViewSet(viewsets.ModelViewSet):

    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        teacher = serializer.instance.teacher

        average = FeedbackService.average_rating(teacher)

        return Response(
            {
                "message": "Feedback Added Successfully",
                "average_rating": average,
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )