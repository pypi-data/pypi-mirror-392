# Functions to allow users to:
# - List NextCloud files and subfolders in a tree view
# - Upload files or folders from local to NextCloud
# - Download files or folders from NextCloud to local

import os
import sys
import time
import math
import requests
import concurrent.futures
import xml.etree.ElementTree as ET
from urllib.parse import quote
from tqdm import tqdm
from typing import List, Optional, Union
from urllib.parse import unquote

# WebDAV base path structure is standard for Nextcloud/OwnCloud WebDAV
WEBDAV_ROOT = "/remote.php/dav/files/"

# Namespaces required for parsing the WebDAV XML response
NAMESPACES = {
    'd': 'DAV:',
}

def _human_readable_size(size_bytes):
    """Converts a size in bytes to a human-readable string (KB, MB, GB, etc.)."""
    if size_bytes is None or size_bytes == 0:
        return "0 B"
    
    size_bytes = float(size_bytes)
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def _get_propfind_xml():
    """XML body for PROPFIND request, requesting resource type and content length."""
    return f"""<?xml version="1.0" encoding="utf-8" ?>
<d:propfind xmlns:d="DAV:">
  <d:prop>
    <d:resourcetype/>
    <d:getcontentlength/>
  </d:prop>
</d:propfind>"""

def _build_webdav_url(base_url: str, username: str, remote_path: str) -> str:
    """Builds the full WebDAV URL for a given path."""
    remote_path = remote_path.strip("/")
    
    # Nextcloud URL structure: /remote.php/dav/files/{username}/{path_to_resource}
    webdav_path = "/".join([
        WEBDAV_ROOT.strip("/"),
        quote(username),
        quote(remote_path)
    ])
    
    return f"{base_url.rstrip('/')}/{webdav_path}"


def nextcloud_folder_check(base_url: str, username: str, app_password: str, remote_folder: str):
    """
    Ensure that a remote folder exists in Nextcloud using MKCOL.
    Creates parent folders recursively if necessary.
    """
    parts = [p for p in remote_folder.strip("/").split("/") if p]
    if not parts:
        return # Cannot check/create root folder
        
    for i in range(1, len(parts) + 1):
        subfolder = "/".join(parts[:i])
        url = _build_webdav_url(base_url, username, subfolder)
        response = requests.request("MKCOL", url, auth=(username, app_password))
        
        # 201: created, 405: already exists
        if response.status_code not in (201, 405):
            print(f"⚠️ Could not create folder '{subfolder}' ({response.status_code})")
            

# --- LISTING FUNCTION ---

def list_remote_path(base_url: str, username: str, app_password: str, remote_path: str, max_depth: int = 3) -> None:
    """
    Lists files and folders from a Nextcloud WebDAV endpoint recursively (tree view).

    :param base_url: Nextcloud server URL 
    :param username: Nextcloud username.
    :param app_password: Nextcloud app password.
    :param remote_path: The starting folder relative to the user's files.
    :param max_depth: Limits recursion depth for large directories.
    """
    
    def _list_recursive(current_path, indent=0):
        if indent >= max_depth:
            print(f"{'  ' * indent}...")
            return

        # Display the current directory name
        if current_path:
            display_name = current_path.split('/')[-1]
            print(f"{'  ' * indent}|-- 📁\033[94m{display_name}/\033[0m")
        
        child_indent = indent + (1 if current_path else 0)

        # Build URL for PROPFIND (Depth 1)
        url = _build_webdav_url(base_url, username, current_path) + '/'
        current_full_path_suffix = url.split(f"/{quote(username)}/")[-1].strip('/')

        headers = {'Depth': '1', 'Content-Type': 'application/xml; charset=utf-8'}

        try:
            response = requests.request(
                'PROPFIND', url, auth=(username, app_password), headers=headers,
                data=_get_propfind_xml(), verify=True
            )

            if response.status_code == 401:
                print(f"\n{'  ' * child_indent}!!! ❌ ERROR: Authentication failed. Check credentials. !!!")
                return
            if response.status_code != 207:
                print(f"\n{'  ' * child_indent}!!! ❌ ERROR: Failed to list path. Status: {response.status_code} !!!")
                return

            root = ET.fromstring(response.content)
            directories_to_recurse = []

            for resp in root.findall('d:response', NAMESPACES):
                href = resp.find('d:href', NAMESPACES).text.strip('/')

                # Skip the entry for the directory itself
                if href.endswith(current_full_path_suffix) or not href:
                    continue
                
                # Get the name of the folder we are currently listing (for display)
                current_dir_name = current_path.split('/')[-1] 
                
                # Get the decoded name of the item from the PROPFIND response
                item_name_encoded = href.split('/')[-1]
                item_name = unquote(item_name_encoded)
                
                if item_name == current_dir_name:
                    continue # Skip the duplicate folder entry

                resourcetype_elem = resp.find('./d:propstat/d:prop/d:resourcetype', NAMESPACES)
                is_dir = resourcetype_elem is not None and resourcetype_elem.find('d:collection', NAMESPACES) is not None
                
                size_elem = resp.find('./d:propstat/d:prop/d:getcontentlength', NAMESPACES)
                size_bytes = int(size_elem.text) if size_elem is not None and size_elem.text else 0

                item_name = unquote(href.split('/')[-1])
                tree_prefix = '  ' * child_indent + '|-- 📄'
                
                if is_dir:
                    directories_to_recurse.append(item_name)
                else:
                    size_str = _human_readable_size(size_bytes)
                    print(f"{tree_prefix}{item_name} \033[90m({size_str})\033[0m")
                
            for directory in directories_to_recurse:

                if directory == username:
                    continue
                    
                new_path = f"{current_path.rstrip('/')}/{directory}"
                _list_recursive(new_path, child_indent)
                
        
        except requests.exceptions.RequestException as e:
            print(f"\n{'  ' * child_indent}!!! ❌ NETWORK ERROR: Could not connect to {base_url}. Details: {e} !!!")
        except ET.ParseError as e:
            print(f"\n{'  ' * child_indent}!!! ❌ XML PARSE ERROR: Failed to parse response. Details: {e} !!!")

    print(f"--- Nextcloud Directory Listing ---\nStarting at: \033[92m{remote_path.strip('/')}/\033[0m")
    _list_recursive(remote_path.strip('/'), 0)
    print("")
    print("✅ Listing Complete")


# --- UPLOAD FUNCTIONS ---

def upload_file(base_url: str,
                username: str,
                app_password: str,
                remote_folder: str,
                local_file_path: str,
                retries: int = 3) -> bool:
    """Uploads a single local file to a specified remote folder."""
    
    remote_file_name = os.path.basename(local_file_path)
    target_url = _build_webdav_url(base_url, username, f"{remote_folder.strip('/')}/{remote_file_name}")

    file_size = os.path.getsize(local_file_path)
    nextcloud_folder_check(base_url, username, app_password, remote_folder)

    for attempt in range(1, retries + 1):
        try:
            with open(local_file_path, "rb") as f:
                with tqdm.wrapattr(
                    f, "read",
                    total=file_size,
                    desc=f"⬆️ {os.path.basename(local_file_path)}",
                    unit="B", unit_scale=True, unit_divisor=1024
                ) as stream:
                    response = requests.put(
                        target_url,
                        data=stream,
                        auth=(username, app_password),
                        timeout=120
                    )

            if response.status_code in (200, 201, 204):
                return True
            else:
                print(f"❌ Upload failed ({response.status_code}): {os.path.basename(local_file_path)}")
                print(response.text)

        except Exception as e:
            print(f"⚠️ Error uploading {local_file_path}: {e}")

        if attempt < retries:
            print(f"🔁 Retrying {os.path.basename(local_file_path)} ({attempt}/{retries})...")
            time.sleep(3)

    print(f"🚫 Giving up on {local_file_path}")
    return False

def upload_folder_recursive(base_url: str,
                            username: str,
                            app_password: str,
                            remote_parent_folder: str,
                            local_dir: str,
                            max_workers: int = 4):
    """Upload a local folder (and its contents recursively) to Nextcloud."""
    
    if not os.path.isdir(local_dir):
        raise ValueError(f"{local_dir} is not a valid directory")

    local_dir = os.path.abspath(local_dir)
    folder_name = os.path.basename(local_dir.rstrip(os.sep))
    remote_base = os.path.join(remote_parent_folder.strip("/"), folder_name).replace("\\", "/")

    nextcloud_folder_check(base_url, username, app_password, remote_base)

    print(f"📂 Preparing folder '{folder_name}' for upload to Nextcloud path '{remote_base}'...")

    all_files = []
    for root, _, files in os.walk(local_dir):
        for name in files:
            all_files.append(os.path.join(root, name))

    base_len = len(local_dir.rstrip(os.sep)) + 1
    print(f"Found {len(all_files)} files to upload.\n")

    def _upload_one(local_file):
        rel_path = local_file[base_len:]
        rel_dir = os.path.dirname(rel_path)
        
        # Calculate the remote folder for this specific file
        remote_path = os.path.join(remote_base, rel_dir).replace("\\", "/")

        # Ensure the remote directory structure exists
        if rel_dir:
            nextcloud_folder_check(base_url, username, app_password, remote_path)

        success = upload_file(
            base_url, username, app_password, remote_path, local_file, retries=3
        )
        return success

    success_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_upload_one, f): f for f in all_files}
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                success_count += 1

    print(f"\n✅ Upload complete: {success_count}/{len(all_files)} files uploaded successfully.")
    print(f"📂 Remote folder created: {remote_base}")


# --- DOWNLOAD FUNCTIONS ---

def _download_single_file(base_url: str, username: str, app_password: str, remote_full_path: str, local_file_path: str) -> bool:
    """Downloads a single file from the WebDAV path to the specified local file path."""
    
    remote_full_path = remote_full_path.strip('/')
    final_download_url = _build_webdav_url(base_url, username, remote_full_path)

    try:
        # Use stream=True for large files
        with requests.get(final_download_url, auth=(username, app_password), stream=True, verify=True) as r:
            r.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

            total_size = int(r.headers.get('content-length', 0))
            chunk_size = 8192 # 8KB chunks
            
            with open(local_file_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024, 
                          desc=f"⬇️ {os.path.basename(local_file_path)}") as pbar:
                    for chunk in r.iter_content(chunk_size=chunk_size): 
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

        return True

    except requests.exceptions.RequestException as e:
        print(f"\n❌ [FAIL] Download failed for {local_file_path}. Network or HTTP Error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ [FAIL] An unexpected error occurred during file write for {local_file_path}: {e}")
        return False

def _get_resource_details(base_url: str, username: str, app_password: str, remote_path: str):
    """Performs a Depth 0 PROPFIND on a single relative path to determine its type."""

    full_url = _build_webdav_url(base_url, username, remote_path)
    headers = { 'Depth': '0', 'Content-Type': 'application/xml; charset=utf-8' }

    try:
        response = requests.request(
            'PROPFIND', full_url, auth=(username, app_password), 
            headers=headers, data=_get_propfind_xml(), verify=True 
        )

        if response.status_code != 207:
            return None # Failed to get details

        root = ET.fromstring(response.content)
        resp = root.find('d:response', NAMESPACES)

        if resp is None:
             return None

        resourcetype_elem = resp.find('./d:propstat/d:prop/d:resourcetype', NAMESPACES)
        is_folder = resourcetype_elem is not None and resourcetype_elem.find('d:collection', NAMESPACES) is not None
        
        return is_folder

    except requests.exceptions.RequestException:
        return None
    except ET.ParseError:
        return None


def _recursive_download_contents(base_url: str, username: str, app_password: str, remote_full_dir_path: str, local_parent_dir: str):
    """Recursively downloads all contents of a folder, preserving structure."""
    
    remote_full_dir_path = remote_full_dir_path.strip('/')
    
    # 1. Determine the local path for the current remote folder and ensure it exists
    folder_name = remote_full_dir_path.split('/')[-1]
    local_dir_path = os.path.join(local_parent_dir, folder_name)
    os.makedirs(local_dir_path, exist_ok=True)
    
    print(f"\nEntering remote folder: {remote_full_dir_path}")
    
    # 2. Get children of the current remote folder (Depth 1 PROPFIND)
    url = _build_webdav_url(base_url, username, remote_full_dir_path) + '/'
    current_full_path_suffix = url.split(f"/{quote(username)}/")[-1].strip('/')

    headers = { 'Depth': '1', 'Content-Type': 'application/xml; charset=utf-8' }
    
    try:
        response = requests.request(
            'PROPFIND', url, auth=(username, app_password), 
            headers=headers, data=_get_propfind_xml(), verify=True
        )
        
        if response.status_code != 207:
            print(f"❌ [FAIL] Could not list contents of {remote_full_dir_path}. Status: {response.status_code}")
            return

        root = ET.fromstring(response.content)
        
        for resp in root.findall('d:response', NAMESPACES):
            href = resp.find('d:href', NAMESPACES).text.strip('/')
            
            if href.endswith(current_full_path_suffix) or not href:
                continue
            
            item_name = href.split('/')[-1]
            # Remote item path MUST be relative to the user's files root
            remote_item_path = f"{remote_full_dir_path.rstrip('/')}/{item_name}"
            
            resourcetype_elem = resp.find('./d:propstat/d:prop/d:resourcetype', NAMESPACES)
            is_dir = resourcetype_elem is not None and resourcetype_elem.find('d:collection', NAMESPACES) is not None
            
            if is_dir:
                _recursive_download_contents(base_url, username, app_password, remote_item_path, local_dir_path)
            else:
                local_file_path = os.path.join(local_dir_path, item_name)
                _download_single_file(base_url, username, app_password, remote_item_path, local_file_path)
        
    except Exception as e:
        print(f"\n❌ [FAIL] Error during recursive download in {remote_full_dir_path}: {e}")


def download_resource(base_url: str, username: str, app_password: str, remote_path: str, local_download_base_path: str):
    """
    Downloads a single file or an entire folder recursively.
    
    :param base_url: Nextcloud server URL 
    :param username: Nextcloud username.
    :param app_password: Nextcloud app password.
    :param remote_path: The path of the resource on Nextcloud (relative to the user's root files).
    :param local_download_base_path: The local directory where the file/folder will be placed.
    """
    
    remote_path = remote_path.strip('/')
    if not remote_path:
        print("❌ [ERROR] Cannot download root path. Please specify a file or subfolder.")
        return

    print(f"\nChecking resource type for '{remote_path}'...")
    is_folder = _get_resource_details(base_url, username, app_password, remote_path)

    if is_folder is None:
        print(f"❌ [FAIL] Download failed: Could not verify path '{remote_path}'.")
        return

    os.makedirs(local_download_base_path, exist_ok=True)

    if is_folder:
        print(f"Starting recursive download for folder '{remote_path}'.")
        # Download into the specified base directory
        _recursive_download_contents(base_url, username, app_password, remote_path, local_download_base_path)
        print(f"\n✅ [SUCCESS] Recursive download of '{remote_path}' complete.")
    else:
        # Single file download
        local_filename = os.path.join(local_download_base_path, remote_path.split('/')[-1])
        if _download_single_file(base_url, username, app_password, remote_path, local_filename):
            print(f"\n✅ [SUCCESS] Downloaded file to: {local_filename}")
