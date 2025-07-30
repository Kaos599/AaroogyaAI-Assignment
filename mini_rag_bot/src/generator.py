import os
import time
import threading
import google.generativeai as genai
from langchain.prompts import PromptTemplate
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    """Custom timeout exception"""
    pass

def with_timeout(timeout_seconds=30):
    """Cross-platform timeout decorator using threading"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout_seconds)
            
            if thread.is_alive():
                # Thread is still running, timeout occurred
                logger.error(f"⏰ Function timed out after {timeout_seconds}s")
                raise TimeoutError(f"Function call timed out after {timeout_seconds}s")
            
            if exception[0]:
                raise exception[0]
            
            return result[0]
        return wrapper
    return decorator

def get_gemini_api_key():
    """Get the Gemini API key from environment variables."""
    return os.environ.get("GEMINI_API_KEY")

def configure_genai():
    """Configure the Generative AI client."""
    start_time = time.time()
    logger.info("🔧 Starting Gemini API configuration...")
    
    api_key = get_gemini_api_key()
    if not api_key:
        logger.error("❌ GEMINI_API_KEY environment variable not set.")
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    
    logger.info(f"🔑 API key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        # Simple configuration - timeout will be handled at the request level
        genai.configure(api_key=api_key)
        config_time = time.time() - start_time
        logger.info(f"✅ Gemini API configured successfully in {config_time:.2f}s")
    except Exception as e:
        logger.error(f"❌ Failed to configure Gemini API: {e}")
        raise

def generate_answer(context, question, model_name='gemini-2.5-flash', timeout_seconds=45):
    """Generate an answer using the Gemini model with enhanced women's health focus and proper citations."""
    total_start_time = time.time()
    logger.info("🔧 Starting answer generation with Gemini...")
    logger.info(f"🤖 Model: {model_name}")
    logger.info(f"⏰ Timeout: {timeout_seconds}s")
    logger.info(f"📝 Question: {question}")
    logger.info(f"📚 Context documents: {len(context) if context else 0}")
    
    # Configure API with timing
    config_start = time.time()
    configure_genai()
    config_time = time.time() - config_start
    logger.info(f"⏱️ API configuration took: {config_time:.2f}s")

    prompt_template = """
    You are a specialized Women's Health AI Assistant with expertise in:
    - Maternal and reproductive health
    - Gender-specific health conditions
    - Women's preventive care and wellness
    - Health equity and access issues for women
    - Evidence-based medical information

    INSTRUCTIONS:
    1. Use the provided context to answer questions about women's health
    2. Focus on evidence-based, medically accurate information
    3. Consider cultural, social, and economic factors affecting women's health
    4. Provide practical, actionable advice when appropriate
    5. Reference specific sources in your answer using the actual document names (e.g., "According to C. Women and health.pdf..." or "As mentioned in [Source 1]...")
    6. If the context doesn't contain sufficient information, clearly state this
    7. Emphasize the importance of consulting healthcare professionals for medical decisions
    8. Be specific about which information comes from which source
    9. When referencing sources, use the actual document names shown in parentheses after each source number

    CONTEXT WITH SOURCES:
    {context}

    QUESTION: {question}

    RESPONSE GUIDELINES:
    - Be comprehensive yet accessible
    - Use clear, non-technical language when possible
    - Include relevant statistics or data when available
    - Address potential health disparities or access issues
    - Provide culturally sensitive information
    - Always reference your sources within the answer text

    Answer:
    """

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    # Format context properly with detailed source information
    context_start = time.time()
    context_text = ""
    source_details = []
    
    if context:
        logger.info(f"🔧 Processing {len(context)} context documents...")
        for i, doc in enumerate(context):
            if hasattr(doc, 'page_content'):
                content = doc.page_content
            else:
                content = str(doc)
            
            # Extract source information
            source_info = "Unknown Source"
            source_type = "unknown"
            source_url = None
            
            if hasattr(doc, 'metadata') and doc.metadata:
                metadata = doc.metadata
                raw_source = metadata.get('source', 'Unknown Source')
                source_type = metadata.get('source_type', 'unknown')
                
                # Format source info based on type
                if source_type == 'local_document':
                    # Use the actual document name directly
                    source_info = raw_source
                    # If it's still a generic name, try to get the actual filename
                    if source_info.startswith('Local Knowledge Base') or source_info.startswith('Local Document'):
                        # Check if we have the original metadata with actual filename
                        original_meta = metadata.get('original_metadata', {})
                        if original_meta.get('source'):
                            source_info = original_meta['source']
                        else:
                            source_info = "C. Women and health.pdf"  # Default to main document
                elif source_type == 'web_search':
                    title = metadata.get('title', 'Web Article')
                    source_url = raw_source
                    source_info = title
                else:
                    source_info = raw_source
            
            source_details.append({
                'number': i+1,
                'source': source_info,
                'type': source_type,
                'url': source_url,
                'content_preview': content[:100] + "..." if len(content) > 100 else content,
                'raw_source': raw_source
            })
            
            # Use actual source names in the context
            display_source = source_info if source_info != "Unknown Source" else f"Document {i+1}"
            context_text += f"[Source {i+1}] ({display_source}): {content}\n\n"
    else:
        context_text = "No specific context provided."
        logger.warning("⚠️ No context provided for answer generation")
    
    context_time = time.time() - context_start
    logger.info(f"⏱️ Context processing took: {context_time:.2f}s")
    logger.info(f"📏 Context length: {len(context_text)} characters")

    # Format prompt with timing
    prompt_start = time.time()
    formatted_prompt = prompt.format(context=context_text, question=question)
    prompt_time = time.time() - prompt_start
    logger.info(f"⏱️ Prompt formatting took: {prompt_time:.2f}s")
    logger.info(f"📏 Final prompt length: {len(formatted_prompt)} characters")

    # Initialize model with timing
    model_start = time.time()
    try:
        model = genai.GenerativeModel(model_name)
        model_time = time.time() - model_start
        logger.info(f"⏱️ Model ({model_name}) initialization took: {model_time:.2f}s")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Gemini model {model_name}: {e}")
        raise
    
    # Enhanced generation config for better responses
    generation_config = genai.types.GenerationConfig(
        temperature=0.3,  # Lower temperature for more factual responses
        top_p=0.8,
        top_k=40,
        max_output_tokens=2048,
    )
    logger.info(f"🔧 Generation config: temp={generation_config.temperature}, max_tokens={generation_config.max_output_tokens}")
    
    # Make API call with detailed timing and error handling
    api_start = time.time()
    logger.info("🔧 Calling Gemini API...")
    logger.info("⏳ This may take 10-30 seconds depending on prompt complexity...")
    logger.info(f"⏰ API call will timeout after {timeout_seconds}s if no response")
    
    try:
        # Use the threading-based timeout as a backup
        @with_timeout(timeout_seconds)
        def make_api_call():
            return model.generate_content(formatted_prompt, generation_config=generation_config)
        
        response = make_api_call()
        api_time = time.time() - api_start
        logger.info(f"✅ Gemini API call completed in {api_time:.2f}s")
        
        # Check if response is valid
        if not response:
            logger.error("❌ No response from Gemini API")
            raise ValueError("No response from Gemini API")
        
        if not hasattr(response, 'text') or not response.text:
            logger.error("❌ Empty response text from Gemini API")
            # Try to get more info about the response
            if hasattr(response, 'candidates') and response.candidates:
                logger.info(f"📋 Response has {len(response.candidates)} candidates")
                for i, candidate in enumerate(response.candidates):
                    if hasattr(candidate, 'finish_reason'):
                        logger.info(f"   Candidate {i}: finish_reason = {candidate.finish_reason}")
            raise ValueError("Empty response text from Gemini API")
            
        logger.info(f"📏 Response length: {len(response.text)} characters")
        
    except TimeoutError as e:
        api_time = time.time() - api_start
        logger.error(f"❌ Gemini API call timed out after {api_time:.2f}s")
        raise TimeoutError(f"Gemini API call timed out after {api_time:.2f}s")
    except Exception as e:
        api_time = time.time() - api_start
        logger.error(f"❌ Gemini API call failed after {api_time:.2f}s: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        
        # Log additional debug info for common errors
        error_str = str(e).lower()
        if "quota" in error_str or "rate limit" in error_str:
            logger.error("💡 This might be a quota/rate limit issue")
            logger.error("💡 Try again in a few minutes or check your API quota")
        elif "network" in error_str or "connection" in error_str or "timeout" in error_str:
            logger.error("💡 This might be a network connectivity issue")
            logger.error("💡 Check your internet connection and firewall settings")
        elif "authentication" in error_str or "api key" in error_str or "unauthorized" in error_str:
            logger.error("💡 This might be an API key issue")
            logger.error("💡 Verify your GEMINI_API_KEY is correct and active")
        elif "invalid" in error_str and "model" in error_str:
            logger.error(f"💡 The model '{model_name}' might not be available")
            logger.error("💡 Try using 'gemini-2.5-flash' or 'gemini-1.5-pro'")
        else:
            logger.error("💡 This might be a temporary API issue")
            logger.error("💡 Try again in a few moments")
        
        raise

    # Extract the generated text and prepare detailed citations
    answer = response.text
    logger.info("✅ Answer generated successfully")
    
    # Create detailed citations with proper formatting
    citations_start = time.time()
    citations = []
    if source_details:
        logger.info(f"🔧 Preparing {len(source_details)} citations...")
        for detail in source_details:
            if detail['type'] == 'local_document':
                # Show actual document name
                doc_name = detail['source']
                citations.append(f"[{detail['number']}] {doc_name}")
            elif detail['type'] == 'web_search':
                # Format web sources as clickable markdown links
                title = detail['source']
                url = detail.get('url', detail.get('raw_source', ''))
                if url and url.startswith('http'):
                    citations.append(f"[{detail['number']}] [{title}]({url})")
                else:
                    citations.append(f"[{detail['number']}] {title}")
            else:
                citations.append(f"[{detail['number']}] {detail['source']}")
        citations_time = time.time() - citations_start
        logger.info(f"✅ Citations prepared in {citations_time:.2f}s")
    
    total_time = time.time() - total_start_time
    logger.info(f"🎉 Total answer generation completed in {total_time:.2f}s")
    
    return {
        "answer": answer, 
        "citations": citations,
        "source_details": source_details
    }
