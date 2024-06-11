from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from rest_framework import status, viewsets

# from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CineRequest
from .serializers import CineRequestSerializer


class CineRequestViewSet(viewsets.ModelViewSet):
    queryset = CineRequest.objects.all()
    serializer_class = CineRequestSerializer


class MarkAsSolvedView(APIView):
    # permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            cine_request = get_object_or_404(CineRequest, pk=pk)
            if cine_request.solved:
                return Response(
                    {"error": "Request is already marked as solved."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            cine_request.solved = True

            # Save the cine_request here temporarily
            cine_request.save()

            # Send email notification
            try:
                send_cine_request_fulfilled_mail(cine_request)
            except Exception as e:
                # If email sending fails, revert the `solved` status
                cine_request.solved = False
                cine_request.save()
                return Response(
                    {"error": "An error occurred while sending email."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {"status": "Request marked as solved and email sent."},
                status=status.HTTP_200_OK,
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": "An error occurred while processing the request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def send_cine_request_fulfilled_mail(cine_request):
    email_subject = "Your Cine Request has been Fulfilled"
    email_body = render_to_string(
        "cine_request/request_fulfilled.html",
        {"cine_request": cine_request},
    )
    try:
        email = EmailMultiAlternatives(email_subject, "", to=[cine_request.email])
        email.attach_alternative(email_body, "text/html")
        email.send()
    except Exception as e:
        raise Exception(f"Email sending failed: {str(e)}")
