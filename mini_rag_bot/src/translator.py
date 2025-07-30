import os
import google.generativeai as genai

def translate_to_english(text, source_lang):
    """Translate text to English using Gemini."""
    try:
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        Translate the following text from {source_lang} to English. 
        Only provide the translation, no additional text or explanations.
        
        Text to translate: {text}
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails

def translate_from_english(text, target_lang):
    """Translate text from English to the target language using Gemini."""
    try:
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Language mapping for better prompts
        lang_names = {
            'hi': 'Hindi',
            'bn': 'Bengali',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese'
        }
        
        target_language = lang_names.get(target_lang, target_lang)
        
        prompt = f"""
        Translate the following English text to {target_language}. 
        Only provide the translation, no additional text or explanations.
        
        Text to translate: {text}
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails
