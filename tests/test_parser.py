from defparse import ArgumentParser, Ignore
from argparse import _StoreTrueAction, _StoreFalseAction
from typing import Literal, List, Tuple, Optional

class TestFunctionParsing():

    def test_signature_parsing(self):

        # create parser
        parser = ArgumentParser()

        def test_function_A(A:int, B:float =0.3):
            """ Test function with type annotations and defaults

                Args:
                    A (int): description of argument A
                    B (float): description of argument B
            """
            return (A, B)

        # add arguments from callable
        parser.add_args_from_callable(test_function_A)

        # check args
        assert "--A" in parser._option_string_actions
        assert "--B" in parser._option_string_actions
        # check help string
        assert parser._option_string_actions['--A'].help == "description of argument A"
        assert parser._option_string_actions['--B'].help == "description of argument B"
        # check argument types
        assert parser._option_string_actions['--A'].type is int
        assert parser._option_string_actions['--B'].type is float
        # check default values
        assert parser._option_string_actions['--A'].default is None
        assert parser._option_string_actions['--B'].default == 0.3
        # check if required
        assert parser._option_string_actions['--A'].required is True
        assert parser._option_string_actions['--B'].required is False

    def test_doc_parsing(self):

        # create parser
        parser = ArgumentParser()

        def test_function_A(A, B=0.3):
            """ Test function with type annotations and defaults

                Args:
                    A (int): description of argument A
                    B (float): description of argument B
            """
            return (A, B)

        # add arguments from callable
        parser.add_args_from_callable(test_function_A)

        # check args
        assert "--A" in parser._option_string_actions
        assert "--B" in parser._option_string_actions
        # check help string
        assert parser._option_string_actions['--A'].help == "description of argument A"
        assert parser._option_string_actions['--B'].help == "description of argument B"
        # check argument types
        assert parser._option_string_actions['--A'].type is int
        assert parser._option_string_actions['--B'].type is float
        # check default values
        assert parser._option_string_actions['--A'].default is None
        assert parser._option_string_actions['--B'].default == 0.3
        # check if required
        assert parser._option_string_actions['--A'].required is True
        assert parser._option_string_actions['--B'].required is False

    def test_boolean_option(self):
        
        # create parser
        parser = ArgumentParser()

        # test ignore marker in signature and in doc
        def test_function_A(A:bool, B =True):
            """ Test function with type annotations and defaults

                Args:
                    A (bool): description of argument A
                    B (bool): description of argument B
            """
            return (A, B)

        # add arguments from callable
        test_function_A = parser.add_args_from_callable(test_function_A)
        
        # check args
        assert "--A" in parser._option_string_actions
        assert "--B" in parser._option_string_actions
        # check type and choices from signature
        assert isinstance(parser._option_string_actions['--A'], _StoreTrueAction)  # no default -> assume False
        assert isinstance(parser._option_string_actions['--B'], _StoreFalseAction) # as default is True

    def test_ignore_arguments(self):
        
        # create parser
        parser = ArgumentParser()

        def test_function_A(A, B=0.3):
            """ Test function with type annotations and defaults

                Args:
                    A (int): description of argument A
                    B (float): description of argument B
            """
            return (A, B)

        # add arguments from callable
        test_function_A = parser.add_args_from_callable(test_function_A, ignore=["A"])
        
        # check args
        assert "--A" not in parser._option_string_actions
        assert "--B" in parser._option_string_actions

        # parse arguments
        parser.parse_args("")

        # try to execute callable without required argument A
        try:
            test_function_A()
            assert False, "Did not expect for function to run without required argument `A`"
        except TypeError as e:
            pass

        # execute with argument
        A, B = test_function_A(A=3)
        assert A == 3
        assert B == 0.3
        
    def test_ignore_by_type_hint(self):
        # create parser
        parser = ArgumentParser()

        # test ignore marker in signature and in doc
        def test_function_A(A:Ignore[int], B):
            """ Test function with type annotations and defaults

                Args:
                    A (int): description of argument A
                    B (defparse.Ignore[float]): description of argument B
            """
            return (A, B)

        # add arguments from callable
        test_function_A = parser.add_args_from_callable(test_function_A)
        
        # check args
        assert "--A" not in parser._option_string_actions
        assert "--B" not in parser._option_string_actions
    
    def test_optional_argument(self):
        
        # create parser
        parser = ArgumentParser()

        def test_function_A(A:Optional[int], B):
            """ Test function with type annotations and defaults

                Args:
                    A (Optional[int]): description of argument A
                    B (Optional[int]): description of argument B
            """
            return (A, B)

        # add arguments from callable
        parser.add_args_from_callable(test_function_A)

        # check args
        assert "--A" in parser._option_string_actions
        assert "--B" in parser._option_string_actions
        # check type and choices from signature
        assert parser._option_string_actions['--A'].type is int
        assert parser._option_string_actions['--A'].required is False
        # check type and choices from docstring
        assert parser._option_string_actions['--B'].type is int
        assert parser._option_string_actions['--B'].required is False

    def test_literal_argument(self):
        
        # create parser
        parser = ArgumentParser()

        def test_function_A(A:Literal[1, 2, 3], B=0.3):
            """ Test function with type annotations and defaults

                Args:
                    A (Literal[1, 2, 3]): description of argument A
                    B (typing.Literal[0.3, 0.4]): description of argument B
            """
            return (A, B)

        # add arguments from callable
        parser.add_args_from_callable(test_function_A)

        # check args
        assert "--A" in parser._option_string_actions
        assert "--B" in parser._option_string_actions
        # check type and choices from signature
        assert parser._option_string_actions['--A'].type is type(1)
        assert parser._option_string_actions['--A'].choices == (1, 2, 3)
        # check type and choices from docstring
        assert parser._option_string_actions['--B'].type is type(0.3)
        assert parser._option_string_actions['--B'].choices == (0.3, 0.4)

    def test_list_argument(self):
        
        # create parser
        parser = ArgumentParser()

        def test_function_A(A:List[int], B):
            """ Test Function

                Args:
                    A (List[int]): A
                    B (List[int]): B

            """
            return (A, B)

        # add arguments from callable
        parser.add_args_from_callable(test_function_A)

        # check args
        assert "--A" in parser._option_string_actions
        assert "--B" in parser._option_string_actions
        # check type from signature
        assert parser._option_string_actions['--A'].type is int
        assert parser._option_string_actions['--A'].nargs == '+'
        # check type from docstring
        assert parser._option_string_actions['--B'].type is int
        assert parser._option_string_actions['--B'].nargs == '+'

    def test_tuple_argument(self):
        
        # create parser
        parser = ArgumentParser()

        def test_function_A(A:Tuple[int, int], B):
            """ Test Function

                Args:
                    A (Tuple[int, int]): A
                    B (Tuple[int, int]): B

            """
            return (A, B)

        # add arguments from callable
        parser.add_args_from_callable(test_function_A)

        # check args
        assert "--A" in parser._option_string_actions
        assert "--B" in parser._option_string_actions
        # check type from signature
        assert parser._option_string_actions['--A'].type is int
        assert parser._option_string_actions['--A'].nargs == 2
        # check type from docstring
        assert parser._option_string_actions['--B'].type is int
        assert parser._option_string_actions['--B'].nargs == 2
    
    def test_optional_list_of_literal_argument(self):
        
        # create parser
        parser = ArgumentParser()

        def test_function_A(A:Optional[List[Literal[1, 2, 3]]], B):
            """ Test Function

                Args:
                    A (Optional[List[Literal[1, 2, 3]]]): A
                    B (Optional[List[Literal[1, 2, 3]]]): B

            """
            return (A, B)

        # add arguments from callable
        parser.add_args_from_callable(test_function_A)
        
        # check args
        assert "--A" in parser._option_string_actions
        assert "--B" in parser._option_string_actions
        # check type from signature
        assert parser._option_string_actions['--A'].type is int
        assert parser._option_string_actions['--A'].nargs == '+'
        assert parser._option_string_actions['--A'].choices == (1, 2, 3)
        assert parser._option_string_actions['--A'].required is False
        # check type from docstring
        assert parser._option_string_actions['--B'].type is int
        assert parser._option_string_actions['--B'].nargs == '+'
        assert parser._option_string_actions['--B'].choices == (1, 2, 3)
        assert parser._option_string_actions['--B'].required is False

    def test_callable_executor(self):

        # create parser
        parser = ArgumentParser()

        def test_function_A(A, B=0.3):
            """ Test function with type annotations and defaults

                Args:
                    A (int): description of argument A
                    B (float): description of argument B
            """
            return (A, B)

        # add arguments from callable
        test_function_A = parser.add_args_from_callable(test_function_A)

        # parse arguments
        parser.parse_args("--A 4".split())
        # execute callable and check result
        A, B = test_function_A()
        assert A == 4
        assert B == 0.3
        
        # parse arguments
        parser.parse_args("--A 3 --B 1.2".split())
        # execute callable and check result
        A, B = test_function_A()
        assert A == 3
        assert B == 1.2

    
    def test_multiple_callables_with_argument_conflict(self):
        
        # create parser
        parser = ArgumentParser()

        def test_function_A(A:int =1, B:int =3):
            return A, B

        def test_function_B(A:float, C:float =0.3):
            return A, C

        # add arguments from first callable
        test_function_A = parser.add_args_from_callable(test_function_A)
   
        try:
            # try to add arguments from second callable
            test_function_B = parser.add_args_from_callable(test_function_B)
            assert False, "Expected TypeError due to type conflict"
        except TypeError:
            pass

    def test_multiple_callables_without_argument_conflict(self):
        
        # create parser
        parser = ArgumentParser()

        def test_function_A(A:int =1, B:int =3):
            return A, B

        def test_function_B(A:int, C:float =0.3):
            return A, C

        # add arguments from both callables
        test_function_A = parser.add_args_from_callable(test_function_A)
        test_function_B = parser.add_args_from_callable(test_function_B)

        # parse args
        parser.parse_args("")
        # execute and check
        A1, _ = test_function_A()
        A2, _ = test_function_B()
        assert A1 == A2
