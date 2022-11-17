from __future__ import annotations
import inspect
import argparse
from docstring_parser import parse
from types import SimpleNamespace
from dataclasses import dataclass
# type hints
from typing import (
    Any,
    Set, 
    List,
    Tuple,
    Union,
    Literal, 
    Optional,
    TypeVar, 
    Callable 
)
from typing import get_origin, get_args
from .typehints import Ignore
# import to allow correct type inference from type hints
# like 'typing.Optional' and `defparse.Ignore` in docstring
import typing
import defparse.typehints as defparse

T = TypeVar('T')

class uses(object):
    USED_FUNCTIONS_KEY = "__uses_functions__"

    def __init__(self, used_fn:Callable):
        self.used_fn = used_fn

    def __call__(self, fn):
        if hasattr(fn, uses.USED_FUNCTIONS_KEY):
            getattr(fn, uses.USED_FUNCTIONS_KEY).add(self.used_fn)
        else:
            setattr(fn, uses.USED_FUNCTIONS_KEY, {self.used_fn})
        return fn

@dataclass
class ArgsContainer():
    _parser:ArgumentParser
    _arg_names:Set[str]
    fn:Callable[[Any, ...], [T]]

    @property
    def kwargs(self) -> Dict[str, Any]:
        # check if arguments are present
        if not hasattr(self._parser, '_parsed_args'):
            raise RuntimeError("No parsed arguments found! Did you forget to call `parse_args`?")
        # get all arguments
        return {k:v for k, v in vars(self._parser._parsed_args).items() if k in self._arg_names}

    def execute(self, **extra_kwargs) -> T:
        return self.fn(**self.kwargs, **extra_kwargs)

    def __call__(self, **extra_kwargs) -> T:
        return self.execute(**extra_kwargs)

class ArgumentParser(argparse.ArgumentParser):

    def __init__(self, *args, formatter:Callable[[str], str] =lambda n: n, **kwargs):
        super(ArgumentParser, self).__init__(*args, **kwargs)
        # save argument formatter
        self.formatter = formatter

    def parse_args(self, *args, **kwargs):
        # parse arguments and store them
        self._parsed_args = super(ArgumentParser, self).parse_args(*args, **kwargs)
        return self._parsed_args

    def _add_args_from_callable(
        self, 
        fn:Callable[[Any], T],
        group:object,
        ignore:List[str]
    ) -> Set[str]:

        # list of all added arguments    
        added_args = set()

        # get function signature
        sig = inspect.signature(fn)

        # parse docstring
        doc = inspect.getdoc(fn)
        doc_params = {p.arg_name: p for p in parse(doc).params} if doc is not None else {}

        # check if function has keyword arguments
        if any((p.kind == p.VAR_KEYWORD for p in sig.parameters.values())):
            # add all arguments of used functions
            # which populate the variable keyword arguments
            if hasattr(fn, uses.USED_FUNCTIONS_KEY):
                added_args = set.union(*(
                    self._add_args_from_callable(
                        fn=sub_fn,
                        group=group,
                        ignore=ignore
                    )
                    for sub_fn in getattr(fn, uses.USED_FUNCTIONS_KEY)
                ))
        
        for name, param in sig.parameters.items():            
            # check if parameter should be ignored
            # or is of kind variable keywords
            if (name in ignore) or (param.kind == param.VAR_KEYWORD):
                continue

            name = self.formatter(name)
            argname = "--" + name
            kwargs = {'required': True}

            # add default value
            if param.default != param.empty:
                kwargs['default'] = param.default
                kwargs['required'] = False

            # find/infer parameter type
            if param.annotation != param.empty:
                kwargs['type'] = param.annotation
            elif name in doc_params:
                kwargs['type'] = eval(doc_params[name].type_name)

            # handle type hints
            if 'type' in kwargs:
                
                origin = True
                while origin is not None:
                    # get origin and args
                    origin = get_origin(kwargs['type'])
                    args = get_args(kwargs['type'])
                    # check if type is marked as ignore
                    if origin is Ignore:
                        break
                    elif origin is Union:
                        # check if argument is marked by Optional
                        if args[1] is type(None):
                            # mark as not required and update type
                            kwargs['type'] = args[0]
                            kwargs['required'] = False
                        else:
                            # Union is not supported
                            raise TypeError("Argument Type cannot be Union of multiple types!")
                    elif origin is Literal:
                        # infer type from args and add choices argument
                        kwargs['type'] = type(args[0])
                        kwargs['choices'] = args
                    elif origin is set:
                        # update keyword arguments
                        kwargs['type'] = args[0]
                        kwargs['nargs'] = '*'
                    elif origin is list:
                        # update keyword arguments
                        kwargs['type'] = args[0]
                        kwargs['nargs'] = '+'
                    elif origin is tuple:
                        # check that types match and update keyword arguments
                        assert all(type(arg) is type(args[0]) for arg in args[1:]), "All types must match"
                        kwargs['type'] = args[0]
                        kwargs['nargs'] = len(args)
                
                if origin is Ignore:
                    # break by ignore type hint
                    continue

            elif 'default' in kwargs:
                # no type found, then infer from default
                kwargs['type'] = type(kwargs['default'])
            
            # check for conflict
            if argname in self._option_string_actions:
                # argument with same name already registered
                action = self._option_string_actions[argname]
                # check if types match
                if ('type' in kwargs) and (action.type is not kwargs['type']):
                    # type conflict
                    raise TypeError("Type conflict between registered argument `%s?`:`%s` and corresponding parameter of callable %s" % (argname, action.type, fn))
                # if types match than there is no conflict
                # the argument is just used multiple times
                added_args.add(name.replace('-', '_'))
                continue

            if 'type' not in kwargs:
                raise AttributeError("Cannot find argument type for argument %s in callable %s" % (name, fn))

            # simple boolean arguments as options
            if (kwargs['type'] is bool) and ('nargs' not in kwargs):
                kwargs['action'] = 'store_false' if kwargs.get('default', False) else 'store_true'
                kwargs.pop('type')

            # get description from docstring
            if name in doc_params:
                kwargs['help'] = doc_params[name].description.replace('\n', ' ')

            # add arguments from signature
            group.add_argument(argname, **kwargs)
            added_args.add(name.replace('-', '_'))

        # return list of added arguments
        return added_args

    def add_args_from_callable(
        self, 
        fn:Callable[[Any], T], 
        *,
        group:str =None,
        ignore:List[str] =[]
    ) -> ArgsContainer[T]: 
        # add arguments to parser
        added_args = self._add_args_from_callable(
            fn=fn, 
            group=self.add_argument_group(group or fn.__name__), 
            ignore=ignore
        )
        # return argument container
        return ArgsContainer(self, added_args, fn)
