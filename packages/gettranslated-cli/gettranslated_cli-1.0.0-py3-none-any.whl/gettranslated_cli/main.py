import argparse
import fnmatch
import json
import os
import sys
from argparse import ArgumentParser

try:
    import requests
except ImportError:
    print("Error: The 'requests' library is required but not installed.")
    print()
    print("Please install it by running:")
    print("  pip install requests")
    print()
    print("Or install the package with dependencies:")
    print("  pip install gettranslated-cli")
    print()
    sys.exit(1)

SERVER = "https://www.gettranslated.ai"
DEBUG = False
ENV_KEY = "GETTRANSLATED_KEY"

# Common directories to exclude from language file detection
EXCLUDED_DIRS = {
    'node_modules', '.git', '.svn', '.hg', '.bzr',
    'build', 'dist', 'out', 'target',
    '.next', '.nuxt', '.vuepress',
    'coverage', '.nyc_output',
    '.vscode', '.idea',
    'tmp', 'temp', '.tmp', '.temp',
    '.DS_Store', 'Thumbs.db',
    'vendor', 'bower_components',
    '.cache', '.parcel-cache',
}

# Fallback supported language codes (used if server request fails)
# This list should match base/lang.py LANGUAGES dictionary
_FALLBACK_LANGUAGE_CODES = {
    "am", "ar", "bg", "bn", "bs", "ca", "cs", "da", "de", "el", "en", "es",
    "et", "fa", "fi", "fr", "gu", "hi", "hr", "hu", "hy", "id", "is", "it",
    "ja", "jv", "ka", "kk", "kn", "ko", "lt", "lv", "mk", "ml", "mn", "mr",
    "ms", "my", "nl", "no", "pa", "pir", "pl", "pt", "ro", "ru", "sk", "sl",
    "so", "sq", "sr", "sv", "sw", "ta", "te", "th", "tl", "tr", "uk", "ur",
    "vi", "zh-Hans", "zh-Hant",
}

# Cache for fetched language codes
_SUPPORTED_LANGUAGE_CODES_CACHE = None


def upload_file(file_path, root_dir, token, force=False, language=None, is_base_language=False):
    # Determine the language to use
    if language is None:
        language = "en"

    # Use os.path.relpath to get the relative path, which handles . correctly
    path = os.path.relpath(file_path, root_dir).replace("\\", "/")
    if path.startswith("/"):
        path = path[1:]
    upload_url = f"{SERVER}/sync/file/{language}/{path}"

    # Create a dictionary with the file key and the file to be uploaded
    # Use context manager to ensure file is closed
    with open(file_path, "rb") as f:
        files = {"file": ("filename", f)}
        
        # Send a POST request to the server
        headers = {"Authorization": f"Bearer {token}"}
        data = {"force": "true"} if force else {}
        response = requests.post(upload_url, files=files, headers=headers, data=data)

    # Check the response
    if response.status_code == 200:
        response_data = response.json()
        debug(json.dumps(response_data, indent=4))
        
        # Display warning message if present
        if "warning" in response_data:
            print(f"⚠️  {response_data['warning']}")
        return response_data
    else:
        error_msg = f"Upload request failed with status code {response.status_code}"
        print(f"{error_msg}")
        print(f"URL: {upload_url}")
        if response.text:
            print(f"Response: {response.text}")
        # For base language uploads, we want to exit on error
        if is_base_language:
            sys.exit(1)
        else:
            # For translation uploads, raise an exception that can be caught so we can continue
            raise RuntimeError(error_msg)


def find_files(directory, file_list, language=None):
    # If language is specified, find files for that language; otherwise use base language
    target_language = language if language else file_list["base_language"]
    
    if file_list["platform"] == "Android":
        # check for Android strings.xml files
        values_dir = "values" if target_language == "en" else f"values-{target_language}"
        return find_files_helper(directory, "strings.xml", values_dir)

    elif file_list["platform"] == "iOS":
        # check for iOS strings files
        return find_files_helper(
            directory, "*.strings", f"{target_language}.lproj"
        )
    elif file_list["platform"] == "React Native":
        # check for React Native JSON files in common locations
        # Priority order: locales/, src/locales/, assets/locales/, translations/, i18n/, root
        common_dirs = ["locales", "src/locales", "assets/locales", "translations", "i18n", ""]
        
        for dir_path in common_dirs:
            results = find_files_helper(
                directory, f"{target_language}.json", dir_path
            )
            if results:
                return results
        
        return []
    else:
        print("Unknown platform")
        sys.exit(1)


def _process_directory_item(item_path, item, excluded_dirs, callback, search_recursive, depth, max_depth):
    """Process a single directory item (file or subdirectory)."""
    # Skip excluded directories
    if os.path.isdir(item_path) and item in excluded_dirs:
        return
    
    # Try callback first (might match a file)
    if os.path.isfile(item_path):
        callback(item_path, item)
    
    # Recurse into subdirectories
    if os.path.isdir(item_path):
        search_recursive(item_path, callback, depth + 1, max_depth)


def _search_recursive_for_languages(directory, excluded_dirs=None):
    """
    Shared recursive search function for all platforms.
    Returns a function that searches recursively for language files.
    """
    if excluded_dirs is None:
        excluded_dirs = EXCLUDED_DIRS.copy()
    
    def search_recursive(search_dir, callback, depth=0, max_depth=5):
        """
        Recursively search directory and call callback for each file.
        callback(file_path, item_name) should return True if file matches and was processed.
        """
        if depth > max_depth:
            return
        
        try:
            if not os.path.isdir(search_dir):
                return
                
            for item in os.listdir(search_dir):
                item_path = os.path.join(search_dir, item)
                _process_directory_item(item_path, item, excluded_dirs, callback, search_recursive, depth, max_depth)
        except PermissionError:
            # Skip directories we can't read
            pass
    
    return search_recursive


def _detect_android_languages(directory):
    """Detect Android language files by recursively scanning for values-* directories"""
    detected_languages = {}
    
    excluded_dirs = EXCLUDED_DIRS.copy()
    excluded_dirs.update({'android', 'ios'})
    
    search_recursive = _search_recursive_for_languages(directory, excluded_dirs)
    supported_codes = get_supported_languages()
    
    def handle_file(file_path, item_name):
        # Look for values directories containing strings.xml
        parent_dir = os.path.basename(os.path.dirname(file_path))
        if parent_dir.startswith("values") and item_name == "strings.xml":
            lang_code = parent_dir.replace("values", "").replace("-", "") if parent_dir != "values" else "en"
            # Only consider supported language codes
            if lang_code in supported_codes:
                if lang_code not in detected_languages:
                    detected_languages[lang_code] = []
                detected_languages[lang_code].append(file_path)
                return True
        return False
    
    search_recursive(directory, handle_file)
    return detected_languages


def _detect_ios_languages(directory):
    """Detect iOS language files by recursively scanning for .lproj directories"""
    detected_languages = {}
    
    excluded_dirs = EXCLUDED_DIRS.copy()
    excluded_dirs.update({'android', 'ios'})
    
    search_recursive = _search_recursive_for_languages(directory, excluded_dirs)
    supported_codes = get_supported_languages()
    
    def handle_file(file_path, item_name):
        # Look for .lproj directories containing Localizable.strings
        parent_dir = os.path.basename(os.path.dirname(file_path))
        if parent_dir.endswith(".lproj") and item_name == "Localizable.strings":
            lang_code = parent_dir.replace(".lproj", "")
            # Only consider supported language codes
            if lang_code in supported_codes:
                if lang_code not in detected_languages:
                    detected_languages[lang_code] = []
                detected_languages[lang_code].append(file_path)
                return True
        return False
    
    search_recursive(directory, handle_file)
    return detected_languages


def _detect_react_native_languages(directory):
    """Detect React Native language files by recursively scanning for JSON files"""
    detected_languages = {}
    
    excluded_dirs = EXCLUDED_DIRS.copy()
    excluded_dirs.update({'android', 'ios'})
    
    search_recursive = _search_recursive_for_languages(directory, excluded_dirs)
    supported_codes = get_supported_languages()

    def handle_file(file_path, item_name):
        # Look for language JSON files (format: lang.json)
        if item_name.endswith(".json"):
            lang_code = item_name.replace(".json", "")
            if lang_code in supported_codes:
                if lang_code not in detected_languages:
                    detected_languages[lang_code] = []
                detected_languages[lang_code].append(file_path)
                return True
        return False
    
    search_recursive(directory, handle_file)
    return detected_languages


def detect_all_languages_in_project(directory, file_list):
    """Detect all language files present in the project directory"""
    platform = file_list["platform"]
    
    if platform == "Android":
        return _detect_android_languages(directory)
    elif platform == "iOS":
        return _detect_ios_languages(directory)
    elif platform == "React Native":
        return _detect_react_native_languages(directory)
    
    return {}


def find_translation_files(directory, file_list):
    """Find translation files for all configured languages (excluding base language)"""
    translation_files = {}
    
    # Get all configured languages
    all_languages = file_list.get("languages", [])
    
    for language in all_languages:
        files = find_files(directory, file_list, language)
        if files:
            translation_files[language] = files
    
    return translation_files


def find_files_helper(directory, filename_pattern, filedir, results=None, root_dir=None):
    """
    Recursively search for files matching the given filename in the specified directory.

    Args:
        directory (str): The directory to start the search from.
        filename (str): The filename to search for.
        filedir (str): The immediate file directory to match.
        results (list, optional): A list to store the matching file paths. Defaults to None.
        root_dir (str, optional): The root directory for the search. Used for empty filedir searches.

    Returns:
        list: A list of file paths matching the given filename.
    """
    if results is None:
        results = []
    if root_dir is None:
        root_dir = directory

    # Directories to exclude from search
    excluded_dirs = {
        'node_modules', '.git', '.svn', '.hg', '.bzr',  # Version control
        'build', 'dist', 'out', 'target',  # Build outputs
        '.next', '.nuxt', '.vuepress',  # Framework builds
        'coverage', '.nyc_output',  # Test coverage
        '.vscode', '.idea',  # IDE files
        'tmp', 'temp', '.tmp', '.temp',  # Temporary files
        '.DS_Store', 'Thumbs.db',  # OS files
        'vendor', 'bower_components',  # Package managers
        '.cache', '.parcel-cache',  # Caches
        'android', 'ios',  # Platform-specific directories (for RN)
    }

    # Iterate over all items in the directory
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)

        # Skip excluded directories
        if os.path.isdir(item_path) and item in excluded_dirs:
            continue

        # If item is a directory, recursively search within it
        if os.path.isdir(item_path):
            find_files_helper(item_path, filename_pattern, filedir, results, root_dir)
        # If item is a file and matches the filename, add it to results
        elif (
            os.path.isfile(item_path)
            and fnmatch.fnmatch(item, filename_pattern)
            and (
                (filedir == "" and directory == root_dir) or  # Root search - only files in root directory
                (filedir != "" and directory.endswith(filedir))  # Specific directory search
            )
        ):
            results.append(item_path)

    return results


def translate(token, first_call=True):
    url = f"{SERVER}/sync/translate"

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, headers=headers)

    # Check the response
    if response.status_code == 200:
        debug(json.dumps(response.json(), indent=4))
        data = response.json()

        if (
            first_call
            and data["translated"] == 0
            and not data["continue"]
            and not data["error"]
        ):
            print("Nothing to translate")
            return

        print(f"Translating {data['language']}... {data['percent_done']}")
        if data["continue"]:
            translate(token, first_call=False)
        elif data["error"]:
            print(
                "LLM error translating strings. Please try again, or contact support if this persists."
            )
            sys.exit(1)

    else:
        print(f"Translate request failed with status code {response.status_code}")
        print(f"URL: {url}")
        if response.text:
            print(f"Response: {response.text}")
        sys.exit(1)


def grammar_check(token):
    url = f"{SERVER}/sync/grammar/check"

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, headers=headers)

    # Check the response
    if response.status_code == 200:
        debug(json.dumps(response.json(), indent=4))
        data = response.json()
        print(f"Checked {data['checked']} string... {data['percent_done']}")

        if data["continue"]:
            grammar_check(token)
        if data["error"]:
            print(
                "Error running grammar check. Please try again, or contact support if this persists."
            )
            sys.exit(1)

    else:
        print(f"Grammar check request failed with status code {response.status_code}")
        print(f"URL: {url}")
        if response.text:
            print(f"Response: {response.text}")
        sys.exit(1)


def get_token(args, working_dir):
    """Get API token from various sources in order of precedence."""
    # First, check if the key was specified as a command line argument
    if args.key is not None:
        debug(f"Using key from command line: {args.key}")
        return args.key

    # Next, check if the key is set as an environment variable
    if os.environ.get(ENV_KEY) is not None:
        debug(f"Using key from environment variable: {os.environ.get(ENV_KEY)}")
        return os.environ.get(ENV_KEY)

    # Check for .gettranslated file in project directory (hidden, less likely to be committed)
    project_config = os.path.join(working_dir, ".gettranslated")
    if os.path.exists(project_config):
        debug(f"Using key from .gettranslated file: {project_config}")
        with open(project_config, "r") as file:
            return file.read().strip()

    return None


def debug(str):
    if DEBUG:
        print(str)


def get_supported_languages():
    """
    Fetch supported language codes from the server.
    Falls back to hardcoded list if the request fails.
    Returns a set of language codes.
    """
    global _SUPPORTED_LANGUAGE_CODES_CACHE
    
    # Return cached value if available
    if _SUPPORTED_LANGUAGE_CODES_CACHE is not None:
        return _SUPPORTED_LANGUAGE_CODES_CACHE
    
    # Try to fetch from server
    url = f"{SERVER}/sync/languages"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "languages" in data and isinstance(data["languages"], list):
                _SUPPORTED_LANGUAGE_CODES_CACHE = set(data["languages"])
                debug(f"Fetched {len(_SUPPORTED_LANGUAGE_CODES_CACHE)} supported languages from server")
                return _SUPPORTED_LANGUAGE_CODES_CACHE
    except Exception as e:
        debug(f"Failed to fetch supported languages from server: {e}")
        debug("Using fallback language codes")
    
    # Fallback to hardcoded list
    _SUPPORTED_LANGUAGE_CODES_CACHE = _FALLBACK_LANGUAGE_CODES
    return _SUPPORTED_LANGUAGE_CODES_CACHE


def get_file_list(token):
    url = f"{SERVER}/sync/file/list"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)

    # Check the response
    if response.status_code == 200:
        debug(json.dumps(response.json(), indent=4))
        return response.json()
    else:
        print(f"File list request failed with status code {response.status_code}")
        print(f"URL: {url}")
        if response.text:
            print(f"Response: {response.text}")
        sys.exit(1)


def sync(dir, fileset, token):
    url = f"{SERVER}/sync/{fileset['uri']}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)

    # Check the response status code and stop if not 200
    if response.status_code != 200:
        print(f"Sync request failed with status code {response.status_code}")
        print(f"URL: {url}")
        if response.text:
            print(f"Response: {response.text}")
        sys.exit(1)

    content = response.content.decode("utf-8")

    output_file = os.path.join(dir, fileset["local_path"])
    print(f"Syncing {output_file}...")

    directory = os.path.dirname(output_file)
    if not os.path.exists(directory):
        debug(f"Creating directory {directory}")
        os.makedirs(directory)

    with open(output_file, "w") as f:
        f.write(content)


class CustomHelpFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
        # Override the _split_lines method to handle newlines
        lines = []
        for line in text.splitlines():
            lines.extend(argparse.HelpFormatter._split_lines(self, line, width))
        return lines


def handle_first_sync_warnings(working_dir, file_list):
    """Handle warnings and language detection on first sync."""
    detected_languages = detect_all_languages_in_project(working_dir, file_list)
    base_language = file_list["base_language"]
    
    if len(detected_languages) > 1:
        print()
        print("Detected multiple language files in your project:")
        for lang, files in detected_languages.items():
            print(f"  - {lang}: {len(files)} file(s)")
        
        if base_language not in detected_languages:
            print()
            print(f"⚠️  Warning: Base language configured as '{base_language}' but no files found for that language!")
            print("   You may need to change the base language in project settings.")
            print()
            response = input("Continue anyway? (y/n): ").strip().lower()
            if response not in ['y', 'yes']:
                print("Upload cancelled.")
                sys.exit(0)
        print()


def _print_translation_files(translation_files):
    """Print list of found translation files."""
    print()
    print("Found existing translation files in your project:")
    for language, files in translation_files.items():
        for file_path in files:
            print(f"  - {file_path}")


def _upload_translation_files(translation_files, working_dir, token, force):
    """Upload translation files to the server."""
    print("Uploading translation files...")
    for language, files in translation_files.items():
        for file_path in files:
            try:
                print(f"Uploading {file_path} as {language}...")
                upload_file(file_path, working_dir, token, force, language)
            except RuntimeError:
                print(f"Failed to upload {file_path}")
                # Continue with next file


def handle_upload_translations(working_dir, file_list, token, force):
    """Offer to upload existing translation files on first sync."""
    all_detected_languages = detect_all_languages_in_project(working_dir, file_list)
    base_language = file_list["base_language"]
    
    # Filter out the base language - those are translation files
    translation_files = {lang: files for lang, files in all_detected_languages.items() 
                       if lang != base_language}
    
    if not translation_files:
        return
    
    _print_translation_files(translation_files)
    print()
    response = input("Would you like to upload these translations? (y/n): ").strip().lower()
    
    if response in ['y', 'yes']:
        _upload_translation_files(translation_files, working_dir, token, force)
    else:
        print("Skipping translation file upload.")


def run_upload_mode(working_dir, file_list, token, force, is_first_sync):
    """Handle upload mode operations."""
    if is_first_sync:
        handle_first_sync_warnings(working_dir, file_list)
    
    print("Beginning upload...")
    matching_files = find_files(working_dir, file_list)

    if len(matching_files) == 0:
        print(
            f"❌ No {file_list['platform']} files found to upload. Have you specified the correct directory?"
        )
        sys.exit(1)

    for file_path in matching_files:
        print(f"Syncing {file_path}...")
        upload_file(file_path, working_dir, token, force, is_base_language=True)

    if is_first_sync:
        handle_upload_translations(working_dir, file_list, token, force)


def run_download_mode(working_dir, file_list, token):
    """Handle download mode operations."""
    print("Beginning download...")
    for fileset in file_list["files"]:
        sync(working_dir, fileset, token)


def run_translate_mode(token):
    """Handle translate mode operations."""
    print("Beginning translation...")
    translate(token)


def main():
    """
    Modes for running this script:
    * upload: Syncs project strings with your project
    * download: Downloads translated string resources to your project
    * translate: Translates any new or untranslated strings in your project
    * sync: Runs upload / translate / download in sequence
    * grammar: Runs a grammar check on your project strings

    Server keys can be specified in a few different ways, in order of precedence:
    1. As a command line argument with -k or --key
    2. As an environment variable named GETTRANSLATED_KEY
    3. In a .gettranslated file in your project directory

    Server URL can be specified with -s or --server (default: https://www.gettranslated.ai)
    """

    # command line parsing
    parser = ArgumentParser(
        formatter_class=CustomHelpFormatter,
        description="GetTranslated CLI - Sync translation files with GetTranslated.ai"
    )
    parser.add_argument(
        "mode",
        choices=["upload", "download", "translate", "sync", "grammar"],
        help="Script mode:\n"
        "* upload (syncs project strings with your project)\n"
        "* download (syncs translated string resources to your project)\n"
        "* translate (translates any new or untranslated strings in your project)\n"
        "* sync (runs upload / translate / download in sequence)\n"
        "* grammar (runs a grammar check on your project strings)",
    )
    parser.add_argument(
        "working_directory",
        nargs='?',
        default='.',
        help="Your main project directory (default: current directory)"
    )
    parser.add_argument(
        "-k", "--key", help="Server key, if not specified by config file or environment variable"
    )
    parser.add_argument(
        "-v", "--verbose", help="Verbose output mode", action="store_true"
    )
    parser.add_argument(
        "-f", "--force", help="Force processing even if file hash matches last processed file", action="store_true"
    )
    parser.add_argument(
        "-s", "--server", help="Server URL (default: https://www.gettranslated.ai)", default="https://www.gettranslated.ai"
    )
    args = parser.parse_args()

    # Normalize server URL (remove trailing slash if present)
    global SERVER, DEBUG
    SERVER = args.server.rstrip('/')
    DEBUG = args.verbose

    working_dir = os.path.abspath(args.working_directory)
    if not os.path.exists(working_dir):
        print(f"❌ Directory {working_dir} does not exist")
        sys.exit(1)

    token = get_token(args, working_dir)
    if token is None:
        print("❌ No API key found.")
        print()
        print("Quick setup options:")
        print("  1. Run with -k flag: translate sync -k YOUR_KEY")
        print("  2. Set environment: export GETTRANSLATED_KEY=YOUR_KEY")
        print("  3. Create config file: echo 'YOUR_KEY' > .gettranslated")
        print()
        print("Get your API key: https://www.gettranslated.ai/settings/api")
        sys.exit(1)

    file_list = get_file_list(token)
    print(f"Connected to project {file_list['name']}")

    is_first_sync = file_list.get("is_first_sync", False)

    if args.mode in ("upload", "sync"):
        run_upload_mode(working_dir, file_list, token, args.force, is_first_sync)

    if args.mode in ("translate", "sync"):
        run_translate_mode(token)

    if args.mode in ("download", "sync"):
        if args.mode == "sync":
            # Our file list may have changed
            file_list = get_file_list(token)
        run_download_mode(working_dir, file_list, token)

    if args.mode == "grammar":
        print("Beginning grammar check...")
        grammar_check(token)

    print("✅ Done!")


if __name__ == "__main__":
    main()

