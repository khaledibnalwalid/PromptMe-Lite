import os
from boxsdk import OAuth2, Client, JWTAuth
import chardet

config_path = os.path.abspath('challenges/LLM06_Excessive_Agency/app/utils/llm06_2025_utils/box_config.json')
if not os.path.exists(config_path):
    raise FileNotFoundError(f"Config file not found at {config_path}")

print(f"Config path (absolute): {config_path}")
print("Config file exists:", os.path.exists(config_path))
print("Current Working Directory:", os.getcwd())

config = JWTAuth.from_settings_file(config_path)
client = Client(config)

WHOLE_BOX_FOLDER_ID = os.getenv('WHOLE_BOX_FOLDER_ID')

def search_file_recursive(folder_id, file_name):
    found_file = False
    file_id = ""
    file_content = "File not found in the accessible folder."
    if folder_id == None:
        folder_id = WHOLE_BOX_FOLDER_ID

    folder = client.folder(folder_id)
    # Get items in the folder
    items = folder.get_items()

    for item in items:
        if item.type == "file" and item.name.lower() == file_name.lower():
            # print(f"✅ File found: {item.name} (ID: {item.id}) in {folder.name}")
            found_file = True
            file_id = item.id
            file_content = client.file(item.id).content()
            result = chardet.detect(file_content[:1000])  # check first 10 KB
            encoding = result['encoding']
            if encoding == None:
                encoding = 'utf-8'
            return found_file, file_id, file_content.decode(encoding)
        elif item.type == "folder":
            # Recursively search in subfolder
            found_file, file_id, file_content = search_file_recursive(item.id, file_name)
            if found_file:
                return found_file, file_id, file_content  # Return immediately if found
    
    return found_file, file_id, file_content

def list_all_files(folder_id):
    folder_content = {}
    if folder_id == None:
        return folder_content
    else:
        if folder_id != WHOLE_BOX_FOLDER_ID:
            root_folder = client.folder(WHOLE_BOX_FOLDER_ID)
            # Get folder information
            root_folder_info = root_folder.get()

            # Access the folder name
            root_folder_name = root_folder_info.name
            folder_content[root_folder_name] = []
            
        folder = client.folder(folder_id)
        # Get folder information
        folder_info = folder.get()

        # Access the folder name
        folder_name = folder_info.name

        folder_content[folder_name] = []
        # Get items in the folder
        items = folder.get_items()
        for item in items:
            if item.type == "file":
                folder_content[folder_name].append(item.name)
            elif item.type == "folder":
                # Recursively search in subfolder
                nested_folder_content = list_all_files(item.id)
                folder_content[folder_name+"/"+item.name] = nested_folder_content[item.name]

        return folder_content

def create_file(folder_id, filename, content):
    """Create a new file in the Box CTF folder."""
    try:
        file_path = f"/tmp/{filename}"  # Temporary file for upload
        with open(file_path, "w") as f:
            f.write(content)

        folder = client.folder(folder_id)
        uploaded_file = folder.upload(file_path, file_name=filename)
        os.remove(file_path)  # Cleanup temp file
        return f"✅ File '{filename}' created successfully (ID: {uploaded_file.id})"
    except Exception as e:
        return f"❌ Error creating file: {e}"


def update_file(folder_id, file_name, new_content):
    """Update an existing file in the Box CTF folder."""
    found_file, file_id, file_content = search_file_recursive(folder_id, file_name)
    if found_file:
        try:
            file = client.file(file_id).get()
            file_path = f"/tmp/{file.name}"
            
            with open(file_path, "w") as f:
                f.write(new_content)

            updated_file = file.update_contents(file_path)
            os.remove(file_path)  # Cleanup temp file
            return f"✅ File '{file.name}' updated successfully"
        except Exception as e:
            return f"❌ Error updating file: {e}"
    else:
        return f"❌ File not found"


def delete_file(folder_id, file_name):
    """Delete a file from the Box CTF folder."""
    found_file, file_id, file_content = search_file_recursive(folder_id, file_name)
    if found_file:
        try:
            file = client.file(file_id)
            file.delete()
            return f"✅ File (ID: {file_id}) deleted successfully"
        except Exception as e:
            return f"❌ Error deleting file: {e}"
    else:
        return f"❌ File not found"
