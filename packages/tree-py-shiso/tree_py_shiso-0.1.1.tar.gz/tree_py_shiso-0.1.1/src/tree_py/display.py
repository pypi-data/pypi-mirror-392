import os

# ANSI Colors
RESET = "\033[0m"
BLUE = "\033[1;34m"
GREEN = "\033[1;32m"
CYAN = "\033[36m"

def format_size(size):
    for unit in ['B', 'K', 'M', 'G', 'T', 'P']:
        if size < 1024:
            if unit == 'B':
                return f"{int(size):>4}"
            return f"{size:>3.1f}{unit}"
        size /= 1024
    return f"{size:>3.1f}E"

def print_tree(tree_generator, options):
    """
    Prints the tree structure.
    """
    for path, markers, meta in tree_generator:
        # Root node
        if not markers:
            print(path.name or str(path))
            continue
            
        # Indentation
        prefix = ""
        if not options.i:
            for is_last_ancestor in markers[:-1]:
                if is_last_ancestor:
                    prefix += "    "
                else:
                    prefix += "│   "
            
            if markers[-1]:
                prefix += "└── "
            else:
                prefix += "├── "
        elif options.f:
             # If -i is used, usually we print full path or just relative path without tree lines.
             # If -f is used, we print full path.
             # If neither, we print name.
             # But tree -i -f prints full path. tree -i prints path relative to root?
             # Let's check standard tree -i behavior.
             # tree -i: "Makes tree not print the indentation lines, useful when used in conjunction with the -f option."
             # It just omits the indentation.
             pass

        # Metadata formatting
        meta_str = ""
        if options.p:
            mode = meta.get('mode', '')
            meta_str += f"[{mode}] "
        
        if options.h:
            size = meta.get('size', 0)
            size_str = format_size(size)
            meta_str += f"[{size_str:>5}] "

        # Name formatting
        name = path.name
        if options.f:
            name = str(path)
            
        # Colorization
        if options.C:
            if meta.get('is_dir'):
                name = f"{BLUE}{name}{RESET}"
            elif os.access(path, os.X_OK): # Executable check (rough on Windows)
                name = f"{GREEN}{name}{RESET}"
        
        print(f"{prefix}{meta_str}{name}")
