import os

# Root directory containing the images
root_dir = os.getcwd()
# Output file (README.md)
output_file = "README.md"

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

print(f"Current working directory: {os.getcwd()}")
print(f"Root directory: {root_dir}")

# Folder icon URL (replace with a preferred folder image URL)
folder_icon_url = "https://cdn-icons-png.flaticon.com/512/148/148947.png"


def generate_readme(directory):
    # Get relative path for the current directory
    rel_path = os.path.relpath(directory, root_dir)
    readme_path = os.path.join(directory, "README.md")
    grid_template = """
<style>
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
  justify-items: center;
}
.grid-item {
  text-align: center;
  font-size: 14px;
}
.grid-item img {
  max-width: 100%;
  height: auto;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 4px;
}
.folder-item img {
  width: 50px;
  height: auto;
  margin-bottom: 8px;
}
</style>

<div class="grid-container">
"""

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
            folder_url = base_url + rel_item_path.replace("\\", "/")
            items.append(
                f"""
  <div class="grid-item folder-item">
    <a href="{folder_url}/README.md" target="_blank">
      <img src="{folder_icon_url}" alt="Folder Icon">
      <p>{item}</p>
    </a>
  </div>
"""
            )
            # Recursively generate README for the subfolder
            generate_readme(item_path)

        elif os.path.isfile(item_path) and item.lower().endswith(
            (".png", ".jpg", ".jpeg", ".gif", ".svg")
        ):
            # File representation with raw.githubusercontent.com link
            file_url = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/{GITHUB_REF_NAME}/{rel_item_path.replace('\\', '/')}"
            file_size = os.path.getsize(item_path) / 1024  # Size in KB
            size_str = (
                f"{file_size:.2f} KB"
                if file_size < 1024
                else f"{file_size / 1024:.2f} MB"
            )
            items.append(
                f"""
  <div class="grid-item">
    <a href="{file_url}" target="_blank">
      <img src="{file_url}" alt="{item}">
    </a>
    <p>{item} <br> {size_str}</p>
  </div>
"""
            )

    grid_template += "\n".join(items)
    grid_template += "\n</div>"

    # Write the README file
    with open(readme_path, "w") as f:
        f.write(f"# {os.path.basename(directory)}\n\n")
        f.write(grid_template)

    print(f"Generated README.md for {directory}")


# Start generating READMEs from the root directory
generate_readme(root_dir)
