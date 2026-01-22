import os
import json
import google.generativeai as genai
from typing import Optional, Dict, Any


def configure_gemini():
    """Configure Gemini API with the API key from environment."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    genai.configure(api_key=api_key)


def extract_contact_info_gemini(text: str, model_name: str = "gemini-2.5-flash") -> Dict[str, Optional[str]]:
    """
    Extract contact information from text using Gemini.
    
    Args:
        text: The natural language text containing contact information
        model_name: The Gemini model to use
        
    Returns:
        Dictionary with name, email, and phone fields (or None for missing fields)
    """
    configure_gemini()
    
    # Create the model instance with the exact model name
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config={
            "response_mime_type": "application/json"
        }
    )
    
    # System prompt for structured extraction
    system_prompt = """Extract contact information from the given text.
Return a JSON object with these exact fields:
•⁠  ⁠name: The person's full name (string or null if not present)
•⁠  ⁠email: The email address (string or null if not present)
•⁠  ⁠phone: The phone number (string or null if not present)

Important rules:
1.⁠ ⁠Return ONLY the JSON object, no other text
2.⁠ ⁠Use null (not "null" string) for missing fields
3.⁠ ⁠Extract the full name as it appears in the text
4.⁠ ⁠Keep phone numbers in their original format
5.⁠ ⁠If no person name is mentioned, set name to null
6.⁠ ⁠Do not make up or infer information that isn't explicitly in the text

Return the JSON object now."""
    
    # Combine prompt with text
    prompt = f"{system_prompt}\n\nText: {text}"
    
    try:
        # Generate content
        response = model.generate_content(prompt)
        
        # Parse the JSON response
        result = json.loads(response.text)
        
        # Ensure all required fields are present
        contact_info = {
            "name": result.get("name"),
            "email": result.get("email"),
            "phone": result.get("phone")
        }
        
        return contact_info
        
    except json.JSONDecodeError as e:
        # If JSON parsing fails, try to extract manually or return nulls
        print(f"JSON decode error: {e}")
        print(f"Response text: {response.text}")
        return {"name": None, "email": None, "phone": None}
    except Exception as e:
        print(f"Error extracting contact info: {e}")
        raise


def extract_contact_info_openai(text: str, model_name: str = "gpt-4o-mini") -> Dict[str, Optional[str]]:
    """
    Extract contact information from text using OpenAI.
    
    Args:
        text: The natural language text containing contact information
        model_name: The OpenAI model to use
        
    Returns:
        Dictionary with name, email, and phone fields (or None for missing fields)
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai package is required for GPT models. Install it with: pip install openai")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    client = OpenAI(api_key=api_key)
    
    system_prompt = """Extract contact information from the given text.
Return a JSON object with these exact fields:
- name: The person's full name (string or null if not present)
- email: The email address (string or null if not present)
- phone: The phone number (string or null if not present)

Important rules:
1. Return ONLY the JSON object, no other text
2. Use null (not "null" string) for missing fields
3. Extract the full name as it appears in the text
4. Keep phone numbers in their original format
5. If no person name is mentioned, set name to null
6. Do not make up or infer information that isn't explicitly in the text"""
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        contact_info = {
            "name": result.get("name"),
            "email": result.get("email"),
            "phone": result.get("phone")
        }
        
        return contact_info
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return {"name": None, "email": None, "phone": None}
    except Exception as e:
        print(f"Error extracting contact info: {e}")
        raise


def extract_contact_info(text: str, model_name: str = "gemini-2.5-flash") -> Dict[str, Optional[str]]:
    """
    Extract contact information from text using the specified LLM.
    
    Args:
        text: The natural language text containing contact information
        model_name: The model to use (gemini-* or gpt-*)
        
    Returns:
        Dictionary with name, email, and phone fields (or None for missing fields)
    """
    if model_name.startswith("gpt-"):
        return extract_contact_info_openai(text, model_name)
    else:
        return extract_contact_info_gemini(text, model_name)
