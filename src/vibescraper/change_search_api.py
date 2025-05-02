import os
import sys
import re

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.py")

def main():
    if len(sys.argv) > 1:
        search_engine = sys.argv[1]
        
        # Read the current config file content
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            # If file doesn't exist, start with empty content
            content = ""
        
        # Regex pattern to find the search_engine line
        pattern = r"search_engine = ['\"](.*?)['\"]"
        
        # Replace or append the search_engine line
        if re.search(pattern, content):
            # Update existing configuration
            updated_content = re.sub(pattern, f"search_engine = '{search_engine}'", content)
        else:
            # Append new configuration
            updated_content = content + f"search_engine = '{search_engine}'\n"
        
        # Write the updated content back to the config file
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        print(f"Search API changed to {search_engine}")
    else:
        print('You must declare your search engine as a command flag: eg: `change_search_api google`')

if __name__ == "__main__":
    main()

