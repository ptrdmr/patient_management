import logging
from django.http import HttpResponse, JsonResponse

logger = logging.getLogger('patient_records')

class LocaltunnelBypassMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"""
        Request Details:
        Path: {request.path}
        Method: {request.method}
        Headers: {dict(request.headers)}
        """)
        
        try:
            response = self.get_response(request)
            
            # Add bypass header for all responses
            if isinstance(response, HttpResponse):
                response['bypass-tunnel-reminder'] = 'true'
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
                
                # Log response info
                logger.info(f"Response status: {response.status_code}")
                if response.status_code in [301, 302]:
                    logger.info(f"Redirect to: {response.get('Location', 'unknown')}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in LocaltunnelBypassMiddleware: {str(e)}")
            return JsonResponse({
                'error': 'An unexpected error occurred'
            }, status=500)

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Allow login view to proceed normally
        if request.path == '/login/':
            return None
            
        # Handle other views
        return None 