import logging
import os
import uuid
import base64
import io
import requests
import urllib.parse
import sys

# Import PIL and ImageGrab
try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None

# Import Gemini and OpenAI related libraries
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

# Import functions from other refactored files
from filesystem_utils import ( # Corrected import path
    is_temp_image_path_safe,
    create_temp_image_directory,
    TEMP_IMAGE_DIR # Need to access this config
)

# --- Configuration (These might need to be passed in or read from a config) ---
# For now, hardcoding based on original agent.py
# TEMP_IMAGE_DIR is now imported from filesystem_utils
# Need access to the script directory from the main agent.py or a config
# For now, assuming this file is in the agent directory
script_dir = os.path.dirname(__file__)
temp_image_path = os.path.join(script_dir, TEMP_IMAGE_DIR)

# NOTE: Hardcoding API keys is not recommended for production.
# Consider using environment variables or a secure configuration method.
GEMINI_API_KEY = "AIzaSyBgnkWuFV2YNEwauGiZ0IhQyEu3iXRvVL0"
OPENAI_API_KEY = "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"
OPENAI_ORG_ID = "org-tKC8NPkFUxkTIVpGgsZqvdEU"


# --- Logging Setup (Assuming basic logging is configured in the main agent.py) ---
# Need to ensure logging is configured before these functions are called
def log(msg, level=logging.INFO):
    logging.log(level, msg)

# --- Helper to create temporary image directory ---
def create_temp_image_directory():
    """Creates the temporary image directory if it doesn't exist."""
    if not os.path.exists(temp_image_path):
        try:
            os.makedirs(temp_image_path)
            log(f"Created temporary image directory: {temp_image_path}")
        except OSError as e:
            log(f"Error creating temporary image directory {temp_image_path}: {e}", level=logging.ERROR)

# --- Image Generation Functions ---

def generate_image_gemini(prompt, temp_image_path):
    log(f"Calling Gemini API with prompt: {prompt}", level=logging.DEBUG)

    if genai is None or types is None:
        log("Gemini API libraries not available.", level=logging.ERROR)
        return {"status": "error", "message": "Gemini API libraries not installed.", "status_code": 500}

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        log(f"Error configuring Gemini API: {e}", level=logging.ERROR)
        return {"status": "error", "message": f"Failed to configure Gemini API: {e}", "status_code": 500}

    model_id = "gemini-2.0-flash-exp-image-generation"

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=['TEXT','IMAGE']
            )
        )
        log(f"Gemini API response received.", level=logging.DEBUG)

        image_data_base64 = None
        mime_type = None

        if response.candidates and len(response.candidates) > 0:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_data_base64 = part.inline_data.data
                    mime_type = part.inline_data.mime_type
                    log(f"Found image data in response (MIME type: {mime_type})", level=logging.DEBUG)
                    break

        if image_data_base64 and mime_type:
            try:
                image_binary_data = image_data_base64

                temp_filename = f"generated_image_gemini_{uuid.uuid4().hex}.png"
                temp_file_path_full = os.path.join(temp_image_path, temp_filename)

                os.makedirs(os.path.dirname(temp_file_path_full), exist_ok=True)

                with open(temp_file_path_full, "wb") as f:
                    f.write(image_binary_data)

                log(f"Saved generated image to temporary file: {temp_file_path_full}", level=logging.DEBUG)

                temp_image_url = f"/{TEMP_IMAGE_DIR}/{temp_filename}"
                return {"status": "success", "temp_image_url": temp_image_url}

            except Exception as save_e:
                log(f"Error saving generated image to temporary file: {save_e}", level=logging.ERROR)
                return {"status": "error", "message": f"Failed to save generated image temporarily: {save_e}", "status_code": 500}

        else:
            log("Gemini API response did not contain expected image data.", level=logging.ERROR)
            log(f"Full Gemini API response: {response}", level=logging.DEBUG)
            return {"status": "error", "message": "Failed to generate image or retrieve image data from API response.", "status_code": 500}

    except Exception as e:
        log(f"Error calling Gemini API for image generation: {e}", level=logging.ERROR)
        error_message = str(e)
        if hasattr(e, 'response') and e.response is not None:
             try:
                 error_details = e.response.json()
                 log(f"Gemini API error response details: {error_details}", level=logging.DEBUG)
                 if 'error' in error_details and 'message' in error_details['error']:
                     error_message = error_details['error']['message']
             except:
                 pass

        return {"status": "error", "message": f"Gemini API error: {error_message}", "status_code": 500}


def generate_image_openai(prompt, size, temp_image_path):
    log(f"Calling OpenAI API with prompt: {prompt}, size: {size}", level=logging.DEBUG)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Organization": OPENAI_ORG_ID
    }

    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": size
    }

    try:
        response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        if data and data.get("data") and len(data["data"]) > 0:
            image_url = data["data"][0].get("url")
            if image_url:
                log(f"OpenAI image generated successfully: {image_url}", level=logging.DEBUG)
                image_response = requests.get(image_url)
                image_response.raise_for_status()

                temp_filename = f"generated_image_openai_{uuid.uuid4().hex}.png"
                temp_file_path_full = os.path.join(temp_image_path, temp_filename)

                os.makedirs(os.path.dirname(temp_file_path_full), exist_ok=True)

                with open(temp_file_path_full, "wb") as f:
                    f.write(image_response.content)

                log(f"Saved generated image to temporary file: {temp_file_path_full}", level=logging.DEBUG)

                temp_image_url = f"/{TEMP_IMAGE_DIR}/{temp_filename}"
                return {"status": "success", "temp_image_url": temp_image_url}

            else:
                log("OpenAI image URL not found in response", level=logging.ERROR)
                return {"status": "error", "message": "Image URL not found in response", "status_code": 500}
        else:
            log(f"Invalid response from OpenAI API: {data}", level=logging.ERROR)
            return {"status": "error", "message": "Invalid response from OpenAI API", "status_code": 500}

    except requests.exceptions.RequestException as e:
        log(f"Error calling OpenAI API: {e}", level=logging.ERROR)
        return {"status": "error", "message": f"Error calling OpenAI API: {e}", "status_code": 500}
    except Exception as e:
        log(f"An unexpected error occurred during OpenAI image generation: {e}", level=logging.ERROR)
        return {"status": "error", "message": f"An unexpected error occurred: {e}", "status_code": 500}


def improve_prompt_gemini(prompt):
    log(f"Calling Gemini API for prompt improvement with prompt: {prompt}", level=logging.DEBUG)

    if genai is None or types is None:
        log("Gemini API libraries not available.", level=logging.ERROR)
        return {"status": "error", "message": "Gemini API libraries not installed.", "status_code": 500}

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        log(f"Error configuring Gemini API: {e}", level=logging.ERROR)
        return {"status": "error", "message": f"Failed to configure Gemini API: {e}", "status_code": 500}

    model_id = "gemini-2.5-flash-preview-04-17"

    prefixed_prompt = f"improve that image request prompt, dont give me any options: {prompt}"

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=[prefixed_prompt],
            config=types.GenerateContentConfig(
                response_modalities=['TEXT']
            )
        )
        log(f"Gemini API response received for prompt improvement.", level=logging.DEBUG)

        improved_prompt = ""
        if response.candidates and len(response.candidates) > 0:
            for part in response.candidates[0].content.parts:
                if part.text:
                    improved_prompt += part.text
            log(f"Extracted improved prompt: {improved_prompt}", level=logging.DEBUG)
            return {"status": "success", "improved_prompt": improved_prompt}
        else:
            log("Gemini API response did not contain expected text data for prompt improvement.", level=logging.ERROR)
            log(f"Full Gemini API response: {response}", level=logging.DEBUG)
            return {"status": "error", "message": "Failed to improve prompt or retrieve text data from API response.", "status_code": 500}

    except Exception as e:
        log(f"Error calling Gemini API for prompt improvement: {e}", level=logging.ERROR)
        error_message = str(e)
        if hasattr(e, 'response') and e.response is not None:
             try:
                 error_details = e.response.json()
                 log(f"Gemini API error response details: {error_details}", level=logging.DEBUG)
                 if 'error' in error_details and 'message' in error_details['error']:
                     error_message = error_details['error']['message']
             except:
                 pass

        return {"status": "error", "message": f"Gemini API error: {error_message}", "status_code": 500}

def capture_screenshot():
    """Capture the current screen as a PNG image and return as BytesIO."""
    if ImageGrab is None:
        log("Screenshot functionality not available. Pillow is not installed.", level=logging.ERROR)
        return {"status": "error", "message": "Screenshot functionality not available. Pillow is not installed.", "status_code": 500}
    try:
        img = ImageGrab.grab()
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        # Do not seek(0) here, the caller will do it before sending
        return {"status": "success", "image_buffer": buf}
    except Exception as e:
        log(f"Screenshot capture error: {e}", level=logging.ERROR)
        return {"status": "error", "message": f"Screenshot failed: {e}", "status_code": 500}
