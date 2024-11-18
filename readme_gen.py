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

    items = []

    for item in os.listdir(directory):
        # Skip hidden files and directories
        if item.startswith("."):
            print(f"Skipping hidden item: {item}")
            continue

        item_path = os.path.join(directory, item)
        rel_item_path = os.path.relpath(item_path, root_dir)

        if os.path.isdir(item_path):
            # Folder representation
            folder_url = base_url + encode_url(rel_item_path)
            folder_icon_url = "https://cdn-icons-png.flaticon.com/512/148/148947.png"
            items.append(
                f"[![Folder Icon]({folder_icon_url}) **{item}**]({folder_url}/README.md)"
            )
            # Recursively generate README for the subfolder
            generate_readme(item_path)

        elif os.path.isfile(item_path) and item.lower().endswith(
            (".png", ".jpg", ".jpeg", ".gif", ".svg")
        ):
            # File representation with raw.githubusercontent.com link
            file_url = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/{GITHUB_REF_NAME}/{encode_url(rel_item_path)}"
            file_size = os.path.getsize(item_path) / 1024  # Size in KB
            size_str = (
                f"{file_size:.2f} KB"
                if file_size < 1024
                else f"{file_size / 1024:.2f} MB"
            )
            items.append(f"![{item}]({file_url})<br>**{item}**<br>{size_str}")

    # Create a Markdown table with 3 columns
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
