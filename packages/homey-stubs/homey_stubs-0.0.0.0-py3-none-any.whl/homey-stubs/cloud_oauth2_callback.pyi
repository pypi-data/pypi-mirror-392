from typing import Literal, LiteralString, TypeVar, final
from warnings import deprecated

from .simple_class import SimpleClass

ChildEvent = TypeVar("ChildEvent", bound=LiteralString)

class CloudOAuth2Callback(SimpleClass[Literal["code", "url"] | ChildEvent]):
    """
    An OAuth2 callback that can be used in log-in flows.
    """

    @final
    @deprecated(
        "This class must not be initialized by the developer, but retrieved by calling ManagerCloud.create_oauth2_callback."
    )
    def __init__(self) -> None: ...
