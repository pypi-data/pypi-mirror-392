#!/usr/bin/env python3

# Top-level assignment
DEBUG = True
VERSION = "1.0.0"


# Top-level function
def top_level_function():
    pass


# Top-level class
class TopLevelClass:
    def method(self):
        pass


# Decorated function
@property
def decorated_function():
    pass


# Decorated class
@dataclass
class DecoratedClass:
    name: str


# Multiple decorators
@staticmethod
@property
def multi_decorated_function():
    pass


# If statement with definitions
if __name__ == "__main__":

    def main():
        print("Main function")

    class MainClass:
        pass

    MAIN_VAR = "main"

# If-else with definitions
if DEBUG:

    def debug_function():
        pass

    class DebugClass:
        pass

    DEBUG_VAR = True
else:

    def production_function():
        pass

    class ProductionClass:
        pass

    PROD_VAR = False

# If-elif-else with definitions
if VERSION == "1.0.0":

    def v1_function():
        pass
elif VERSION == "2.0.0":

    def v2_function():
        pass

    class V2Class:
        pass
else:

    def default_function():
        pass


# Nested definitions (should NOT be captured)
class OuterClass:
    def inner_method(self):
        pass

    class InnerClass:
        pass

    INNER_VAR = "nested"


def outer_function():
    def inner_function():
        pass

    class InnerClass:
        pass

    inner_var = "nested"


# Decorated definitions in if blocks
if True:
    IF_VAR = "if"

    def if_function():
        pass

    @decorator
    def decorated_if_function():
        def decorated_if_inner_function():
            pass

    @dataclass
    class DecoratedIfClass:
        pass
else:

    def else_function():
        pass

    ELSE_VAR = "else"


@first_decorator
@second_decorator
class DoubleDecoratedClass:
    pass
