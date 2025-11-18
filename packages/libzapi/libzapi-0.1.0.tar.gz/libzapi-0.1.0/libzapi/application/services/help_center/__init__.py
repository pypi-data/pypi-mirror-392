import libzapi.infrastructure.api_clients.help_center as api
from libzapi.application.services.help_center.categories import CategoriesService
from libzapi.application.services.help_center.sections import SectionsService

from libzapi.infrastructure.http.auth import oauth_headers, api_token_headers
from libzapi.infrastructure.http.client import HttpClient


class HelpCenter:
    def __init__(
        self, base_url: str, oauth_token: str | None = None, email: str | None = None, api_token: str | None = None
    ):
        if oauth_token:
            headers = oauth_headers(oauth_token)
        elif email and api_token:
            headers = api_token_headers(email, api_token)
        else:
            raise ValueError("Provide oauth_token or email+api_token")

        http = HttpClient(base_url, headers=headers)

        # Initialize services
        self.categories = CategoriesService(api.CategoryApiClient(http))
        self.sections = SectionsService(api.SectionApiClient(http))
