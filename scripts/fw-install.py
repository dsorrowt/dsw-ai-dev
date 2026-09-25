"""Install and uninstall the framework's global artifacts (stdlib, python3 only).

    scripts/fw-install.py install
    scripts/fw-install.py uninstall [--dry-run]

The source tree is the only state. 'install' copies skills/<name>/** and agents/fw-*.md into
~/.agents/skills/<name>/** and ~/.omp/agent/agents/fw-*.md; 'uninstall' deletes exactly the
destinations that the same tree describes. Nothing is recorded anywhere, so a second 'install'
over unchanged sources writes nothing and reports every file as unchanged - that repeated run is
the drift check, and deleting a state file cannot strand an installation, because there is none.

A destination that differs from its source is rewritten (still exit 0): the managed roots are this
framework's namespace, so whatever sits at a planned path - an older copy, an operator edit, a
foreign file - is replaced by what the tree describes, and 'uninstall' deletes it the same way.
The two consequences worth knowing:

- a copy whose source was deleted from the tree is invisible to both commands and stays behind;
- editing or replacing an installed copy is not preserved: the next command undoes it.

Content the plan does not name is never touched: a directory that still holds such content is
reported and left alone, and files outside the managed roots are never read or removed.

Every write goes through a directory chain opened without following symlinks and lands through
'os.replace', so a symlink swapped in after the checks cannot redirect it. A symlink anywhere in
the source tree, a source path the walk cannot read, a symlink or a non-file at a planned
destination, or a destination whose parent is a file refuses the run (exit 2) before anything is
written. 'uninstall' removes the files, then the empty directories below the managed roots,
deepest first.

Exit codes: 0 - done ('--dry-run' printed a plan), 2 - refused or failed (a partial run names the
paths already changed), 3 - 'uninstall' found nothing this framework installs.
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import os
import re
import stat
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, NoReturn, Sequence

SKILLS_DEST_REL = Path(".agents/skills")
AGENTS_DEST_REL = Path(".omp/agent/agents")
AGENT_PATTERN = "fw-*.md"

#: Roots allowed to hold installed files: every destination is built strictly inside one of them.
MANAGED_DEST_RELS = (SKILLS_DEST_REL, AGENTS_DEST_REL)

EXIT_OK = 0
EXIT_ERROR = 2
EXIT_NOT_INSTALLED = 3

SKIPPED_NAMES = frozenset({".DS_Store"})


class InstallError(Exception):
    """Fatal condition detected before any install location was modified."""


class PartialWriteError(InstallError):
    """A filesystem failure raised after some paths had already been changed."""

    def __init__(self, message: str, applied: Sequence[Path] = ()) -> None:
        if applied:
            note = f"{len(applied)} path(s) already changed, e.g. {applied[0]}"
            message = f"{message}\n  {note}; re-run the same command to finish or reconcile."
        super().__init__(message)


@dataclass
class Plan:
    """The file set the source tree describes: destination (absolute) -> source file."""

    root: Path
    home: Path
    files: dict[Path, Path] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


def fail(message: str) -> NoReturn:
    raise InstallError(message)


def refuse(summary: str, problems: Sequence[str], hint: str) -> NoReturn:
    """Refuse before anything changed: one message shape for both commands."""
    fail(f"{summary}:\n  " + "\n  ".join(problems) + f"\n{hint}")


def shown(paths: Sequence[object], limit: int = 3) -> str:
    """'a, b, c' or 'a, b and N more' for reports."""
    head = ", ".join(str(path) for path in paths[:limit])
    return head if len(paths) <= limit else f"{head} and {len(paths) - limit} more"


def managed_roots(home: Path) -> tuple[Path, ...]:
    return tuple(home / rel for rel in MANAGED_DEST_RELS)


def symlink_below(path: Path, base: Path) -> Path | None:
    """First component of path at or below base that is a symbolic link, or None."""
    if not path.is_relative_to(base):
        return None
    current = base
    for part in path.relative_to(base).parts:
        current = current / part
        if current.is_symlink():
            return current
    return None


def assert_real_paths(paths: Iterable[Path], home: Path, action: str) -> None:
    """Refuse to act while a target path traverses a symlink."""
    for path in sorted(paths):
        link = symlink_below(path, home)
        if link is not None:
            fail(
                f"refusing to {action} {path}: {link} is a symbolic link and the framework never "
                "follows symlinks inside its install locations"
            )


def open_parent(home: Path, target: Path) -> int:
    """Open target's directory below home, creating missing levels; no level may be a symlink.

    Each component is opened with O_NOFOLLOW and kept as a file descriptor, so a directory
    swapped for a symlink while the command runs cannot redirect what is written there.
    """
    fd = os.open(home, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in target.relative_to(home).parts[:-1]:
            try:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            except FileNotFoundError:
                try:
                    os.mkdir(part, dir_fd=fd)
                except FileExistsError:
                    pass  # a concurrent run created it first
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
    except BaseException:
        os.close(fd)
        raise
    return fd


def fresh_tmp(parent_fd: int, owner: Path, mode: int, applied: Sequence[Path] = ()) -> tuple[int, str]:
    """Open a '.tmp' sibling of owner for writing: the fixed name first, a unique one when busy.

    A busy fixed name that is a symlink is refused outright; anything else - a leftover of a
    crashed run or a concurrent writer - falls back to a private name, so no run eats its
    neighbour's temporary file.
    """
    tmp = owner.name + ".tmp"
    try:
        handle = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode, dir_fd=parent_fd)
    except FileExistsError:
        if stat.S_ISLNK(os.stat(tmp, dir_fd=parent_fd, follow_symlinks=False).st_mode):
            raise PartialWriteError(f"refusing to write through the symlink {owner.parent / tmp}", applied)
        tmp = f"{owner.name}.tmp-{os.getpid()}-{os.urandom(4).hex()}"
        handle = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode, dir_fd=parent_fd)
    return handle, tmp


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def note_kept(blocked: Sequence[Path]) -> None:
    if blocked:
        print(
            f"fw-install: uninstall: kept {len(blocked)} non-empty director"
            f"{'y' if len(blocked) == 1 else 'ies'} ({shown(sorted(blocked))}): they hold content "
            "this framework did not install"
        )


def stuck_note(stuck: Sequence[Path]) -> str:
    one = len(stuck) == 1
    return (
        f"{len(stuck)} director{'y' if one else 'ies'} below the managed roots "
        f"{'is' if one else 'are'} empty but could not be removed: {shown(sorted(stuck))}"
    )


def remove_created_dirs(dirs: Iterable[Path]) -> tuple[list[Path], list[Path], list[Path]]:
    """Remove the deepest directories first: (removed, blocked, stuck).

    'blocked' is not empty: it holds content this framework did not install, which is never
    deleted. 'stuck' is empty and still could not be removed - the caller treats that as a failure.
    """
    removed: list[Path] = []
    blocked: list[Path] = []
    stuck: list[Path] = []
    for directory in sorted(dirs, key=lambda path: len(path.parts), reverse=True):
        try:
            directory.rmdir()
        except FileNotFoundError:
            continue  # a concurrent run removed it first
        except OSError as exc:
            (blocked if exc.errno in (errno.ENOTEMPTY, errno.EEXIST) else stuck).append(directory)
        else:
            removed.append(directory)
    return removed, blocked, stuck


# --- the installable set ----------------------------------------------------


def source_files(top: Path) -> Iterator[Path]:
    """Every regular file under top; a symlink or an unreadable path refuses the run, never skips."""
    def unreadable(exc: OSError) -> NoReturn:
        fail(f"cannot read the source tree {exc.filename}: {exc}")

    for dirpath, dirnames, filenames in os.walk(top, onerror=unreadable):
        for name in dirnames:
            directory = Path(dirpath) / name
            if directory.is_symlink():
                fail(f"source {directory} is a symbolic link and the source tree must contain only real files")
        dirnames.sort()
        for name in sorted(filenames):
            if name in SKIPPED_NAMES:
                continue
            source = Path(dirpath) / name
            try:
                found = os.lstat(source)
            except OSError as exc:
                fail(f"cannot read the source tree {source}: {exc}")
            if stat.S_ISLNK(found.st_mode):
                fail(f"source {source} is a symbolic link and the source tree must contain only real files")
            if not stat.S_ISREG(found.st_mode):
                fail(f"source {source} is not a regular file")
            yield source


def agent_name_declared(path: Path) -> bool:
    """True when the file opens with a frontmatter block that declares 'name'."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    block = re.match(r"\A---\s*\n(.*?)\n---", text, re.S)
    return bool(block and re.search(r"^[ \t]*name[ \t]*:", block.group(1), re.M))


def collect_plan(root: Path, home: Path) -> Plan:
    """List every file the two commands work on, keyed by its absolute destination."""
    skills_src = root / "skills"
    if not skills_src.is_dir():
        fail(f"source tree is incomplete: {skills_src} is not a directory")
    plan = Plan(root=root, home=home)

    for skill_dir in sorted(path for path in skills_src.iterdir() if path.is_dir()):
        if skill_dir.is_symlink():
            fail(f"source {skill_dir} is a symbolic link and the source tree must contain only real files")
        if not (skill_dir / "SKILL.md").is_file():
            plan.warnings.append(f"skills/{skill_dir.name}: no SKILL.md, skipped")
            continue
        dest_dir = home / SKILLS_DEST_REL / skill_dir.name
        for source in source_files(skill_dir):
            plan.files[dest_dir / source.relative_to(skill_dir)] = source

    agents_src = root / "agents"
    for entry in sorted(agents_src.iterdir()) if agents_src.is_dir() else []:
        if entry.is_symlink():
            fail(f"source {entry} is a symbolic link and the source tree must contain only real files")
        if entry.name in SKIPPED_NAMES:
            continue
        if not entry.is_file():
            plan.warnings.append(f"agents/{entry.name}: not a regular file, skipped")
        elif not entry.match(AGENT_PATTERN):
            plan.warnings.append(f"agents/{entry.name}: does not match {AGENT_PATTERN}, skipped")
        else:
            if not agent_name_declared(entry):
                plan.warnings.append(f"agents/{entry.name}: no frontmatter with a 'name' field, installed as is")
            plan.files[home / AGENTS_DEST_REL / entry.name] = entry

    if not plan.files:
        fail(f"no installable files found under {root}")
    return plan


def candidate_dirs(home: Path, destinations: Iterable[Path]) -> set[Path]:
    """The directories 'uninstall' may try to remove: the managed roots and the levels below them."""
    roots = managed_roots(home)
    dirs: set[Path] = set(roots)
    for dest in destinations:
        for root in roots:
            if dest.is_relative_to(root):
                dirs.update(
                    parent for parent in dest.parents if parent != root and parent.is_relative_to(root)
                )
    return dirs


# --- install ----------------------------------------------------------------


def compare(plan: Plan) -> tuple[list[tuple[Path, Path]], list[tuple[Path, Path]], list[Path], dict[Path, str]]:
    """Sort the plan into new, rewritten and unchanged destinations, plus the blocked ones.

    Rewriting is the rule for a destination that differs from its source: the managed roots belong
    to this framework, so an older copy, an operator edit and a foreign file are all replaced by
    what the tree describes. A symlink, a directory or another non-file on the way is a refusal,
    not a rewrite, and it is detected before anything is written.
    """
    new: list[tuple[Path, Path]] = []
    rewritten: list[tuple[Path, Path]] = []
    unchanged: list[Path] = []
    blocked: dict[Path, str] = {}
    for dest, source in sorted(plan.files.items()):
        blocking_parent = next(
            (p for p in dest.parents if p != plan.home and p.exists() and not p.is_dir()), None
        )
        if blocking_parent is not None:
            blocked[blocking_parent] = "expected a directory, found a file"
        elif dest.is_symlink():
            blocked[dest] = "occupied by a symbolic link"
        elif dest.is_dir():
            blocked[dest] = "expected a file, found a directory"
        elif dest.exists() and not dest.is_file():
            blocked[dest] = "expected a regular file, found something else"
        elif not dest.exists():
            new.append((dest, source))
        elif sha256_file(dest) == sha256_file(source):
            unchanged.append(dest)
        else:
            rewritten.append((dest, source))
    return new, rewritten, unchanged, blocked


def apply_writes(pending: Sequence[tuple[Path, Path]], home: Path) -> list[Path]:
    """Write every pending file without following a symlink; a failure names what was written."""
    applied: list[Path] = []
    for dest, source in pending:
        if dest.is_symlink():
            raise PartialWriteError(f"refusing to write through the symlink {dest}", applied)
        parent = None
        try:
            parent = open_parent(home, dest)
            mode = 0o755 if os.stat(source).st_mode & 0o111 else 0o644
            handle, tmp = fresh_tmp(parent, dest, mode, applied)
            with os.fdopen(handle, "wb") as stream:
                stream.write(source.read_bytes())
            os.replace(tmp, dest.name, src_dir_fd=parent, dst_dir_fd=parent)
        except OSError as exc:
            raise PartialWriteError(f"cannot copy {source} -> {dest}: {exc}", applied) from exc
        finally:
            if parent is not None:
                os.close(parent)
        applied.append(dest)
    return applied


def cmd_install(plan: Plan) -> int:
    if not plan.home.is_dir():
        fail(f"refusing to install, nothing was changed: HOME {plan.home} does not exist")
    assert_real_paths(plan.files, plan.home, "install to")
    new, rewritten, unchanged, blocked = compare(plan)
    if blocked:
        refuse(
            "refusing to install, nothing was changed; these destinations are not writable files",
            [f"{path}: {reason}" for path, reason in blocked.items()],
            "(delete or move them by hand, then re-run 'install')",
        )
    apply_writes([*new, *rewritten], plan.home)
    warnings = f", {len(plan.warnings)} warning(s)" if plan.warnings else ""
    print(
        f"fw-install: {len(new)} new, {len(rewritten)} rewritten, {len(unchanged)} unchanged file(s) "
        f"from {plan.root}{warnings}"
    )
    return EXIT_OK


# --- uninstall --------------------------------------------------------------


def cmd_uninstall(plan: Plan, dry_run: bool) -> int:
    home = plan.home
    dirs = candidate_dirs(home, plan.files)
    assert_real_paths({*plan.files, *dirs}, home, "uninstall")

    present: list[Path] = []
    absent: list[Path] = []
    problems: list[str] = []
    for dest in sorted(plan.files):
        if dest.is_symlink():
            problems.append(f"{dest}: reached through a symbolic link")
        elif not dest.exists():
            absent.append(dest)
        elif not dest.is_file():
            problems.append(f"{dest}: expected a file, found something else")
        else:
            present.append(dest)
    if problems:
        refuse(
            "refusing to uninstall, nothing was changed",
            problems,
            "(delete or move those paths by hand, then retry)",
        )
    if not present and not any(directory.is_dir() and not any(directory.iterdir()) for directory in dirs):
        print("fw-install: not installed: nothing this framework installs is present", file=sys.stderr)
        return EXIT_NOT_INSTALLED

    changed = [dest for dest in present if sha256_file(dest) != sha256_file(plan.files[dest])]
    if changed:
        print(
            f"fw-install: note: {len(changed)} file(s) differ from the sources and are removed with "
            f"the rest ({shown(changed)})",
            file=sys.stderr,
        )

    if dry_run:
        print(
            "fw-install: uninstall --dry-run: nothing is changed; plan for "
            f"{len(present)} installed file(s), re-run without --dry-run to apply it"
        )
        print(
            f"fw-install:   would delete {len(present)} file(s) ({len(absent)} already absent) and "
            "remove the directories below the managed roots that become empty"
        )
        return EXIT_OK

    applied: list[Path] = []
    for dest in present:
        try:
            dest.unlink()
        except FileNotFoundError:
            absent.append(dest)  # a concurrent run or the operator got there first
        except OSError as exc:
            raise PartialWriteError(f"cannot delete {dest}: {exc}", applied) from exc
        else:
            applied.append(dest)

    removed, blocked, stuck = remove_created_dirs(dirs)
    if stuck:
        raise PartialWriteError(
            f"refusing to report success: {stuck_note(stuck)}; re-running 'uninstall' removes them "
            "once the cause is fixed",
            applied,
        )
    note_kept(blocked)
    print(
        f"fw-install: uninstall: deleted {len(applied)} installed file(s), {len(absent)} already "
        f"absent; removed {len(removed)} empty director{'y' if len(removed) == 1 else 'ies'} below "
        "the managed roots"
    )
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fw-install.py", description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("install", help="copy the sources into the managed roots, idempotently")
    undo = commands.add_parser("uninstall", help="delete the copies the sources describe")
    undo.add_argument("--dry-run", action="store_true", help="check, print the plan, change nothing")
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    try:
        plan = collect_plan(root, Path.home())
        for warning in plan.warnings:
            print(f"fw-install: warning: {warning}", file=sys.stderr)
        if args.command == "install":
            return cmd_install(plan)
        return cmd_uninstall(plan, dry_run=args.dry_run)
    except InstallError as exc:
        print(f"fw-install: error: {exc}", file=sys.stderr)
        return EXIT_ERROR
    except OSError as exc:
        print(f"fw-install: error: filesystem operation failed: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
