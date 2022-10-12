import inspect
import argparse
from docstring_parser import parse
from types import SimpleNamespace
from functools import wraps
from typing import Callable, List, Any, TypeVar

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
            if name in ignore:
                continue
            
            # find/infer parameter type
            if param.annotation != param.empty:
                param_type = param.annotation
            elif param.default != param.empty:
                param_type = type(param.default)
            elif name in doc_params:
                param_type = eval(doc_params[name].type_name)
            else:
                param_type = None
            
            argname = "--" + name
            # check for conflict
            if argname in self._option_string_actions:
                # argument with same name already registered
                action = self._option_string_actions[argname]
                # check if types match
                if (param_type is not None) and (action.type is not param_type):
                    # type conflict
                    raise TypeError("Type conflict between registered argument `%s?`:`%s` and corresponding parameter of callable %s" % (argname, action.type, fn))
                # if types match than there is no conflict
                # the argument is just used multiple times
                continue

            if param_type is None:
                raise AttributeError("Cannot find argument type for argument %s in callable %s" % (name, fn))

            # get description from docstring
            description = doc_params[name].description.replace('\n', ' ') if name in doc_params else None

            # add arguments from signature
            group.add_argument(
                argname, 
                type=param_type,
                default=param.default if param.default != inspect._empty else None,
                required=param.default is param.empty,
                help=description
            )

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
