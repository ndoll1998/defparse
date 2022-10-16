import inspect
import argparse
from docstring_parser import parse
from types import SimpleNamespace
from functools import wraps
# type hints
from typing import (
    Any, 
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

class ArgumentParser(argparse.ArgumentParser):

    def parse_args(self, *args, **kwargs):
        # parse arguments and store them
        self._parsed_args = super(ArgumentParser, self).parse_args(*args, **kwargs)
        return self._parsed_args

    def add_args_from_callable(
        self, 
        fn:Callable[[Any], T], 
        *,
        group:str =None,
        ignore:List[str] =[]
    ) -> Callable[[Any], T]:
    
        # create argument group
        group = self.add_argument_group(group or fn.__name__)
        
        # get function signature
        sig = inspect.signature(fn)

        # parse docstring
        doc = inspect.getdoc(fn)
        doc_params = {p.arg_name: p for p in parse(doc).params} if doc is not None else {}

        for name, param in sig.parameters.items():            
            # check if parameter should be ignored
            if (name in ignore):
                continue

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
                            raise TypeError("Argument Type cannot be Union of multiple types!")
                    elif origin is Literal:
                        # infer type from args and add choices argument
                        kwargs['type'] = type(args[0])
                        kwargs['choices'] = args
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
                continue

            if 'type' not in kwargs:
                raise AttributeError("Cannot find argument type for argument %s in callable %s" % (name, fn))

            # get description from docstring
            if name in doc_params:
                kwargs['help'] = doc_params[name].description.replace('\n', ' ')

            # add arguments from signature
            group.add_argument(argname, **kwargs)

        # create function executor
        @wraps(fn)
        def call_wrapper(*args, **kwargs):
            if not hasattr(self, '_parsed_args'):
                raise RuntimeError("No parsed arguments found! Did you forget to call `parse_args`?")

            # get arguments from parser
            parser_args = {
                k:v for k, v in vars(self._parsed_args).items()
                if (k in sig.parameters) and (k not in ignore)
            }
            # run callable
            return fn(*args, **kwargs, **parser_args)

        return call_wrapper
