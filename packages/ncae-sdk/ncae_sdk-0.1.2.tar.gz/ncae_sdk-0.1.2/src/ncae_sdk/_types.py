import functools
import inspect
from dataclasses import dataclass
from typing import Annotated, Any, Awaitable, Iterator, Optional

from typing_extensions import Callable, ParamSpec, TypeAlias, TypeVar
from typing_extensions import get_args as get_type_args
from typing_extensions import get_origin as get_type_origin

FuncP = ParamSpec("FuncP")
FuncR = TypeVar("FuncR")
Func = Callable[FuncP, FuncR]


@dataclass(frozen=True)
class ParamProcessorContext:
    current: list[inspect.Parameter]
    original: list[inspect.Parameter]

    @property
    def current_map(self) -> dict[str, inspect.Parameter]:
        return {param.name: param for param in self.current}

    @property
    def original_map(self) -> dict[str, inspect.Parameter]:
        return {param.name: param for param in self.original}


ParamProcessor: TypeAlias = Callable[[ParamProcessorContext], Iterator[inspect.Parameter]]


def process_function_parameters(
    *processors: ParamProcessor,
) -> Callable[[Callable[FuncP, Awaitable[FuncR]]], Callable[FuncP, Awaitable[FuncR]]]:
    def decorator(func: Callable[FuncP, Awaitable[FuncR]]) -> Callable[FuncP, Awaitable[FuncR]]:
        @functools.wraps(func)
        async def wrapper(*args: FuncP.args, **kwargs: FuncP.kwargs) -> FuncR:
            return await func(*args, **kwargs)

        # Obtain function signature and parameters
        original_signature = inspect.signature(func)
        original_params = list(original_signature.parameters.values())

        # Apply all processors in sequence to transform the function signature
        current_params = original_params
        for processor in processors:
            # Construct context and run parameter processor
            context = ParamProcessorContext(
                current=current_params,
                original=original_params,
            )
            current_params = list(processor(context))

            # Add any new parameters to original parameters for subsequent processors
            missing_params = [p for p in current_params if p.name not in context.original_map]
            if missing_params:
                original_params.extend(missing_params)

        # Replace wrapper signature with transformed signature
        wrapper_signature = original_signature.replace(parameters=current_params)
        setattr(wrapper, "__signature__", wrapper_signature)

        return wrapper

    return decorator


def inject_parameter(name: str, typ: type) -> ParamProcessor:
    def processor(ctx: ParamProcessorContext) -> Iterator[inspect.Parameter]:
        yield from ctx.current
        yield inspect.Parameter(
            name=name,
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=typ,
        )

    return processor


def resolve_generic_signatures(ctx: ParamProcessorContext) -> Iterator[inspect.Parameter]:
    for param in ctx.current:
        original_param = ctx.original_map[param.name]
        param_class = _extract_class_type(original_param.annotation)

        if param_class:
            new_type = _resolve_generic_class_signature(original_param.annotation)
            new_annotation = _replace_annotation_type(param.annotation, new_type)
            yield param.replace(annotation=new_annotation)
        else:
            yield param


def _extract_class_type(annotation: type) -> Optional[type]:
    if inspect.isclass(annotation):
        return annotation
    elif origin := get_type_origin(annotation):
        if inspect.isclass(origin):
            return origin

    return None


def _replace_annotation_type(annotation: type, new_type: type) -> Any:
    origin = get_type_origin(annotation)
    args = get_type_args(annotation)

    if origin is Annotated and len(args) == 2:
        return Annotated[new_type, args[1]]
    else:
        return new_type


def _resolve_generic_class_signature(cls_annotation: type) -> Any:
    # Extract actual class (origin) with its generics and their arguments
    cls = _extract_class_type(cls_annotation)
    cls_args = get_type_args(cls_annotation)
    cls_generics = getattr(cls, "__parameters__", [])

    # Ensure type origin is actually a class and return early if there are no generics to resolve
    if not inspect.isclass(cls):
        raise TypeError("Provided argument is not a class.")
    if not cls_generics or not cls_args:
        return cls_annotation

    # Fill generic arguments with their defaults if not explicitly provided
    if len(cls_generics) != len(cls_args):
        filled_args = list(cls_args)
        for gen in cls_generics[len(cls_args) :]:
            if defaults := getattr(gen, "__default__", ()):
                filled_args.append(defaults)
        cls_args = tuple(filled_args)

    # Build mapping of generic type variables to their actual arguments
    if len(cls_generics) != len(cls_args):
        raise TypeError("Unable to resolve generics in class signature due to mismatched arguments.")
    cls_generic_map = {gen: arg for gen, arg in zip(cls_generics, cls_args)}

    # Generate wrapper function around class, so that its constructor signature can be modified
    @functools.wraps(cls)
    def cls_wrapper(*args: Any, **kwargs: Any) -> Any:
        return cls(*args, **kwargs)

    # Obtain the __init__ signature and parameters, skipping 'self'
    # The latter is implicitly handled by Python and must not be specified
    init_signature = inspect.signature(cls.__init__)
    init_params = list(init_signature.parameters.values())[1:]

    # Build new function parameters, resolving all generic variables where possible
    wrapper_params: list[inspect.Parameter] = []
    for init_param in init_params:
        # Forward existing parameter as-is if there are no generics to resolve
        param_generics = getattr(init_param.annotation, "__parameters__", [])
        if not param_generics:
            wrapper_params.append(init_param)
            continue

        # Ensure parameter annotation points to class type
        if not inspect.isclass(init_param.annotation):
            raise TypeError(f"Parameter {init_param.name} annotation is not a class type.")

        # Resolve all generic variables in parameter annotation
        wrapper_param_args: list[type] = []
        for param_generic in param_generics:
            if concrete_type := cls_generic_map.get(param_generic, None):
                wrapper_param_args.append(concrete_type)
            else:
                raise TypeError(f"Unable to resolve generic {param_generic} in parameter {init_param.name}.")

        # Construct new parameter annotation with resolved generics
        wrapper_param_annotation = init_param.annotation[tuple(wrapper_param_args)]
        wrapper_param = init_param.replace(annotation=wrapper_param_annotation)
        wrapper_params.append(wrapper_param)

    # Replace wrapper signature with resolved parameters
    wrapper_signature = init_signature.replace(parameters=wrapper_params)
    setattr(cls_wrapper, "__signature__", wrapper_signature)

    return cls_wrapper
