import random
from urllib.parse import urlencode
from datafakegenerator.providers.base_provider import BaseProvider


class UrlProvider(BaseProvider):
    def __init__(
        self,
        *,
        protocol: bool = True,
        host: bool = True,
        path: bool = True,
        query_string: bool = True,
        blank_percentage: float = 0.0,
        **kwargs
    ):
        """
        Generate realistic URLs with optional parts.
        Example formats:
          https://facebook.com/foo/bar?x=1
          http://example.org
          /foo/bar
        """
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.protocol_enabled = protocol
        self.host_enabled = host
        self.path_enabled = path
        self.query_enabled = query_string

        self.protocols = ["http", "https"]
        self.hosts = [
            "google.com", "facebook.com", "twitter.com", "github.com",
            "example.org", "mywebsite.net", "openai.com", "amazon.com",
            "linkedin.com", "youtube.com", "wikipedia.org", "reddit.com",
            "apple.com", "microsoft.com", "medium.com", "notion.so",
            "zoom.us", "shopify.com", "pinterest.com", "cnn.com",
            "nytimes.com", "bbc.com", "bloomberg.com", "tiktok.com",
            "airbnb.com", "netflix.com", "spotify.com", "dropbox.com",
            "salesforce.com", "wordpress.com", "blogspot.com"
        ]
        self.paths = [
            "/", "/home", "/profile", "/search", "/login", "/register",
            "/products", "/products/new", "/products/sale", "/shop",
            "/cart", "/checkout", "/orders", "/orders/history",
            "/blog", "/blog/latest", "/blog/tech", "/blog/news",
            "/docs", "/docs/api", "/docs/getting-started",
            "/contact", "/about", "/privacy-policy", "/terms",
            "/dashboard", "/settings", "/settings/profile",
            "/settings/security", "/api/v1/resource", "/api/v1/items",
            "/api/v2/users", "/api/v2/data", "/api/v2/search",
            "/foo/bar", "/v1/login", "/v1/logout", "/uploads/files"
        ]
        self.query_params = [
            {"foo": "bar"},
            {"id": str(random.randint(1, 1000))},
            {"q": "test"},
            {"q": "laptop"},
            {"q": "python"},
            {"lang": "en"},
            {"lang": "es"},
            {"page": str(random.randint(1, 50))},
            {"ref": "newsletter"},
            {"utm_source": "google"},
            {"utm_campaign": "spring_sale"},
            {"sort": "price_asc"},
            {"sort": "popularity"},
            {"filter": "in_stock"},
            {"category": "electronics"},
            {"category": "fashion"},
            {"tag": "ai"},
            {"session": str(random.randint(100000, 999999))},
        ]

    def generate_non_blank(self, row_data=None):

        protocol = random.choice(
            self.protocols) if self.protocol_enabled else None
        host = random.choice(self.hosts) if self.host_enabled else None
        path = random.choice(self.paths) if self.path_enabled else ""

        query = ""
        if self.query_enabled and random.random() < 0.5:
            params = random.choice(self.query_params)
            query = "?" + urlencode(params)

        if protocol and host:
            base = f"{protocol}://{host}"
        elif host:
            base = host
        elif protocol:
            base = f"{protocol}://"
        else:
            base = ""

        url = base + path + query
        return url or None
