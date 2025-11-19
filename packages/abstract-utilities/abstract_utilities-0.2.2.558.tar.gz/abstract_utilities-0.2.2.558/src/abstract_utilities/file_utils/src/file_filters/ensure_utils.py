from .filter_utils import *
def normalize_listlike(value, typ=list, sep=','):
    """Normalize comma-separated or iterable values into the desired type."""
    if value in [True, None, False]:
        return value
    if isinstance(value, str):
        value = [v.strip() for v in value.split(sep) if v.strip()]
    return typ(value)

def ensure_exts(exts):
    if exts in [True, None, False]:
        return exts
    out = []
    for ext in normalize_listlike(exts, list):
        if not ext.startswith('.'):
            ext = f".{ext}"
        out.append(ext)
    return set(out)

def ensure_patterns(patterns):
    """Normalize pattern list and ensure they are valid globs."""
    if patterns in [True, None, False]:
        return patterns
    patterns = normalize_listlike(patterns, list)
    out = []
    for pattern in patterns:
        if not pattern:
            continue
        if '*' not in pattern and '?' not in pattern:
            # Implicitly make it a prefix match
            if pattern.startswith('.') or pattern.startswith('~'):
                pattern = f"*{pattern}"
            else:
                pattern = f"{pattern}*"
        out.append(pattern)
    return out
def ensure_directories(*args,**kwargs):
    directories = []
    for arg in args:
        arg_str = str(arg)
        if is_dir(arg_str,**kwargs):
            directories.append(arg_str)
        elif is_file(arg_str,**kwargs):
            dirname = os.path.dirname(arg_str)
            directories.append(dirname)
    safe_directories = get_dir_filter_kwargs(**kwargs)
    directories+= make_list(safe_directories.get('directories',[]))
    return list(set([r for r in directories if r]))
def get_proper_type_str(string):
    if not string:
        return None
    string_lower = string.lower()
    items = {
        "d":["dir","dirs","directory","directories","d","dirname"],
        "f":["file","filepath","file_path","files","filepaths","file_paths","f"]
     }
    for key,values in items.items():
        if string_lower in values:
            return key
    init = string_lower[0] if len(string_lower)>0 else None
    if init in items:
        return init
def check_path_type(
    path: str,
    user: Optional[str] = None,
    host: Optional[str] = None,
    user_as_host: Optional[str] = None,
    use_shell: bool = False
) -> Literal["file", "directory", "missing", "unknown"]:
    """
    Determine whether a given path is a file, directory, or missing.
    Works locally or remotely (via SSH).

    Args:
        path: The path to check.
        user, host, user_as_host: SSH parameters if remote.
        use_shell: Force shell test instead of Python os.path.
    Returns:
        One of: 'file', 'directory', 'missing', or 'unknown'
    """

    # --- remote check if user/host is given ---
    if user_as_host or (user and host):
        remote_target = user_as_host or f"{user}@{host}"
        cmd = f"if [ -f '{path}' ]; then echo file; elif [ -d '{path}' ]; then echo directory; else echo missing; fi"
        try:
            result = subprocess.check_output(
                ["ssh", remote_target, cmd],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=5
            ).strip()
            return result if result in ("file", "directory", "missing") else "unknown"
        except Exception:
            return "unknown"

    # --- local check ---
    if not use_shell:
        if os.path.isfile(path):
            return "file"
        elif os.path.isdir(path):
            return "directory"
        elif not os.path.exists(path):
            return "missing"
        return "unknown"
    else:
        # fallback using shell tests (useful for sandboxed contexts)
        cmd = f"if [ -f '{path}' ]; then echo file; elif [ -d '{path}' ]; then echo directory; else echo missing; fi"
        try:
            output = subprocess.check_output(
                cmd, shell=True, stderr=subprocess.DEVNULL, text=True
            ).strip()
            return output if output in ("file", "directory", "missing") else "unknown"
        except Exception:
            return "unknown"
