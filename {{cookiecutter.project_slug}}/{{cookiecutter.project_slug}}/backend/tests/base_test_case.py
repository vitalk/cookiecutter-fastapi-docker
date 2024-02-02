class BaseTestCase:
    base_url: str

    def get_url(self) -> str:
        return self.base_url
