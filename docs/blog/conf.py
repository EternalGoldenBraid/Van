project = "The Van Build"
extensions = ["myst_parser"]
myst_enable_extensions = ["linkify"]
myst_heading_anchors = 3
root_doc = "index"
exclude_patterns = ["_build", "**/README.md", "README.md", ".venv"]

html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["stove.css"]
html_title = project
html_copy_source = False
html_show_copyright = False
numfig = True
