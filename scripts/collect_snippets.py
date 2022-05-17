import re
import shutil
import os

snippets_dir_path = ".snippets"
pre_snippets_dir_path = ".snippets_setup"

with open("README.md") as file:
    file_name: str
    for _, file_name, snippet in re.findall(r"(?s)((?<=```python)|(?<=``` python)) *(#? *\w*) *\n(.*?)(?=```)", file.read()):
        if file_name == '#noqa':
            continue
        if not file_name.startswith("#"):
            raise KeyError("snippet should have name: `#snippet_name`")

        file_name = file_name[1:].strip()

        if os.path.exists(f"{snippets_dir_path}/{file_name}.py"):
            raise FileExistsError(f"Snippet with name `{file_name}` already exist.")

        shutil.copyfile(f"{pre_snippets_dir_path}/{file_name}.py", f"{snippets_dir_path}/{file_name}.py")
        with open(f"{snippets_dir_path}/{file_name}.py", "a") as snippet_file:
            snippet_file.write(snippet)
