# example_utils.py
# ─────────────────────────────────────────────────────────────────────────────
# WebFileManager — using the helper utilities without starting the server
# Useful for scripts that need filesystem info or path helpers.
# ─────────────────────────────────────────────────────────────────────────────

from WebFileManager import fmt_size, disk_stats, list_dir
from WebFileManager.utils import join_path, resolve, sanitise_name

# ── disk usage ────────────────────────────────────────────────────────────────
free, used, total = disk_stats('/')
print("Free :", free)
print("Used :", used)
print("Total:", total)

# ── directory listing ─────────────────────────────────────────────────────────
print("\nFiles in /:")
for name, size, is_directory in list_dir('/', '/'):
    kind = "DIR " if is_directory else "FILE"
    print("  [{}]  {}  {}".format(kind, name, "" if is_directory else fmt_size(size)))

# ── path helpers ──────────────────────────────────────────────────────────────
print("\nPath helpers:")
print(join_path("/data", "notes.txt"))          # -> /data/notes.txt
print(resolve("/", "/subdir/file.txt"))         # -> /subdir/file.txt
print(sanitise_name("../../etc/passwd"))        # -> etcpasswd  (safe!)
