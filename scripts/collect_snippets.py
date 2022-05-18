import re
from pathlib import Path

snippets_dir_path = ".snippets"
snippets_setup_dir_path = ".snippets_setup"

with open("README.md") as file:
    file_name: str
    for _, file_name, snippet in re.findall(r"(?s)(?:(?<=```python)|(?<=``` python)) *(#(\w*))?\n(.*?)(?=```)", file.read()):
        if file_name == 'noqa':
            continue

        if not file_name:
            raise KeyError("snippet should have name: `#snippet_name`")

        snippet_path = Path(f"{snippets_dir_path}/{file_name}.py")
        snippet_setup_path = Path(f"{snippets_setup_dir_path}/{file_name}.py")

        if snippet_path.exists():
            raise FileExistsError(f"Snippet with name `{file_name}` already exist.")

        snippet_path.write_text(snippet_setup_path.read_text() + snippet)
