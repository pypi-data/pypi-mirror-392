from .ensure_utils import *
def get_allowed_predicate(allowed=None):
    if allowed != False:
        if allowed == True:
            allowed = None
        allowed = allowed or make_allowed_predicate()
    else:
        def allowed(*args):
            return True
        allowed = allowed
    return allowed
def get_globs(items,recursive: bool = True,allowed=None):
    glob_paths = []
    items = [item for item in make_list(items) if item]
    for item in items:
        pattern = os.path.join(item, "**/*")  # include all files recursively\n
        nuItems = glob.glob(pattern, recursive=recursive)
        if allowed:
            nuItems = [nuItem for nuItem in nuItems if nuItem and allowed(nuItem)]
        glob_paths += nuItems
    return glob_paths
def get_allowed_files(items,allowed=True):
    allowed = get_allowed_predicate(allowed=allowed)
    return [item for item in items if item and os.path.isfile(item) and allowed(item)]
def get_allowed_dirs(items,allowed=False):
    allowed = get_allowed_predicate(allowed=allowed)
    return [item for item in items if item and os.path.isdir(item) and allowed(item)]

def get_filtered_files(items,allowed=None,files = []):
    allowed = get_allowed_predicate(allowed=allowed)
    glob_paths = get_globs(items)
    return [glob_path for glob_path in glob_paths if glob_path and os.path.isfile(glob_path) and glob_path not in files and allowed(glob_path)]
def get_filtered_dirs(items,allowed=None,dirs = []):
    allowed = get_allowed_predicate(allowed=allowed)
    glob_paths = get_globs(items)
    return [glob_path for glob_path in glob_paths if glob_path and os.path.isdir(glob_path) and glob_path not in dirs and allowed(glob_path)]

def get_all_allowed_files(items,allowed=None):
    dirs = get_all_allowed_dirs(items)
    files = get_allowed_files(items)
    nu_files = []
    for directory in dirs:
        files += get_filtered_files(directory,allowed=allowed,files=files)
    return files
def get_all_allowed_dirs(items,allowed=None):
    allowed = get_allowed_predicate(allowed=allowed)
    dirs = get_allowed_dirs(items)
    nu_dirs=[]
    for directory in dirs:
        nu_dirs += get_filtered_dirs(directory,allowed=allowed,dirs=nu_dirs)
    return nu_dirs

def make_allowed_predicate(cfg: ScanConfig) -> Callable[[str], bool]:
    """
    Build a predicate that returns True if a given path is considered allowed
    under the given ScanConfig. Applies allowed_* and exclude_* logic symmetrically.
    """
    def allowed(path: str=None,p=None) -> bool:
        p = p or Path(path)
        name = p.name.lower()
        path_str = str(p).lower()

        # --------------------
        # A) directory filters
        # --------------------
        if cfg.exclude_dirs:
            for dpat in cfg.exclude_dirs:
                dpat_l = dpat.lower()
                if dpat_l in path_str or fnmatch.fnmatch(name, dpat_l):
                    if p.is_dir() or dpat_l in path_str:
                        return False

        if cfg.allowed_dirs and cfg.allowed_dirs != ["*"]:
            # must be in at least one allowed dir
            if not any(
                fnmatch.fnmatch(path_str, f"*{dpat.lower()}*") for dpat in cfg.allowed_dirs
            ):
                return False

        # --------------------
        # B) pattern filters
        # --------------------
        if cfg.allowed_patterns and cfg.allowed_patterns != ["*"]:
            if not any(fnmatch.fnmatch(name, pat.lower()) for pat in cfg.allowed_patterns):
                return False

        if cfg.exclude_patterns:
            for pat in cfg.exclude_patterns:
                if fnmatch.fnmatch(name, pat.lower()):
                    return False

        # --------------------
        # C) extension filters
        # --------------------
        if p.is_file():
            ext = p.suffix.lower()
            if cfg.allowed_exts and ext not in cfg.allowed_exts:
                return False
            if cfg.exclude_exts and ext in cfg.exclude_exts:
                return False

        # --------------------
        # D) type filters (optional)
        # --------------------
        if cfg.allowed_types and cfg.allowed_types != {"*"}:
            if not any(t in path_str for t in cfg.allowed_types):
                return False
        if cfg.exclude_types and cfg.exclude_types != {"*"}:
            if any(t in path_str for t in cfg.exclude_types):
                return False

        return True

    return allowed
