from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

import PIL.Image


# Configure the Gemini API with the provided API key from agent.py
# NOTE: Hardcoding API keys is not recommended for production.
# Consider using environment variables or a secure configuration method.


# Choose the experimental model supporting image generation used in agent.py
# NOTE: Experimental models may change or be deprecated.
MODEL_ID = "gemini-2.0-flash-exp"

def generate_image_from_prompt(prompt: str, output_path: str = "generated_image.png"):
    """
    Generates an image using the Gemini API with the specified model and saves it.

    Args:
        prompt (str): The text prompt for image generation.
        output_path (str): The path to save the generated image.
    """
    if not prompt:
        print("Error: Prompt is required for image generation.")
        return

    try:
        # Set up the model instance, requesting image output
      
        client = genai.Client(api_key="AIzaSyBgnkWuFV2YNEwauGiZ0IhQyEu3iXRvVL0")

        text_input = (prompt)

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=[text_input],
            config=types.GenerateContentConfig(
            response_modalities=['TEXT','IMAGE']
            )
        )

        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                image = Image.open(BytesIO(part.inline_data.data))
                image.save(output_path)

    except Exception as e:
        print(f"An error occurred during Gemini image generation: {e}")
        # Attempt to extract error details from the response if available
        error_message = str(e)
        if hasattr(e, 'response') and e.response is not None:
             try:
                 error_details = e.response.json()
                 print(f"Gemini API error response details: {error_details}")
                 if 'error' in error_details and 'message' in error_details['error']:
                     error_message = error_details['error']['message']
             except:
                 pass # Ignore if response is not JSON or doesn't have expected structure
        print(f"Gemini API error: {error_message}")


if __name__ == "__main__":
    # Example usage:
    test_prompt = "A vibrant abstract painting"
    generate_image_from_prompt(test_prompt)

    # You can add more test cases here
    # generate_image_from_prompt("A black and white photograph of a forest", "forest_bw.png")
