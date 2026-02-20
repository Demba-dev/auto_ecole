from django.utils.deprecation import MiddlewareMixin

class NoCacheAuthenticatedMiddleware(MiddlewareMixin):
    """Prevent caching of pages for authenticated users so that after logout the
    browser won't show protected pages from its cache (back button).

    Adds headers: Cache-Control: no-store, no-cache, must-revalidate, Pragma: no-cache
    only for responses served while the user was authenticated.
    """

    def process_response(self, request, response):
        try:
            user = getattr(request, 'user', None)
            if user and user.is_authenticated:
                response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
        except Exception:
            pass
        return response
