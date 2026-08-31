from django.shortcuts import redirect
from news.views import username_is_allowed

ALLOW_PREFIXES = (
    "/admin/",
    "/static/",
    "/username/",
    "/screen/login/",
    "/screen/logout/",
)


class UsernameSubMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            if not (user.is_staff or user.is_superuser):
                path = request.path or ""
                if path.startswith("/screen") and not any(path.startswith(p) for p in ALLOW_PREFIXES):
                    if not username_is_allowed(user):
                        return redirect("/username/?needed=1")
        return self.get_response(request)
