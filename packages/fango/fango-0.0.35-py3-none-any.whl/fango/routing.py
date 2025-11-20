from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from fango.viewsets import AsyncGenericViewSet

from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class FangoRouter(APIRouter):
    viewsets = []

    def get(self, *args, **kwargs) -> Callable:
        response_model_exclude_unset = kwargs.pop("response_model_exclude_unset", True)
        return super().get(*args, **kwargs, response_model_exclude_unset=response_model_exclude_unset)

    def register(
        self,
        basename: str,
        viewset: type["AsyncGenericViewSet"],
    ) -> None:
        """
        Register viewset.

        """
        vs = viewset(
            self,
            basename,
        )
        self.viewsets.append(vs)


action = FangoRouter()
