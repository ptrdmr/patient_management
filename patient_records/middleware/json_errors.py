import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class JSONErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                response = self.get_response(request)
                return response
            except Exception as e:
                logger.exception('Unhandled exception in AJAX request')
                return JsonResponse({
                    'error': 'An unexpected error occurred'
                }, status=500)
        return self.get_response(request) 