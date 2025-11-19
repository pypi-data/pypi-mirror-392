# src/repocards/core/fetcher.py
from __future__ import annotations

import base64
import fnmatch
import os
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse

import requests

from ..schemas import FetchedFile, RepoSnapshot

GITHUB_API = "https://api.github.com"

# ------------------------- File selection policy -------------------------

# Keep the include list strongly biased toward human-written, texty content.
INCLUDE_GLOBS = [
    "README*", "readme*",
    "docs/**/*.md", "doc/**/*.md", "documentation/**/*.md",
    ".github/workflows/**/*.yml", ".github/workflows/**/*.yaml",
    "examples/**/*.md", "examples/**/*.py", "examples/**/*.sh",
    "demo/**/*.md", "demo/**/*.py", "demo/**/*.sh",
    "scripts/**/*.py", "scripts/**/*.sh", "scripts/**/CMakeLists.txt", "scripts/**/Makefile",
    "pyproject.toml", "setup.cfg", "setup.py",
    "requirements*.txt", "environment*.yml", "Pipfile", "Pipfile.lock",
    "package.json", "pnpm-lock.yaml", "yarn.lock",
    "Cargo.toml", "Cargo.lock",
    "go.mod", "go.sum",
    "CMakeLists.txt", "**/*.cmake",
    "Makefile", "makefile",
    # NEW: docker files
    "Dockerfile", "docker/**/Dockerfile*", "docker/**/*.yml", "docker/**/*.yaml", "docker/**/*.sh",
]

# Exclude obvious binaries and bulky folders. Do NOT exclude .github (for workflows).
EXCLUDE_GLOBS = [
    ".git/**", "**/.git/**",
    "**/.venv/**", "venv/**", "env/**",
    "data/**", "datasets/**", "docs/_build/**",
    "**/.ipynb_checkpoints/**",
    # Common binary / large formats
    "**/*.png", "**/*.jpg", "**/*.jpeg", "**/*.gif", "**/*.webp",
    "**/*.bmp", "**/*.tif", "**/*.tiff", "**/*.ico",
    "**/*.pdf", "**/*.svgz",
    "**/*.zip", "**/*.tar", "**/*.tar.*", "**/*.7z", "**/*.rar",
    "**/*.dmg", "**/*.exe", "**/*.dll", "**/*.so", "**/*.dylib", "**/*.a",
    "**/*.bin", "**/*.wasm", "**/*.class", "**/*.jar",
    "**/*.pt", "**/*.pth", "**/*.onnx", "**/*.h5", "**/*.ckpt",
    "**/*.parquet", "**/*.feather",
]

# Extensions we consider text-like if encountered elsewhere in the tree.
TEXTY_EXTS = {
    ".md", ".rst", ".txt",
    ".toml", ".cfg", ".ini", ".yml", ".yaml", ".json",
    ".py", ".sh", ".ps1", ".bat",
    ".c", ".h", ".cpp", ".hpp", ".cc", ".cxx",
    ".cmake", ".go", ".rs", ".java", ".gradle",
    ".ts", ".tsx", ".js", ".jsx", ".vue",
    ".mk",  # Make fragments
}

# ------------------------------ Helpers ------------------------------

def _auth_headers(token: Optional[str]) -> Dict[str, str]:
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _parse_repo_url(url: str) -> Tuple[str, str, Optional[str]]:
    """
    Supports: https://github.com/owner/repo[.git][#/tree/<ref>|#<ref>]
    Returns (owner, repo, ref|None).
    """
    u = urlparse(url)
    if u.netloc not in {"github.com", "www.github.com"}:
        raise ValueError("Only GitHub URLs are supported.")
    parts = [p for p in u.path.strip("/").split("/") if p]
    if len(parts) < 2:
        raise ValueError("Invalid GitHub repo URL.")
    owner, repo = parts[0], parts[1].removesuffix(".git")
    ref = None
    # /tree/<ref>
    if len(parts) >= 4 and parts[2] == "tree":
        ref = "/".join(parts[3:])
    # #<ref> fragment
    if u.fragment:
        ref = u.fragment
    return owner, repo, ref

def _matches_any(path: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatch(path, pat) for pat in patterns)

def _looks_texty(path: str) -> bool:
    p = path.lower()
    if p.endswith("cmakelists.txt"):
        return True
    dot = p.rfind(".")
    if dot == -1:
        return False
    return p[dot:] in TEXTY_EXTS

def _rank_candidate(path: str) -> int:
    p = path.lower()
    # highest priority: readme, manifests, workflows
    if p.startswith("readme"): return 0
    if p in ("pyproject.toml","setup.cfg","setup.py","requirements.txt","requirements-dev.txt",
             "package.json","cargo.toml","go.mod","cmakelists.txt","makefile"):
        return 0
    if p.startswith(".github/workflows/"): return 0
    # docs next
    if p.startswith(("docs/","documentation/","doc/")): return 1
    # examples/scripts/build-related
    if "build" in p or p.startswith(("examples/","scripts/","meta/","docker/")): return 2
    return 3

# ------------------------------- Fetcher -------------------------------

def fetch_repo_snapshot_via_api(
    repo_url: str,
    token: Optional[str] = None,
    max_files: int = 160,
    max_bytes_per_file: int = 300_000,
) -> RepoSnapshot:
    """
    Fetch a curated subset of files via the GitHub REST API (no git clone).
    Also fetches repo metadata: description, license, topics, and languages.

    The selection aims to surface human-written docs, manifests, CI workflows,
    and scripts that are most useful for building/running a project.
    """
    owner, name, ref = _parse_repo_url(repo_url)
    session = requests.Session()
    session.headers.update(_auth_headers(token or os.getenv("GITHUB_TOKEN")))

    # --- Repo meta
    r = session.get(f"{GITHUB_API}/repos/{owner}/{name}")
    r.raise_for_status()
    repo = r.json()
    default_branch = repo.get("default_branch", "main")
    description = repo.get("description")
    license_spdx = (repo.get("license") or {}).get("spdx_id") or None

    # Topics
    topics: List[str] = []
    rt = session.get(f"{GITHUB_API}/repos/{owner}/{name}/topics")
    if rt.ok:
        topics = (rt.json().get("names") or [])[:10]

    # Languages
    languages: Dict[str, int] = {}
    rl = session.get(f"{GITHUB_API}/repos/{owner}/{name}/languages")
    if rl.ok and isinstance(rl.json(), dict):
        languages = rl.json()

    # Resolve ref
    if not ref:
        ref = default_branch

    # --- List tree (handles branch name or SHA)
    r = session.get(f"{GITHUB_API}/repos/{owner}/{name}/git/trees/{ref}", params={"recursive": "1"})
    if r.status_code == 422:  # ref may be a branch name; resolve to SHA
        rb = session.get(f"{GITHUB_API}/repos/{owner}/{name}/branches/{ref}")
        rb.raise_for_status()
        sha = rb.json()["commit"]["sha"]
        r = session.get(f"{GITHUB_API}/repos/{owner}/{name}/git/trees/{sha}", params={"recursive": "1"})
    r.raise_for_status()
    tree = r.json().get("tree", [])

    # --- Choose candidate paths
    candidate_paths: List[str] = []
    for node in tree:
        if node.get("type") != "blob":
            continue
        path = node["path"]
        # basic filters
        if _matches_any(path, EXCLUDE_GLOBS):
            continue
        if _matches_any(path, INCLUDE_GLOBS) or _looks_texty(path):
            candidate_paths.append(path)

    candidate_paths = sorted(candidate_paths, key=_rank_candidate)

    truncated = False
    if len(candidate_paths) > max_files:
        candidate_paths = candidate_paths[:max_files]
        truncated = True

    # --- Fetch file contents (text only, size-capped)
    files: List[FetchedFile] = []
    for path in candidate_paths:
        rr = session.get(f"{GITHUB_API}/repos/{owner}/{name}/contents/{path}", params={"ref": ref})
        if rr.status_code == 404:
            continue
        rr.raise_for_status()
        meta = rr.json()
        if isinstance(meta, list):
            continue  # directory
        size = int(meta.get("size") or 0)
        if size > max_bytes_per_file:
            truncated = True
            continue
        enc = meta.get("encoding")
        content_b64 = meta.get("content") or ""
        text = ""
        if enc == "base64":
            try:
                text = base64.b64decode(content_b64).decode("utf-8", errors="replace")
            except Exception:
                # skip undecodable blobs
                continue
        else:
            text = content_b64
        files.append(FetchedFile(path=path, content=text))

    return RepoSnapshot(
        owner=owner,
        name=name,
        ref=ref,
        description=description,
        license_spdx=license_spdx,
        topics=topics,
        files=files,
        truncated=truncated,
        languages=languages,
    )
