import os
from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, APIConnectionError

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print("Error: OPENAI_API_KEY not found in .env file.")
    exit()

print(f"Found API Key: {api_key[:5]}...{api_key[-4:]}") # Print partial key for verification

try:
    # Initialize the OpenAI client
    # Make sure you have the 'openai' library installed: pip install openai
    client = OpenAI(api_key=api_key)

    print("Attempting to connect to OpenAI API...")

    # Make a simple test call
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", # Use a standard, usually available model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, OpenAI!'"}
        ],
        max_tokens=10 # Keep the response short
    )

    # Check the response
    if response.choices and response.choices[0].message:
        print("\nSuccess! Received response from OpenAI:")
        print(f"  Model Used: {response.model}")
        print(f"  Response Text: {response.choices[0].message.content.strip()}")
    else:
        print("\nWarning: Received an unexpected response format from OpenAI.")
        print(response)

except AuthenticationError:
    print("\nError: OpenAI API Key is invalid or incorrect. Please check your .env file.")
except APIConnectionError as e:
    print(f"\nError: Failed to connect to OpenAI API.")
    print(f"  Details: {e}")
    print("  Please check your internet connection, firewall settings, or VPN/proxy configuration.")
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}") 