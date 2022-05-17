import re
import shutil

snippets_dir_path = ".snippets"
pre_snippets_dir_path="scripts/pre_snippets"

snippet_number = 1
with open("README.md") as file:
    for file_name, snippet in re.findall(r"(?s)(?<=```python #)(\w*)\n(.*?)(?=```)", file.read()):
        shutil.copyfile(f"{pre_snippets_dir_path}/{file_name}.py", f"{snippets_dir_path}/snippet{snippet_number}.py")
        with open(f"{snippets_dir_path}/snippet{snippet_number}.py", "a") as snippet_file:
            snippet_file.write(snippet)

        snippet_number += 1
