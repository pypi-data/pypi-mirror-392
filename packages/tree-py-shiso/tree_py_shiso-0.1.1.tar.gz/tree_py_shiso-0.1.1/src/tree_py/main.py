import argparse
import sys
from pathlib import Path
from .core import generate_tree
from .display import print_tree

def main():
    # Ensure UTF-8 output for PowerShell compatibility with tree characters
    sys.stdout.reconfigure(encoding='utf-8')
    
    parser = argparse.ArgumentParser(description="A directory tree generator", add_help=False)
    parser.add_argument("--help", action="help", help="show this help message and exit")
    parser.add_argument("path", nargs="?", default=".", help="Directory path")
    parser.add_argument("-a", action="store_true", help="All files are listed.")
    parser.add_argument("-d", action="store_true", help="List directories only.")
    parser.add_argument("-L", type=int, default=None, help="Max display depth of the directory tree.")
    parser.add_argument("-f", action="store_true", help="Print the full path prefix for each file.")
    parser.add_argument("-i", action="store_true", help="Makes tree not print the indentation lines, useful when used in conjunction with the -f option.")
    parser.add_argument("-h", action="store_true", help="Print the size in a more human readable way.")
    parser.add_argument("-p", action="store_true", help="Print the file type and permissions for each file.")
    parser.add_argument("-C", action="store_true", help="Turn colorization on always.")
    parser.add_argument("-I", type=str, help="Do not list files that match the given pattern.")
    parser.add_argument("-P", type=str, help="List only those files that match the pattern.")
    parser.add_argument("--prune", action="store_true", help="Makes tree prune empty directories from the output.")
    parser.add_argument("--dirsfirst", action="store_true", help="List directories before files.")
    
    args = parser.parse_args()
    
    root_path = Path(args.path)
    if not root_path.exists():
        print(f"tree: {args.path}: No such file or directory")
        sys.exit(1)
        
    tree_generator = generate_tree(root_path, args)
    print_tree(tree_generator, args)

if __name__ == "__main__":
    main()
