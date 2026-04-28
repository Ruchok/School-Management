"""
Custom CSRF handling middleware
"""
import logging
from django.middleware.csrf import CsrfViewMiddleware as DjangoCsrfViewMiddleware

logger = logging.getLogger(__name__)


class CsrfDebugMiddleware(DjangoCsrfViewMiddleware):
    """Enhanced CSRF middleware with better logging for debugging"""
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Call parent process_view
        result = super().process_view(request, view_func, view_args, view_kwargs)
        
        # Log CSRF token info for debugging
        if request.method == 'POST':
            csrf_token = request.META.get('CSRF_COOKIE', 'NOT_SET')
            post_token = request.POST.get('csrfmiddlewaretoken', 'NOT_PROVIDED')
            
            logger.debug(f"""
                CSRF Debug Info for {request.path}:
                - CSRF Cookie: {csrf_token[:10]}... (truncated)
                - POST Token: {post_token[:10] if post_token != 'NOT_PROVIDED' else post_token}... (truncated)
                - Session ID: {request.session.session_key}
                - User: {request.user.username if request.user.is_authenticated else 'Anonymous'}
            """)
        
        return result
