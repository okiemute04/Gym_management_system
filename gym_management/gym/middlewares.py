from django.http import JsonResponse
from .models import Membership
import datetime



class MembershipMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_func.__name__ == 'CheckinViewSet.as_view' and request.method == 'POST':
            membership_id = request.data.get('membership')
            membership = Membership.objects.get(id=membership_id)
            if membership.state == 'canceled':
                return JsonResponse({'detail': 'Membership is Canceled'}, status=400)
            if membership.credits == 0:
                return JsonResponse({'detail': 'No credits available'}, status=400)
            if membership.end_date and membership.end_date < datetime.date.today():
                return JsonResponse({'detail': 'Membership has expired'}, status=400)
        return None
