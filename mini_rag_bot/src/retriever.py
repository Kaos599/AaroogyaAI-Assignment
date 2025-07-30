import os
from .vector_store import get_chroma_client, create_collection
from .embeddings import get_embedding_function
from langchain_tavily import TavilySearch
from langchain.docstore.document import Document

class Retriever:
    def __init__(self, collection_name="women_health"):
        print("🔧 Initializing Retriever...")
        self.client = get_chroma_client()
        self.collection = create_collection(self.client, collection_name)
        self.embedding_function = get_embedding_function()
        
        # Initialize Tavily search with better error handling
        tavily_api_key = os.environ.get("TAVILY_API_KEY")
        if tavily_api_key and tavily_api_key != "dummy_key" and len(tavily_api_key) > 10:
            try:
                print("🔧 Initializing Tavily search...")
                self.tavily = TavilySearch(
                    api_key=tavily_api_key, 
                    max_results=3, 
                    include_answer=True,
                    search_depth="advanced"
                )
                self.tavily_available = True
                print("✅ Tavily search initialized successfully")
            except Exception as e:
                print(f"⚠️ Tavily search not available: {e}")
                self.tavily_available = False
        else:
            print("⚠️ TAVILY_API_KEY not set or invalid - web search disabled")
            self.tavily_available = False
        
        print("✅ Retriever initialized successfully")

    def query(self, query_text, n_results=5):
        """Enhanced query with women's health focus and proper citation tracking."""
        print(f"🔍 Processing query: '{query_text}'")
        documents = []
        
        # Step 1: Query local vector store
        print("🔧 Searching local knowledge base...")
        try:
            query_embedding = self.embedding_function.embed_query(query_text)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            if results['documents'] and results['documents'][0]:
                local_docs_found = len([doc for doc in results['documents'][0] if doc.strip()])
                print(f"✅ Found {local_docs_found} relevant documents in local knowledge base")
                
                for i, doc in enumerate(results['documents'][0]):
                    if doc.strip():  # Only add non-empty documents
                        # Extract original metadata if available
                        original_metadata = results['metadatas'][0][i] if results.get('metadatas') and results['metadatas'][0] else {}
                        
                        # Get the original source name, preserving file names
                        source_name = original_metadata.get('source', f'Local Document {i+1}')
                        
                        # Clean up source names to show actual document names
                        if source_name and source_name != f'Local Document {i+1}':
                            # Keep the original source name as is (e.g., "C. Women and health.pdf")
                            pass
                        else:
                            # Fallback to a more descriptive name
                            if original_metadata.get('file_type') == 'application/pdf':
                                source_name = f"PDF Document (Chunk {original_metadata.get('chunk_id', i+1)})"
                            else:
                                source_name = f"Document {i+1}"
                        
                        documents.append(Document(
                            page_content=doc, 
                            metadata={
                                'source': source_name,
                                'source_type': 'local_document',
                                'score': results['distances'][0][i] if results.get('distances') else 0.0,
                                'chunk_id': i,
                                'original_metadata': original_metadata
                            }
                        ))
            else:
                print("⚠️ No relevant documents found in local knowledge base")
        except Exception as e:
            print(f"❌ Error querying local vector store: {e}")

        # Step 2: Enhance query for women's health context
        enhanced_query = self._enhance_query_for_womens_health(query_text)
        
        # Step 3: Always use Tavily search for additional context if available
        if self.tavily_available:
            print("🔧 Searching web for additional context...")
            try:
                # Use the correct method for Tavily search
                tavily_response = self.tavily.invoke(enhanced_query)
                
                # Handle the response format - Tavily returns a dict with 'results' key
                if isinstance(tavily_response, dict) and 'results' in tavily_response:
                    tavily_results = tavily_response['results']
                    results_to_process = tavily_results[:3]  # Limit to 3 results
                    web_results_count = len(results_to_process)
                    print(f"✅ Found {web_results_count} relevant web results")
                    
                    for i, res in enumerate(results_to_process):
                        if isinstance(res, dict) and 'content' in res:
                            documents.append(Document(
                                page_content=res['content'], 
                                metadata={
                                    'source': res.get('url', 'Unknown URL'),
                                    'title': res.get('title', 'Web Result'),
                                    'source_type': 'web_search',
                                    'search_engine': 'Tavily'
                                }
                            ))
                elif isinstance(tavily_response, list):
                    # Fallback for list format
                    results_to_process = tavily_response[:3]
                    web_results_count = len(results_to_process)
                    print(f"✅ Found {web_results_count} relevant web results")
                    
                    for i, res in enumerate(results_to_process):
                        if isinstance(res, dict) and 'content' in res:
                            documents.append(Document(
                                page_content=res['content'], 
                                metadata={
                                    'source': res.get('url', 'Unknown URL'),
                                    'title': res.get('title', 'Web Result'),
                                    'source_type': 'web_search',
                                    'search_engine': 'Tavily'
                                }
                            ))
                else:
                    print(f"⚠️ Unexpected Tavily response format: {type(tavily_response)}")
                    
            except Exception as e:
                print(f"⚠️ Web search failed: {e}")
        else:
            print("⚠️ Web search not available - using only local knowledge base")

        # Step 4: If still insufficient results, try Context7 MCP (if available)
        if len(documents) < 2:
            print("🔧 Attempting to find additional context...")
            context7_docs = self._try_context7_search(enhanced_query)
            documents.extend(context7_docs)

        # Ensure we have a mix of local and web sources
        local_docs = [doc for doc in documents if doc.metadata.get('source_type') == 'local_document']
        web_docs = [doc for doc in documents if doc.metadata.get('source_type') == 'web_search']
        
        print(f"📊 Retrieved {len(local_docs)} local documents and {len(web_docs)} web documents")
        
        # Return a balanced mix, prioritizing local but including web sources
        final_documents = []
        
        # Add local documents first (up to 3)
        final_documents.extend(local_docs[:3])
        
        # Add web documents to fill remaining slots
        remaining_slots = n_results - len(final_documents)
        if remaining_slots > 0 and web_docs:
            final_documents.extend(web_docs[:remaining_slots])
        
        # If we still have slots and more local docs, add them
        remaining_slots = n_results - len(final_documents)
        if remaining_slots > 0 and len(local_docs) > 3:
            final_documents.extend(local_docs[3:3+remaining_slots])
        
        final_count = len(final_documents)
        print(f"✅ Query completed - returning {final_count} documents ({len([d for d in final_documents if d.metadata.get('source_type') == 'local_document'])} local, {len([d for d in final_documents if d.metadata.get('source_type') == 'web_search'])} web)")
        return final_documents

    def _enhance_query_for_womens_health(self, query_text):
        """Enhance query with women's health context."""
        womens_health_terms = [
            "women's health", "maternal health", "reproductive health", 
            "gynecological", "pregnancy", "menstrual", "breast health",
            "cervical health", "hormonal health", "menopause"
        ]
        
        # Check if query already contains women's health terms
        query_lower = query_text.lower()
        has_womens_health_context = any(term in query_lower for term in womens_health_terms)
        
        if not has_womens_health_context:
            return f"women's health {query_text}"
        return query_text

    def _needs_current_info(self, query_text):
        """Check if query needs current/recent information."""
        current_info_indicators = [
            "latest", "recent", "current", "new", "2024", "2023", 
            "guidelines", "recommendations", "statistics", "data"
        ]
        return any(indicator in query_text.lower() for indicator in current_info_indicators)

    def _try_context7_search(self, query_text):
        """Try to get information from Context7 MCP if available."""
        documents = []
        try:
            # This would be implemented if Context7 MCP is available
            # For now, return empty list
            pass
        except Exception as e:
            print(f"Context7 search not available: {e}")
        
        return documents
