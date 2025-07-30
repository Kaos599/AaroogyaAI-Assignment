import streamlit as st
import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from tempfile import NamedTemporaryFile
from mini_rag_bot.src.loaders import load_pdf, load_html
from mini_rag_bot.src.splitter import split_text
from mini_rag_bot.src.vector_store import get_chroma_client, create_collection, add_documents_to_collection
from mini_rag_bot.src.embeddings import get_embedding_function
from mini_rag_bot.src.retriever import Retriever
from mini_rag_bot.src.generator import generate_answer
from mini_rag_bot.src.translator import translate_to_english, translate_from_english

# Initialize session state for uploaded files tracking
if "uploaded_files_info" not in st.session_state:
    st.session_state.uploaded_files_info = []

def check_api_keys():
    """Check if API keys are properly configured."""
    gemini_key = os.environ.get("GEMINI_API_KEY")
    tavily_key = os.environ.get("TAVILY_API_KEY")
    
    issues = []
    if not gemini_key or gemini_key == "dummy_key" or len(gemini_key) < 20:
        issues.append("❌ GEMINI_API_KEY is missing or invalid")
    else:
        issues.append("✅ GEMINI_API_KEY is configured")
    
    if not tavily_key or tavily_key == "dummy_key" or len(tavily_key) < 20:
        issues.append("⚠️ TAVILY_API_KEY is missing (web search will be disabled)")
    else:
        issues.append("✅ TAVILY_API_KEY is configured")
    
    return issues

def main():
    st.set_page_config(
        page_title="Women's Health AI Assistant", 
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("🏥 Women's Health AI Assistant")
    st.markdown("*Specialized AI assistant for women's health questions with evidence-based responses*")

    # Check API configuration
    with st.sidebar:
        st.header("🔧 System Status")
        api_status = check_api_keys()
        for status in api_status:
            st.write(status)
        
        st.header("📚 Document Management")
        uploaded_files = st.file_uploader(
            "Upload PDF or HTML files", 
            accept_multiple_files=True, 
            type=['pdf', 'html'],
            help="Upload documents related to women's health for better context"
        )
        
        if st.button("📥 Ingest Documents", type="primary"):
            if uploaded_files:
                # Create a status container for detailed progress tracking
                with st.status("Processing documents...", expanded=True) as status:
                    try:
                        total_chunks = 0
                        processed_files = []
                        
                        for file_idx, uploaded_file in enumerate(uploaded_files):
                            st.write(f"📄 Processing file {file_idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
                            
                            # Save uploaded file temporarily
                            with NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.type.split('/')[1]}") as tmp_file:
                                tmp_file.write(uploaded_file.getvalue())
                                tmp_file_path = tmp_file.name
                            
                            st.write("✅ File uploaded successfully")

                            # Load document based on type
                            if uploaded_file.type == "application/pdf":
                                st.write("🔧 Loading PDF document...")
                                documents = load_pdf(tmp_file_path)
                                st.write(f"✅ Loaded {len(documents)} pages from PDF")
                            else:
                                st.write("🔧 Loading HTML document...")
                                with open(tmp_file_path, 'r', encoding='utf-8') as f:
                                    html_content = f.read()
                                documents = load_html(f"file://{tmp_file_path}")
                                st.write(f"✅ Loaded HTML document")

                            # Split into chunks
                            st.write("🔧 Splitting document into chunks...")
                            chunks = split_text(documents)
                            st.write(f"✅ Created {len(chunks)} text chunks")
                            
                            # Add metadata to chunks for proper citation
                            for chunk in chunks:
                                chunk.metadata['source'] = uploaded_file.name
                                chunk.metadata['file_type'] = uploaded_file.type
                            
                            # Initialize vector store components
                            st.write("🔧 Initializing vector store...")
                            client = get_chroma_client()
                            collection = create_collection(client)
                            embedding_function = get_embedding_function()
                            
                            # Add documents to collection
                            st.write("🔧 Adding documents to vector store...")
                            add_documents_to_collection(collection, chunks, embedding_function)
                            st.write("✅ Documents added to vector store")
                            
                            # Clean up temporary file
                            os.remove(tmp_file_path)
                            
                            # Track processed file info
                            file_info = {
                                'name': uploaded_file.name,
                                'type': uploaded_file.type,
                                'chunks': len(chunks),
                                'pages': len(documents) if uploaded_file.type == "application/pdf" else 1
                            }
                            processed_files.append(file_info)
                            total_chunks += len(chunks)
                        
                        # Update session state with file information
                        st.session_state.uploaded_files_info.extend(processed_files)
                        
                        # Update status to complete
                        status.update(
                            label=f"✅ Successfully processed {len(uploaded_files)} document(s)!",
                            state="complete"
                        )
                        
                        # Show summary
                        st.success(f"🎉 Processing Complete!")
                        st.info(f"📊 **Summary:**\n- Files processed: {len(uploaded_files)}\n- Total chunks created: {total_chunks}\n- Documents ready for querying!")
                        
                    except Exception as e:
                        status.update(
                            label=f"❌ Error processing documents: {str(e)}",
                            state="error"
                        )
                        st.error(f"❌ Error details: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
            else:
                st.warning("Please upload at least one file.")
        
        # Show uploaded files information
        if st.session_state.uploaded_files_info:
            st.header("📚 Uploaded Documents")
            for file_info in st.session_state.uploaded_files_info:
                with st.expander(f"📄 {file_info['name']}", expanded=False):
                    st.write(f"**Type:** {file_info['type']}")
                    if file_info['type'] == "application/pdf":
                        st.write(f"**Pages:** {file_info['pages']}")
                    st.write(f"**Text chunks:** {file_info['chunks']}")
            
            if st.button("🗑️ Clear All Documents", type="secondary"):
                st.session_state.uploaded_files_info = []
                st.rerun()
        
        st.header("🌍 Language Support")
        language = st.selectbox(
            "Select your language:",
            ["English", "Hindi (हिंदी)", "Bengali (বাংলা)"],
            help="Ask questions in your preferred language"
        )

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about women's health..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message("assistant"):
            # Create a status container for detailed progress tracking
            with st.status("Processing your question...", expanded=True) as status:
                try:
                    # Step 1: Language detection and translation
                    original_prompt = prompt
                    if language == "Hindi (हिंदी)":
                        st.write("🔧 Translating from Hindi to English...")
                        prompt = translate_to_english(prompt, "hi")
                        st.write("✅ Translation completed")
                    elif language == "Bengali (বাংলা)":
                        st.write("🔧 Translating from Bengali to English...")
                        prompt = translate_to_english(prompt, "bn")
                        st.write("✅ Translation completed")
                    
                    # Step 2: Initialize retriever and search for context
                    st.write("🔧 Initializing retrieval system...")
                    retriever = Retriever()
                    st.write("✅ Retrieval system ready")
                    
                    st.write("🔍 Searching for relevant information...")
                    context_docs = retriever.query(prompt)
                    
                    if not context_docs:
                        st.write("⚠️ No relevant documents found")
                        status.update(
                            label="⚠️ No relevant information found",
                            state="complete"
                        )
                        response = "I apologize, but I couldn't find relevant information to answer your question. Please try rephrasing your question or upload relevant documents."
                    else:
                        st.write(f"✅ Found {len(context_docs)} relevant sources")
                        
                        # Step 3: Generate answer
                        st.write("🔧 Generating comprehensive answer...")
                        result = generate_answer(context_docs, prompt)
                        answer = result['answer']
                        st.write("✅ Answer generated successfully")
                        
                        # Step 4: Translate back if needed
                        if language == "Hindi (हिंदी)":
                            st.write("🔧 Translating answer to Hindi...")
                            answer = translate_from_english(answer, "hi")
                            st.write("✅ Translation completed")
                        elif language == "Bengali (বাংলা)":
                            st.write("🔧 Translating answer to Bengali...")
                            answer = translate_from_english(answer, "bn")
                            st.write("✅ Translation completed")
                        
                        status.update(
                            label="✅ Answer ready with citations",
                            state="complete"
                        )
                        
                        # Format response with proper citations
                        response = answer
                        
                        # Display citations in a nice format
                        if result.get('citations'):
                            st.markdown("---")
                            st.markdown("### 📚 Sources and Citations")
                            
                            for i, citation in enumerate(result['citations'], 1):
                                # Parse citation to extract number and content
                                if citation.startswith('[') and ']' in citation:
                                    # Extract the content after the number
                                    content = citation.split('] ', 1)[1] if '] ' in citation else citation
                                    
                                    # Check if it's a markdown link (web source)
                                    if content.startswith('[') and '](' in content and content.endswith(')'):
                                        # It's a markdown link - display it directly
                                        st.markdown(f"**{i}.** 🌐 {content}")
                                    elif 'http' in content:
                                        # It's a URL but not formatted as markdown
                                        st.markdown(f"**{i}.** 🌐 {content}")
                                    elif '.pdf' in content.lower() or 'PDF' in content:
                                        # PDF document
                                        st.markdown(f"**{i}.** 📄 {content}")
                                    else:
                                        # Other document
                                        st.markdown(f"**{i}.** 📋 {content}")
                                else:
                                    st.markdown(f"**{i}.** 📋 {citation}")
                            
                            # Show source details if available
                            if result.get('source_details'):
                                with st.expander("🔍 View Source Details", expanded=False):
                                    for detail in result['source_details']:
                                        st.markdown(f"**Source {detail['number']}:** {detail['source']}")
                                        st.markdown(f"*Type:* {detail['type']}")
                                        if detail.get('url'):
                                            st.markdown(f"*URL:* {detail['url']}")
                                        st.markdown(f"*Preview:* {detail['content_preview']}")
                                        st.markdown("---")
                    
                except Exception as e:
                    status.update(
                        label=f"❌ Error processing question",
                        state="error"
                    )
                    error_msg = f"❌ I encountered an error while processing your question: {str(e)}"
                    if "API key not valid" in str(e):
                        error_msg += "\n\n🔧 **Solution**: Please check your GEMINI_API_KEY in the .env file."
                    elif "TAVILY_API_KEY" in str(e):
                        error_msg += "\n\n🔧 **Note**: Web search is disabled. Only local documents will be used."
                    st.error(error_msg)
                    response = error_msg
            
            # Display the main answer outside the status container
            if 'response' in locals() and not response.startswith("❌"):
                st.markdown("### 💬 Answer")
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Sample questions
    if not st.session_state.messages:
        st.markdown("### 💡 Sample Questions:")
        sample_questions = [
            "What are the main health challenges faced by women?",
            "What are the key recommendations for maternal health?",
            "How can women maintain reproductive health?",
            "What are the signs of hormonal imbalances in women?"
        ]
        
        cols = st.columns(2)
        for i, question in enumerate(sample_questions):
            with cols[i % 2]:
                if st.button(question, key=f"sample_{i}"):
                    st.session_state.messages.append({"role": "user", "content": question})
                    st.rerun()

if __name__ == "__main__":
    main()
