# tree-py

A Python implementation of the `tree` command, designed for Windows but compatible with other platforms. It provides a feature-rich command-line utility to recursively list directories in a tree-like format.

## Installation

```bash
uv tool install tree-py
```

## Usage

```bash
tree-py [options] [directory]
```

### Common Options

| Flag | Description |
| :--- | :--- |
| `-L <level>` | Max display depth of the directory tree. |
| `-d` | List directories only. |
| `-a` | All files are listed (including hidden files). |
| `-f` | Print the full path prefix for each file. |
| `-i` | Makes tree not print the indentation lines. |
| `-h` | Print the size in a human readable way. |
| `-p` | Print the file type and permissions. |
| `-C` | Turn colorization on always. |
| `-I <pattern>` | Do not list files that match the given pattern. |
| `-P <pattern>` | List only those files that match the pattern. |
| `--prune` | Prune empty directories from the output. |
| `--dirsfirst` | List directories before files. |

### Examples

**Project Overview:**
```bash
tree-py -L 2 -I "node_modules|__pycache__" --dirsfirst
```

**Find specific files:**
```bash
tree-py -P "*.json" --prune
```

**Flat list with full paths:**
```bash
tree-py -i -f
```
