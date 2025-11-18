import os

def print_source_code(file_name):
    """
    Print the contents of a Python model or utility file.
    
    Args:
        file_name (str): Name of the file without .py extension
    
    Returns:
        None: Prints the file contents or lists available files if not found
    """
    # Get base directory
    base_dir = os.path.dirname(__file__)
    
    # Define directories to search
    search_dirs = {
        'models': os.path.join(base_dir, 'models'),
        'utils': os.path.join(base_dir, 'utils'),
        'simple': os.path.join(base_dir, 'simple'),
        'tasks': os.path.join(base_dir, 'tasks')
    }
    
    # Try to find the file in both directories
    for dir_name, dir_path in search_dirs.items():
        file_path = os.path.join(dir_path, f'{file_name}.py')
        
        if os.path.isfile(file_path):
            # Found the file, print its contents
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    print(f"Contents of {file_name}.py from {dir_name} directory:\n")
                    print(content)
                return
            except Exception as e:
                print(f"Error reading file '{file_name}.py': {str(e)}")
                return
    
    # If we reach here, the file wasn't found in either directory
    print(f"Error: '{file_name}.py' not found.")
    print("\nAvailable files:")
    
    # List all available files in both directories
    for dir_name, dir_path in search_dirs.items():
        if os.path.exists(dir_path):
            files = [f[:-3] for f in os.listdir(dir_path) if f.endswith('.py')]
            print(f"\n{dir_name.capitalize()} directory:")
            if files:
                for file in sorted(files):
                    print(f"  - {file}")
            else:
                print("  No Python files found")
        else:
            print(f"\n{dir_name.capitalize()} directory does not exist")
