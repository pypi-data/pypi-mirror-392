#!/usr/bin/env python3

import sys

import tree_sitter_python as tspython
from tree_sitter import Language, Parser


def main():
    if len(sys.argv) != 2:
        print("Usage: python ts_playground.py <python_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, "rb") as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)

    # Setup Tree-sitter
    PYTHON_LANGUAGE = Language(tspython.language())
    parser = Parser()
    parser.language = PYTHON_LANGUAGE

    # Parse the file
    tree = parser.parse(source_code)

    # Query for top-level and if-block definitions
    query = PYTHON_LANGUAGE.query("""
    [
      ; Direct module children
      (module 
        (function_definition name: (identifier) @function-name))
      (module 
        (class_definition name: (identifier) @class-name))
      (module 
        (decorated_definition 
          (function_definition name: (identifier) @function-name)))
      (module 
        (decorated_definition 
          (class_definition name: (identifier) @class-name)))
      (module 
        (expression_statement 
          (assignment left: (identifier) @assignment-name)))

      ; Inside top-level if statements
      (module
        (if_statement
          (block
            (function_definition name: (identifier) @function-name))))
      (module
        (if_statement
          (block
            (class_definition name: (identifier) @class-name))))
      (module
        (if_statement
          (block
            (decorated_definition 
              (function_definition name: (identifier) @function-name)))))
      (module
        (if_statement
          (block
            (decorated_definition 
              (class_definition name: (identifier) @class-name)))))
      (module
        (if_statement
          (block
            (expression_statement 
              (assignment left: (identifier) @assignment-name)))))
      ; Else clause
      (module
        (if_statement
          (else_clause
            (block
              (function_definition name: (identifier) @function-name)))))
      (module
        (if_statement
          (else_clause
            (block
              (class_definition name: (identifier) @class-name)))))
      (module
        (if_statement
          (else_clause
            (block
              (decorated_definition 
                (function_definition name: (identifier) @function-name))))))
      (module
        (if_statement
          (else_clause
            (block
              (decorated_definition 
                (class_definition name: (identifier) @class-name))))))
      (module
        (if_statement
          (else_clause
            (block
              (expression_statement 
                (assignment left: (identifier) @assignment-name))))))
    ]
    """)

    print(f"Top-level items in {file_path}:")
    print("-" * 40)

    captures = query.captures(tree.root_node)

    if not captures:
        print("No top-level items found.")
        return

    # Print functions
    functions = captures.get("function-name", [])
    if functions:
        print("Functions:")
        for node in functions:
            line_num = node.start_point[0] + 1
            func_name = node.text.decode("utf-8")
            print(f"  Line {line_num}: {func_name}")

    # Print classes
    classes = captures.get("class-name", [])
    if classes:
        print("Classes:")
        for node in classes:
            line_num = node.start_point[0] + 1
            class_name = node.text.decode("utf-8")
            print(f"  Line {line_num}: {class_name}")

    # Print assignments
    assignments = captures.get("assignment-name", [])
    if assignments:
        print("Assignments:")
        for node in assignments:
            line_num = node.start_point[0] + 1
            var_name = node.text.decode("utf-8")
            print(f"  Line {line_num}: {var_name}")


if __name__ == "__main__":
    main()
