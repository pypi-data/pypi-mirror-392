from client.pypi.pixelarraythirdparty.client import AsyncClient


class GoogleLogin(AsyncClient):
    async def _get_auth_url(self):
        pass
        
    async def _get_code_from_redirect_uri(self, redirect_uri: str):
        pass

    async def _get_user_info(self, token: str) -> dict:
        pass

    async def login(self) -> dict:
        pass

    async def logout(self) -> dict:
        pass
