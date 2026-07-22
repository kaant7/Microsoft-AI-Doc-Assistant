import os
import re
import shutil
import subprocess
import tempfile

SOURCES = [
    {
        "repo": "https://github.com/MicrosoftDocs/azure-ai-docs.git",
        "sparse_path": "articles/foundry-local",
        "dest": os.path.join("docs", "foundry-local"),
    },
    {
        "repo": "https://github.com/MicrosoftLearning/mslearn-ai-studio.git",
        "sparse_path": "Instructions/Exercises",
        "dest": os.path.join("docs", "ai-studio"),
    },
    {
        "repo": "https://github.com/MicrosoftLearning/mslearn-ai-agents.git",
        "sparse_path": "Instructions/Exercises",
        "dest": os.path.join("docs", "ai-agents"),
    },
    {
        "repo": "https://github.com/MicrosoftLearning/mslearn-openai.git",
        "sparse_path": "Instructions/Labs",
        "dest": os.path.join("docs", "openai"),
    },
]

SKIP_DIR_NAMES = {"media"}
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
    return "includes" in (p.lower() for p in parts[:-1])


def fetch_source(repo, sparse_path, dest_dir):
    with tempfile.TemporaryDirectory() as tmp:
        print(f"System: Fetching '{sparse_path}' from {repo}...")
        subprocess.run(
            ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", repo, tmp],
            check=True,
        )
        subprocess.run(["git", "sparse-checkout", "set", sparse_path], cwd=tmp, check=True)

        src_root = os.path.join(tmp, sparse_path)
        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)

        copied = 0
        for root, dirs, files in os.walk(src_root):
            dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIR_NAMES]
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

                dest_path = os.path.join(dest_dir, rel_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                with open(dest_path, "w", encoding="utf-8") as f:
                    f.write(content)
                copied += 1

        print(f"Done: copied {copied} markdown files into '{dest_dir}'.")
        return copied


def fetch():
    total = 0
    for source in SOURCES:
        total += fetch_source(source["repo"], source["sparse_path"], source["dest"])
    print(f"\nAll sources fetched: {total} markdown files total.")


if __name__ == "__main__":
    fetch()
