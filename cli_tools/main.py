#!/usr/bin/env python3
import argparse
import requests
import os
import uuid
import json

def find_project_root(marker='Makefile'):
    # 1. Check for environment variable
    if 'SIMON_NB_PROJECT_ROOT' in os.environ:
        project_root = os.environ['SIMON_NB_PROJECT_ROOT']
        if os.path.exists(os.path.join(project_root, marker)):
            return project_root
        else:
            print(f"Warning: SIMON_NB_PROJECT_ROOT is set to '{project_root}', but marker file '{marker}' was not found there.")

    # 2. Fallback to searching from current directory
    path = os.getcwd()
    while path != '/':
        if os.path.exists(os.path.join(path, marker)):
            return path
        path = os.path.dirname(path)
    return None

def main():
    parser = argparse.ArgumentParser(description="Simon NB CLI tool.")
    parser.add_argument("image_url", help="URL or local path of the image to process.")
    parser.add_argument("prompt", help="Prompt for the image generation.")
    args = parser.parse_args()

    project_root = find_project_root()
    if not project_root:
        print("Error: Could not find project root.")
        print("Please run this command from within the project directory, or set the SIMON_NB_PROJECT_ROOT environment variable.")
        return

    # --- 1. Handle image source (URL or local path) ---
    image_source = args.image_url
    image_bytes = None

    if image_source.startswith('http://') or image_source.startswith('https://'):
        print("Downloading image...")
        try:
            response = requests.get(image_source)
            response.raise_for_status()
            image_bytes = response.content
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image: {e}")
            return
    elif os.path.exists(image_source):
        print(f"Reading local image from: {image_source}")
        with open(image_source, "rb") as f:
            image_bytes = f.read()
    else:
        print(f"Error: Image source '{image_source}' is not a valid URL or an existing file path.")
        return

    if not image_bytes:
        print("Error: Could not read image data.")
        return

    # --- 2. Upload image to service ---
    print("Uploading image to service...")
    try:
        files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
        response = requests.post("http://127.0.0.1:8000/upload/", files=files)
        response.raise_for_status()
        response_json = response.json()
        container_image_path = response_json["file_path"]
        print(f"Image uploaded. Path in container: {container_image_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error uploading image: {e}")
        return

    # --- 3. Create session ---
    print("Creating session...")
    try:
        response = requests.post("http://127.0.0.1:8787/apps/nano-banana-agent/users/simon/sessions")
        response.raise_for_status()
        session_id = response.json()["id"]
        print(f"Session created: {session_id}")
    except requests.exceptions.RequestException as e:
        print(f"Error creating session: {e}")
        return

    # --- 4. Run SSE ---
    print("Running agent...")
    
    message = f"{container_image_path}\n\n{args.prompt}"

    payload = {
        "sessionId": session_id,
        "appName": "nano-banana-agent",
        "userId": "simon",
        "newMessage": {
            "parts": [{"text": message}],
            "role": "user"
        },
        "streaming": True
    }

    try:
        with requests.post("http://localhost:8787/run_sse", json=payload, stream=True) as response:
            response.raise_for_status()
            final_image_url = None
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data:'):
                        try:
                            data = json.loads(decoded_line[5:])
                            if 'content' in data and 'parts' in data['content']:
                                for part in data['content']['parts']:
                                    if 'functionResponse' in part and part['functionResponse']['name'] == 'generate_nano_banana':
                                        response_data = part['functionResponse']['response']
                                        if response_data.get('status') == 'success':
                                            report = response_data.get('report', [])
                                            if report:
                                                final_image_url = report[0]
                                                break
                                        else:
                                            print(f"\n--- Agent Error ---\n{response_data.get('report')}\n-------------------")
                                            final_image_url = "ERROR" # Sentinel value to stop processing
                                            break
                                    # Fallback to text
                                    if 'text' in part and part['text'].startswith('http'):
                                        final_image_url = part['text']
                                        break
                        except json.JSONDecodeError:
                            continue
                if final_image_url:
                    break
    except requests.exceptions.RequestException as e:
        print(f"Error running agent: {e}")
        return

    if final_image_url == "ERROR": # Check for the sentinel value
        print("Agent failed to process the image. See error message above.")
        return

    if not final_image_url:
        print("Could not get the final image URL.")
        return

    print(f"Generated image URL: {final_image_url}")

    # --- 5. Download final image ---
    print("Downloading final image...")
    try:
        # The URL from the container might be localhost, replace if needed for the script's context
        final_image_url = final_image_url.replace('localhost', '127.0.0.1')
        response = requests.get(final_image_url, stream=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error downloading final image: {e}")
        return

    # --- 6. Save final image ---
    output_filename = os.path.basename(final_image_url.split('?')[0])
    with open(output_filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Processing complete. Image saved as {output_filename}")

if __name__ == "__main__":
    main()