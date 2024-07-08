import ast
import sys

def extract_global_variables(script_path):
    with open(script_path, 'r') as file:
        script_content = file.read()

    # Parse the script content using ast.parse() and extract the global variables
    tree = ast.parse(script_content)
    global_vars = {}

    # Check Python version and set literal node types accordingly
    if sys.version_info >= (3, 8):
        # Python 3.8 and above
        literal_nodes = (ast.Constant,)
    else:
        # Python 3.7 and below, including Python 2.x and IronPython
        literal_nodes = (ast.Num, ast.Str, ast.List, ast.Dict, ast.Tuple)
        if sys.version_info[0] == 2:
            # Additional types for Python 2.x
            literal_nodes += (ast.Str,)

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    if isinstance(node.value, literal_nodes):
                        var_value = ast.literal_eval(node.value)
                    else:
                        try:
                            # Fallback for other types using literal_eval for safe evaluation
                            var_value = ast.literal_eval(node.value)
                        except ValueError:
                            # For non-literals or complex cases, keep a representation of the code
                            var_value = "Unsupported value for safe evaluation"
                    global_vars[var_name] = var_value

    return global_vars
