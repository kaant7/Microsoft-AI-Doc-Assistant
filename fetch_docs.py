import os
import re
import shutil
import subprocess
import tempfile

REPO_URL = "https://github.com/MicrosoftDocs/azure-ai-docs.git"
SPARSE_PATH = "articles/foundry-local"
DEST_DIR = os.path.join("docs", "foundry-local")
SKIP_DIRS = {"media"}
SKIP_FILES = {"toc.yml", "index.yml"}

FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)
INCLUDE_RE = re.compile(r"\[!INCLUDE\s*\[[^\]]*\]\(([^)]+)\)\]")


def strip_frontmatter(text):
    return FRONTMATTER_RE.sub("", text, count=1)


def resolve_includes(text, base_dir, visited):
    def replace(match):
        inc_path = os.path.normpath(os.path.join(base_dir, match.group(1)))
        if inc_path in visited or not os.path.exists(inc_path):
            return ""
        visited.add(inc_path)
        with open(inc_path, "r", encoding="utf-8") as f:
            inc_text = strip_frontmatter(f.read())
        return resolve_includes(inc_text, os.path.dirname(inc_path), visited)

    return INCLUDE_RE.sub(replace, text)


def is_include_fragment(rel_path):
    parts = rel_path.split(os.sep)
    return "includes" in parts[:-1]


def fetch():
    with tempfile.TemporaryDirectory() as tmp:
        print(f"System: Fetching '{SPARSE_PATH}' from {REPO_URL}...")
        subprocess.run(
            ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", REPO_URL, tmp],
            check=True,
        )
        subprocess.run(["git", "sparse-checkout", "set", SPARSE_PATH], cwd=tmp, check=True)

        src_root = os.path.join(tmp, SPARSE_PATH)
        if os.path.exists(DEST_DIR):
            shutil.rmtree(DEST_DIR)

        copied = 0
        for root, dirs, files in os.walk(src_root):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for filename in files:
                if not filename.lower().endswith(".md") or filename in SKIP_FILES:
                    continue
                src_path = os.path.join(root, filename)
                rel_path = os.path.relpath(src_path, src_root)
                # Files under includes/ aren't standalone articles — they're
                # fragments embedded into other articles via [!INCLUDE], so skip them.
                if is_include_fragment(rel_path):
                    continue

                with open(src_path, "r", encoding="utf-8") as f:
                    content = f.read()
                content = strip_frontmatter(content)
                content = resolve_includes(content, root, {src_path})

                dest_path = os.path.join(DEST_DIR, rel_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                with open(dest_path, "w", encoding="utf-8") as f:
                    f.write(content)
                copied += 1

        print(f"Done: copied {copied} markdown files into '{DEST_DIR}'.")


if __name__ == "__main__":
    fetch()
