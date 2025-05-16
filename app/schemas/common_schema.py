from typing import Generic, Optional, TypeVar
from pydantic.generics import GenericModel

T = TypeVar("T")

class ApiResponse(GenericModel, Generic[T]):
    message: str
    data: Optional[T] = None