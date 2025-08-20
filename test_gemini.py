import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    logger.error("Error: GOOGLE_API_KEY not found in .env file.")
    exit()

logger.info(f"Found Google API Key: {api_key[:5]}...{api_key[-4:]}")

try:
    # Configure genai
    genai.configure(api_key=api_key)
    logger.info("Google GenAI configured.")

    # --- List Available Models ---
    logger.info("Listing available models...")
    available_models = []
    for m in genai.list_models():
      # Check if the model supports the 'generateContent' method
      if 'generateContent' in m.supported_generation_methods:
        available_models.append(m.name) # Keep the full name like 'models/...'
    logger.info(f"Models supporting 'generateContent': {available_models}")
    # --- End Listing Models ---

    # --- Try using a recommended model from the list ---
    target_model_name = None
    # Prioritize the recommended model
    if 'models/gemini-1.5-flash-latest' in available_models:
         target_model_name = 'models/gemini-1.5-flash-latest' # Use the full name
    elif 'models/gemini-1.5-flash' in available_models:
         target_model_name = 'models/gemini-1.5-flash' # Fallback option
    elif available_models: # Fallback to the first available model if needed
        target_model_name = available_models[0] # Use the first full name from the list
        logger.warning(f"Could not find recommended 'gemini-1.5-flash' variants, trying '{target_model_name}' instead.")
    else:
        logger.error("No models supporting 'generateContent' found for your API key.")
        exit()
    # --- End Model Selection ---


    if target_model_name:
        logger.info(f"Attempting to use model: {target_model_name}")
        # Use the FULL model name here
        model = genai.GenerativeModel(target_model_name)

        # Simple test prompt
        prompt = "Say 'Hello, Gemini!'"
        logger.info(f"Sending prompt: '{prompt}'")

        # Generate content
        response = model.generate_content(prompt)

        # Check response
        if hasattr(response, 'text'):
             logger.info("\nSuccess! Received response from Gemini:")
             logger.info(f"  Response Text: {response.text.strip()}")
        # Check for potential block reasons
        elif hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
             logger.warning("\nWarning: Prompt was blocked by Gemini safety filters.")
             logger.warning(f"  Block Reason: {response.prompt_feedback.block_reason}")
             logger.warning(f"  Safety Ratings: {response.prompt_feedback.safety_ratings}")
        # Check candidates for block reasons
        elif response.candidates and response.candidates[0].finish_reason != 'STOP':
             logger.warning("\nWarning: Content generation stopped.")
             logger.warning(f"  Finish Reason: {response.candidates[0].finish_reason}")
             logger.warning(f"  Safety Ratings: {response.candidates[0].safety_ratings}")
        else:
             logger.warning("\nWarning: Received an unexpected response format from Gemini.")
             logger.warning(f"  Full Response: {response}")


except Exception as e:
    logger.error(f"\nAn error occurred during the Gemini API test: {e}", exc_info=True) 