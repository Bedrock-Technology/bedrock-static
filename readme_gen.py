import os
import urllib.parse

# Root directory containing the images
root_dir = os.getcwd()

# GitHub repository and branch information
GITHUB_REPOSITORY = (
    os.getenv("GITHUB_REPOSITORY")
    if os.getenv("GITHUB_REPOSITORY")
    else "Bedrock-Technology/bedrock-static"
)
GITHUB_REF_NAME = (
    os.getenv("GITHUB_REF_NAME") if os.getenv("GITHUB_REF_NAME") else "main"
)

# Base URL for GitHub repository content
base_url = f"https://github.com/{GITHUB_REPOSITORY}/blob/{GITHUB_REF_NAME}/"


# Encode URLs to handle special characters like spaces
def encode_url(path):
    return urllib.parse.quote(path.replace("\\", "/"), safe="/")


def generate_readme(directory):
    # Get relative path for the current directory
    rel_path = os.path.relpath(directory, root_dir)
    readme_path = os.path.join(directory, "README.md")

    # Start with a Markdown heading
    md_content = f"# {os.path.basename(directory)}\n\n"

    # Separate and sort folders and files (case-insensitive)
    folders = sorted(
        [
            item
            for item in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, item)) and not item.startswith(".")
        ],
        key=str.lower,  # Sort ignoring case
    )
    files = sorted(
        [
            item
            for item in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, item))
            and not item.startswith(".")
            and item.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg"))
        ],
        key=str.lower,  # Sort ignoring case
    )

    # Add folders to the Markdown content
    for folder in folders:
        folder_path = os.path.join(directory, folder)
        folder_rel_path = os.path.relpath(folder_path, root_dir)
        folder_url = base_url + encode_url(folder_rel_path)
        folder_icon_url = "https://cdn-icons-png.flaticon.com/512/148/148947.png"
        md_content += f'[<img src="{folder_icon_url}" alt="Folder Icon" style="max-width: 180; max-height: 180;">]({folder_url}/README.md)<br>**{folder}**\n\n'
        # md_content += f"[![Folder Icon]({folder_icon_url}) **{folder}**]({folder_url}/README.md)\n\n"
        # Recursively generate README for the subfolder
        generate_readme(folder_path)

    # Add files to the Markdown content
    items = []
    for file in files:
        file_path = os.path.join(directory, file)
        file_rel_path = os.path.relpath(file_path, root_dir)
        file_url = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/{GITHUB_REF_NAME}/{encode_url(file_rel_path)}"
        file_size = os.path.getsize(file_path) / 1024  # Size in KB
        size_str = (
            f"{file_size:.2f} KB" if file_size < 1024 else f"{file_size / 1024:.2f} MB"
        )
        items.append(
            f'[<img src="{file_url}" alt="{file}" style="max-width: 180; max-height: 180;">]({file_url})<br>**{file}**<br>{size_str}'
        )
        # items.append(f"![{file}]({file_url})<br>**{file}**<br>{size_str}")

    # Add files to the Markdown table
    if items:
        md_content += create_table(items, columns=4)

    # Write the README file
    with open(readme_path, "w") as f:
        f.write(md_content)

    print(f"Generated README.md for {directory}")


def create_table(items, columns=3):
    """Creates a Markdown table with a specified number of columns."""
    table = "| " + " | ".join([" "] * columns) + " |\n"
    table += "| " + " | ".join(["---"] * columns) + " |\n"

    for i in range(0, len(items), columns):
        row = items[i : i + columns]
        table += "| " + " | ".join(row + [" "] * (columns - len(row))) + " |\n"

    return table


# Start generating READMEs from the root directory
generate_readme(root_dir)
