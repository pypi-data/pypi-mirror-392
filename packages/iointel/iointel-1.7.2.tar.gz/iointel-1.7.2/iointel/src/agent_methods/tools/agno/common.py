from pydantic import BaseModel
import inspect
from functools import wraps
from agno.tools import Toolkit

from ..utils import register_tool


class DisableAgnoRegistryMixin:
    """
    Put this as first parent class when inheriting
    from Agno tool to disable Agno registry,
    because we only care about our own registry."""

    def _register_tools(self):
        """Disabled in favour of iointel registry."""

    def register(self, function, name=None):
        """Disabled in favour of iointel registry."""


def make_base(agno_tool_cls: type[Toolkit]):
    class BaseAgnoTool(BaseModel):
        class Inner(DisableAgnoRegistryMixin, agno_tool_cls):
            pass

        def _get_tool(self) -> Inner:
            raise NotImplementedError()

        _tool: Inner

        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)
            self._tool = self._get_tool()

    return BaseAgnoTool


def wrap_tool(name, agno_method):
    def wrapper(func):
        agno_signature = inspect.signature(agno_method)
        our_signature = inspect.signature(func)
        have_contradicting_defaults = False
        for argname, argparam in agno_signature.parameters.items():
            if (
                argparam.default is None
                and our_signature.parameters[argname].default is not None
            ):
                have_contradicting_defaults = True
                break

        if have_contradicting_defaults:

            @wraps(func)
            def patcher(*a, **kw):
                bound = agno_signature.bind(*a, **kw)
                bound.apply_defaults()
                final_args = dict(bound.arguments)
                for argname, argvalue in bound.arguments.items():
                    if (
                        argvalue is None
                        and agno_signature.parameters[argname].default is None
                    ):
                        final_args[argname] = our_signature.parameters[argname].default
                return func(**final_args)

            patcher.__iointel_tool__ = func
        else:
            # no need to patch argument values, we don't have contradicting defaults
            patcher = func
        # copy only docstring and annotations from original agno tool,
        # leave other properties like __qualname__ or __module__ as is
        return register_tool(name=name)(
            wraps(agno_method, assigned=["__doc__", "__annotations__"])(patcher)
        )

    return wrapper
