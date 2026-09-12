import os
from google import genai
from PIL import Image

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set. Please set it before testing.")
        return

    try:
        client = genai.Client(api_key=api_key)
        # Create a small blank image for testing dynamically
        img = Image.new('RGB', (100, 100), color = 'red')
        
        print("Sending request with standard [str, PIL.Image] format...")
        res = client.models.generate_content(
            model="gemini-3.6-flash", 
            contents=["Describe the main color in this image in one word", img]
        )
        print("\n✅ SUCCESS! Payload format accepted by the installed SDK version.")
        print(f"Response: {res.text}")
    except Exception as e:
        print("\n❌ ERROR encountered with the loose payload format:")
        print(e)
        print("\nIf you see a TypeError or 400 here, we will need to wrap the variables in explicit `types.Part` objects.")

if __name__ == "__main__":
    main()
