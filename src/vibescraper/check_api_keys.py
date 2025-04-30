import os
import re
import sys

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.py")

def find_env_var(pattern, exclude=None):
    regex = re.compile(pattern)
    for key in os.environ:
        if regex.search(key):
            if exclude and exclude in key:
                continue
            return key
    return None

def main():
    # Find any env var containing BRAVE
    brave_key_name = find_env_var(r"BRAVE")
    # Find any env var containing GOOGLE but NOT CSE
    google_key_name = find_env_var(r"GOOGLE", exclude="CSE")
    # Find any env var containing both GOOGLE and CSE (order-independent)
    google_cse_name = None
    for key in os.environ:
        if "GOOGLE" in key and "CSE" in key:
            google_cse_name = key
            break

    # Decision logic
    if not brave_key_name and not google_key_name:
        print("ERROR: You must set at least one environment variable containing BRAVE or GOOGLE (not CSE) in its name.")
        sys.exit(1)

    if not brave_key_name and google_key_name and not google_cse_name:
        print(f"ERROR: Found GOOGLE API key ({google_key_name}) but no GOOGLE CSE ID (any variable containing both GOOGLE and CSE). Both are required for Google search.")
        sys.exit(1)

    if google_key_name and not google_cse_name:
        print(f"WARNING: Found GOOGLE API key ({google_key_name}) but no GOOGLE CSE ID. Google search will not work.")

    # Compose config.py lines
    config_lines = "\n# --- API key environment variable accessors appended by installer ---\n"
    config_lines += "import os\n"

    if brave_key_name:
        config_lines += f'{brave_key_name} = os.getenv("{brave_key_name}")\n'
    else:
        config_lines += '# BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")\n'

    if google_key_name:
        config_lines += f'GOOGLE_API_KEY = os.getenv("{google_key_name}")\n'
        if google_cse_name:
            config_lines += f'GOOGLE_CSE_ID = os.getenv("{google_cse_name}")\n'
        else:
            config_lines += '# GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")\n'
    else:
        config_lines += '# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")\n# GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")\n'

    # Append to config.py
    with open(CONFIG_FILE, "a", encoding="utf-8") as f:
        f.write(config_lines)
    print(f"API key accessors appended to {CONFIG_FILE}")

if __name__ == "__main__":
    main()

