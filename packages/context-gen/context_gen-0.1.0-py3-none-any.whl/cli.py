import os
import fnmatch
import pathlib
import pathspec


context_gen_ignore_file_name = ".ctxgenignore"
context_gen_include_file_name = ".ctxgeninclude"

def should_ignore(path, ignore_patterns, root_path):
    """
    Checks if a given path should be ignored based on ignore_patterns.
    Compares against the relative path from the root and the item name.
    """
    spec = pathspec.PathSpec.from_lines("gitwildmatch", ignore_patterns)
    relative_path = os.path.relpath(path, root_path)
    # Normalize path separators for consistent matching
    relative_path_unix = relative_path.replace(os.sep, '/')
    return spec.match_file(relative_path)
    # path_name = os.path.basename(path)

    # for pattern in ignore_patterns:
    #     # Match against the full relative path
    #     if fnmatch.fnmatch(relative_path_unix, pattern) or \
    #        fnmatch.fnmatch(relative_path_unix + '/', pattern) or \
    #        fnmatch.fnmatch(path_name, pattern) or pattern in relative_path_unix:
    #         return True
    # return False

def should_include(path, include_patterns, root_path):
    """
    Checks if a given path should be included based on include_patterns.
    If no include_patterns are provided, everything is considered for inclusion (subject to ignore).
    """
    if not include_patterns:
        return True  # No include patterns means include everything (that's not ignored)

    relative_path = os.path.relpath(path, root_path)
    # Normalize path separators for consistent matching
    relative_path_unix = relative_path.replace(os.sep, '/')
    path_name = os.path.basename(path)


    for pattern in include_patterns:
        # Check if the current path is or is within an included directory
        if fnmatch.fnmatch(relative_path_unix, pattern) or \
           fnmatch.fnmatch(path_name, pattern) or \
           relative_path_unix.startswith(pattern.rstrip('/') + '/'): # check if it's a subdirectory of an include pattern
            return True
        # Check if any parent directory of the current path matches an include pattern
        # This is to ensure files within included subdirectories are also captured
        # e.g., include_patterns = ["src/components"] should include "src/components/button/button.js"
        temp_path = pathlib.Path(relative_path_unix)
        for p_pattern in include_patterns:
            if temp_path.match(p_pattern) or str(temp_path).startswith(p_pattern.rstrip('/') + '/'):
                 return True
            for parent in temp_path.parents:
                if parent.match(p_pattern) or str(parent).startswith(p_pattern.rstrip('/') + '/'):
                    return True


    return False

def get_file_content(file_path):
    """Reads and returns the content of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def main():
    """
    Main function to traverse directory and write content to a Markdown file.
    """
    script_path = os.path.abspath(__file__)
    root_directory = os.getcwd()
    root_directory_name = os.path.basename(root_directory)
    output_filename = f"{root_directory_name}.ctx.md"
    ignore_file_path = os.path.join(root_directory, context_gen_ignore_file_name)
    include_file_path = os.path.join(root_directory, context_gen_include_file_name)
    script_name = os.path.basename(__file__)

    include_patterns = None

    ignore_patterns = [
        script_name,  # Ignore the script itself
        output_filename, # Ignore the output file
        ".git/",       # Common ignore
        ".DS_Store",   # Common ignore
        "__pycache__/", # Common ignore
        "*.pyc",       # Common ignore
        ".env",        # Common ignore
    ]
    if os.path.exists(ignore_file_path):
        with open(ignore_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    ignore_patterns.append(line)
        print(f"Loaded ignore patterns from: {ignore_file_path}")
    else:
        print(f"{context_gen_ignore_file_name} file not found at {ignore_file_path}. Using default ignore patterns.")

    if os.path.exists(include_file_path):
        with open(include_file_path, 'r', encoding='utf-8') as f:
            _include_patterns = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    _include_patterns.append(line)
            if len(_include_patterns) > 0:
                include_patterns = _include_patterns
        print(f"Loaded include patterns from: {include_file_path}")

    if include_patterns:
        print(f"Using include patterns: {include_patterns}")
    else:
        print("No specific include patterns provided. Processing all non-ignored items.")


    all_content = []

    for dirpath, dirnames, filenames in os.walk(root_directory, topdown=True):
        # --- Filter directories based on ignore and include patterns ---
        original_dirnames = list(dirnames) # Keep a copy for iteration

        # Apply ignore patterns to directories
        dirs_to_remove_due_to_ignore = []
        for dname in dirnames:
            current_dir_path = os.path.join(dirpath, dname)
            if should_ignore(current_dir_path, ignore_patterns, root_directory):
                dirs_to_remove_due_to_ignore.append(dname)

        for dname in dirs_to_remove_due_to_ignore:
            if dname in dirnames: # Check if still present before removing
                dirnames.remove(dname)


        # Apply include patterns to directories (if any are specified)
        # If include patterns exist, a directory must be explicitly included or be a parent/child of an included path
        if include_patterns:
            dirs_to_keep_due_to_include = []
            for dname in dirnames:
                current_dir_path = os.path.join(dirpath, dname)
                if should_include(current_dir_path, include_patterns, root_directory):
                    dirs_to_keep_due_to_include.append(dname)
            dirnames[:] = dirs_to_keep_due_to_include # Effectively filter dirnames

        # --- Process files ---
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            relative_file_path = os.path.relpath(file_path, root_directory)

            # Check if the file itself should be ignored
            if should_ignore(file_path, ignore_patterns, root_directory):
                print(f"Ignoring file: {relative_file_path}")
                continue

            # Check if the file is within an included path (if include_patterns are set)
            # This check is crucial because os.walk might yield files in directories
            # that are siblings of included directories but not themselves targeted for deep scan.
            if include_patterns and not should_include(file_path, include_patterns, root_directory):
                # print(f"Skipping file (not in include path): {relative_file_path}") # Can be verbose
                continue


            file_ext = os.path.splitext(filename)[1].lstrip('.')
            if not file_ext: # Handle files with no extension
                file_ext = "txt"

            print(f"Processing file: {relative_file_path}")
            content = get_file_content(file_path)

            if content is not None:
                formatted_content = f"#### {filename}\n"
                formatted_content += f"- *Path*: {relative_file_path.replace(os.sep, '/')}\n" # Use unix-style paths
                formatted_content += f"```{file_ext}\n"
                formatted_content += f"{content}\n"
                formatted_content += "```\n\n"
                all_content.append(formatted_content)

    output_file_abs_path = os.path.join(root_directory, output_filename)
    with open(output_file_abs_path, 'w', encoding='utf-8') as f:
        f.write("".join(all_content))

    print(f"\nSuccessfully generated '{output_filename}' in '{root_directory}'.")
    print(f"Total files processed: {len(all_content)}")

if __name__ == "__main__":
    main()