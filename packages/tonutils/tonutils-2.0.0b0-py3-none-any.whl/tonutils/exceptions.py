import typing as t

__all__ = [
    "ClientError",
    "ContractError",
    "DeserializeNotImplementedError",
    "NotRefreshedError",
    "PytoniqDependencyError",
    "ClientNotConnectedError",
    "TonutilsException",
]


class TonutilsException(Exception):
    @classmethod
    def _obj_name(cls, obj: t.Union[object, type, str]) -> str:
        if isinstance(obj, type):
            return obj.__name__
        elif isinstance(obj, str):
            return obj
        return obj.__class__.__name__


class ClientError(TonutilsException): ...


class ContractError(TonutilsException):
    def __init__(self, obj: t.Union[object, type, str], message: str) -> None:
        super().__init__(f"{self._obj_name(obj)}: {message}")


class DeserializeNotImplementedError(TonutilsException):
    def __init__(self, obj: t.Union[object, type, str]) -> None:
        super().__init__(f"Deserialize for `{self._obj_name(obj)}` is not implemented.")


class NotRefreshedError(TonutilsException):
    def __init__(self, obj: t.Union[object, type, str], attr: str) -> None:
        super().__init__(
            f"Access to `{attr}` is not allowed.\n"
            f"Call `await {self._obj_name(obj)}.refresh()` before accessing `{attr}`."
        )


class ClientNotConnectedError(TonutilsException):
    def __init__(self, obj: t.Union[object, type, str]) -> None:
        super().__init__(
            f"`{self._obj_name(obj)}` is not connected.\n"
            f"Use `async with {self._obj_name(obj)}(...) as client:` "
            f"or call `await {self._obj_name(obj)}(...).connect()` before making requests."
        )


class PytoniqDependencyError(TonutilsException):
    def __init__(self, obj: t.Union[object, type, str]) -> None:
        super().__init__(
            f"The `pytoniq` library is required to use "
            f"`{self._obj_name(obj)}` functionality.\n"
            "Please install it with `pip install tonutils[pytoniq]`."
        )
