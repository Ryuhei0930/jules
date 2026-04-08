import ast

def check_model_name():
    with open('app.py', 'r') as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'generate_content':
                for keyword in node.keywords:
                    if keyword.arg == 'model':
                        if isinstance(keyword.value, ast.Constant):
                            print(f"Model used: {keyword.value.value}")
                            assert keyword.value.value == 'gemini-3.1-flash-image-preview', "Wrong model name"

if __name__ == '__main__':
    check_model_name()
    print("Model check passed.")
