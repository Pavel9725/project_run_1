from rest_framework.decorators import api_view
from django.conf import settings
from rest_framework.response import Response


@api_view(['GET'])
def view_about(request):
    details = {
        'company_name': settings.COMPANY_NAME,
        'slogan': settings.SLOGAN,
        'contacts': settings.CONTACTS
    }
    return Response(details)


