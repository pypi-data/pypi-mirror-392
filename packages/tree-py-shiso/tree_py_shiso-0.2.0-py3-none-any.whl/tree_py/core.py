import os
import fnmatch
import stat
from pathlib import Path

def get_metadata(path, options):
    meta = {}
    try:
        st = path.stat()
        if options.p:
            meta['mode'] = stat.filemode(st.st_mode)
        if options.h:
            meta['size'] = st.st_size
        meta['is_dir'] = path.is_dir()
    except Exception:
        pass
    return meta

def is_excluded(name, options):
    if options.I:
        # Support multiple patterns separated by |
        patterns = options.I.split('|')
        for pat in patterns:
            if fnmatch.fnmatch(name, pat):
                return True
    return False

def is_included(name, is_dir, options):
    if is_dir:
        return True
    if options.P:
        patterns = options.P.split('|')
        match = False
        for pat in patterns:
            if fnmatch.fnmatch(name, pat):
                match = True
                break
        if not match:
            return False
    return True

def has_valid_children(path, options):
    try:
        for item in path.iterdir():
            name = item.name
            if not options.a and name.startswith('.'):
                continue
            if is_excluded(name, options):
                continue
            
            if item.is_dir():
                if has_valid_children(item, options):
                    return True
            else:
                if options.d: continue
                if is_included(name, False, options):
                    return True
    except PermissionError:
        pass
    return False

def generate_tree(root_path, options, markers=None):
    """
    Generator that yields (path, markers, metadata).
    """
    if markers is None:
        markers = []
        yield root_path, [], get_metadata(root_path, options)

    if options.L is not None and len(markers) >= options.L:
        return

    try:
        items = list(root_path.iterdir())
    except PermissionError:
        return

    # Filter items
    filtered_items = []
    for item in items:
        name = item.name
        if not options.a and name.startswith('.'):
            continue
        if is_excluded(name, options):
            continue
        
        if item.is_dir():
            if options.prune:
                if not has_valid_children(item, options):
                    continue
            filtered_items.append(item)
        else:
            if options.d:
                continue
            if is_included(name, False, options):
                filtered_items.append(item)

    # Sort items
    if options.dirsfirst:
        filtered_items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
    else:
        filtered_items.sort(key=lambda x: x.name.lower())

    # Iterate and recurse
    for i, item in enumerate(filtered_items):
        is_last = (i == len(filtered_items) - 1)
        current_markers = markers + [is_last]
        
        yield item, current_markers, get_metadata(item, options)
        
        if item.is_dir():
            yield from generate_tree(item, options, current_markers)
