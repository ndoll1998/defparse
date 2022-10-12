from defparse import ArgumentParser

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
