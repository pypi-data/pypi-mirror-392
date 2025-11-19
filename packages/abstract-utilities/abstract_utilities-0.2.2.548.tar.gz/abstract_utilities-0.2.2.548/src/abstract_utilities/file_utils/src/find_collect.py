from ..imports import *
from .file_filters import *

def _fast_walk(
    root: Path,
    exts: Iterable[str],
    skip_dirs: Iterable[str] = (),
    skip_patterns: Iterable[str] = (),
) -> List[Path]:
    exts = tuple(exts)
    skip_dirs = set(sd.lower() for sd in skip_dirs or ())
    skip_patterns = tuple(sp.lower() for sp in (skip_patterns or ()))

    out = []
    for p in root.rglob("*"):
        # skip directories by name hit
        if p.is_dir():
            name = p.name.lower()
            if name in skip_dirs:
                # rglob doesn't let us prune mid-iteration cleanly; we just won't collect under it
                continue
            # nothing to collect for dirs
            continue

        # file filters
        name = p.name.lower()
        if any(fnmatch.fnmatch(name, pat) for pat in skip_patterns):
            continue
        if p.suffix.lower() in exts:
            out.append(p)

    # de-dup and normalize
    return sorted({pp.resolve() for pp in out})


def enumerate_source_files(
    src_root: Path,
    cfg: Optional["ScanConfig"] = None,
    *,
    exts: Optional[Iterable[str]] = None,
    fast_skip_dirs: Optional[Iterable[str]] = None,
    fast_skip_patterns: Optional[Iterable[str]] = None,
) -> List[Path]:
    """
    Unified enumerator:
      - If `cfg` is provided: use collect_filepaths(...) with full rules.
      - Else: fast walk using rglob over `exts` (defaults to EXTS) with optional light excludes.
    """
    src_root = Path(src_root)

    if cfg is not None:
        files = collect_filepaths([str(src_root)], cfg=cfg)
        return sorted({Path(f).resolve() for f in files})

    # Fast mode
    return _fast_walk(
        src_root,
        exts or EXTS,
        skip_dirs=fast_skip_dirs or (),
        skip_patterns=fast_skip_patterns or (),
    )

def get_find_cmd(
    *args,
    mindepth: Optional[int] = None,
    maxdepth: Optional[int] = None,
    depth: Optional[int] = None,
    file_type: Optional[str] = None,  # 'f' or 'd'
    name: Optional[str] = None,
    size: Optional[str] = None,
    mtime: Optional[str] = None,
    perm: Optional[str] = None,
    user: Optional[str] = None,
    **kwargs
) -> str:
    """
    Construct a Unix `find` command string that supports multiple directories.
    Accepts filtering via ScanConfig-compatible kwargs.
    """
    # Normalize inputs into canonical form
    kwargs = get_safe_canonical_kwargs(*args, **kwargs)
    cfg = define_defaults(**kwargs)

    # Get directory list (may come from args or kwargs)
    kwargs["directories"] = ensure_directories(*args, **kwargs)
    if not kwargs["directories"]:
        return []

    # Build base command for all directories
    dir_expr = " ".join(shlex.quote(d) for d in kwargs["directories"])
    cmd = [f"find {dir_expr}"]

    # --- depth filters ---
    if depth is not None:
        cmd += [f"-mindepth {depth}", f"-maxdepth {depth}"]
    else:
        if mindepth is not None:
            cmd.append(f"-mindepth {mindepth}")
        if maxdepth is not None:
            cmd.append(f"-maxdepth {maxdepth}")

    # --- file type ---
    if file_type in ("f", "d"):
        cmd.append(f"-type {file_type}")

    # --- basic attributes ---
    if name:
        cmd.append(f"-name {shlex.quote(name)}")
    if size:
        cmd.append(f"-size {shlex.quote(size)}")
    if mtime:
        cmd.append(f"-mtime {shlex.quote(mtime)}")
    if perm:
        cmd.append(f"-perm {shlex.quote(perm)}")
    if user:
        cmd.append(f"-user {shlex.quote(user)}")

    # --- cfg-based filters ---
    if cfg:
        # Allowed extensions
        if cfg.allowed_exts and cfg.allowed_exts != {"*"}:
            ext_expr = " -o ".join(
                [f"-name '*{e}'" for e in cfg.allowed_exts if e]
            )
            cmd.append(f"\\( {ext_expr} \\)")

        # Excluded extensions
        if cfg.exclude_exts:
            for e in cfg.exclude_exts:
                cmd.append(f"! -name '*{e}'")

        # Allowed directories
        if cfg.allowed_dirs and cfg.allowed_dirs != ["*"]:
            dir_expr = " -o ".join(
                [f"-path '*{d}*'" for d in cfg.allowed_dirs if d]
            )
            cmd.append(f"\\( {dir_expr} \\)")

        # Excluded directories
        if cfg.exclude_dirs:
            for d in cfg.exclude_dirs:
                cmd.append(f"! -path '*{d}*'")

        # Allowed patterns
        if cfg.allowed_patterns and cfg.allowed_patterns != ["*"]:
            pat_expr = " -o ".join(
                [f"-name '{p}'" for p in cfg.allowed_patterns if p]
            )
            cmd.append(f"\\( {pat_expr} \\)")

        # Excluded patterns
        if cfg.exclude_patterns:
            for p in cfg.exclude_patterns:
                cmd.append(f"! -name '{p}'")

        # Allowed types (semantic, not `-type`)
        if cfg.allowed_types and cfg.allowed_types != {"*"}:
            type_expr = " -o ".join(
                [f"-path '*{t}*'" for t in cfg.allowed_types if t]
            )
            cmd.append(f"\\( {type_expr} \\)")

        # Excluded types
        if cfg.exclude_types:
            for t in cfg.exclude_types:
                cmd.append(f"! -path '*{t}*'")

    return " ".join(cmd)

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

def collect_globs(
    *args,
    mindepth: Optional[int] = None,
    maxdepth: Optional[int] = None,
    depth: Optional[int] = None,
    file_type: Optional[str] = None,   # "f", "d", or None
    allowed: Optional[Callable[[str], bool]] = None,
    **kwargs
) -> List[str] | dict:
    """
    Collect file or directory paths recursively.

    - If file_type is None → returns {"f": [...], "d": [...]}
    - If file_type is "f" or "d" → returns a list of that type
    - Supports SSH mode via `user_at_host`
    """
    kwargs["directories"] = ensure_directories(*args, **kwargs)
    kwargs= get_safe_canonical_kwargs(**kwargs)
    kwargs["cfg"] = define_defaults(**kwargs)
    
    type_strs = {"f":"files","d":"dirs"}
    file_type = get_proper_type_str(file_type)
    file_types = make_list(file_type)
    if file_type == None:
        file_types = ["f","d"]
    return_results = {}
    return_result=[]
    for file_type in file_types:
        type_str = type_strs.get(file_type)
        # Remote path (SSH)
        find_cmd = get_find_cmd(
                mindepth=mindepth,
                maxdepth=maxdepth,
                depth=depth,
                file_type=file_type,
                **{k: v for k, v in kwargs.items() if v},
            )
        result = run_pruned_func(run_cmd,find_cmd,
            **kwargs
            
            )
        return_result = [res for res in result.split('\n') if res]
        return_results[type_str]=return_result
    if len(file_types) == 1:
        return return_result
    return return_results
def get_files_and_dirs(
    *args,
    recursive: bool = True,
    include_files: bool = True,
    **kwargs
    ):
    if recursive == False:
        kwargs['maxdepth']=1
    if include_files == False:
        kwargs['file_type']='d'
    result = collect_globs(*args,**kwargs)
    if include_files == False:
        return result,[]
    dirs = result.get("dirs")
    files = result.get("files")
    return dirs,files
def collect_filepaths(
    *args,
    **kwargs
    ) -> List[str]:
    kwargs['file_type']='f'
    return collect_globs(*args,**kwargs)
