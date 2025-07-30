# 🏥 Women's Health AI Assistant - Setup Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
python install_dependencies.py
```

### 2. Configure API Keys
Update your `.env` file with valid API keys:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
TAVILY_API_KEY=your_actual_tavily_api_key_here
```

**How to get API keys:**

#### Gemini API Key:
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it in your `.env` file

#### Tavily API Key (Optional - for web search):
1. Go to [Tavily](https://tavily.com/)
2. Sign up for an account
3. Get your API key from the dashboard
4. Add it to your `.env` file

### 3. Run the Application
```bash
streamlit run mini_rag_bot/src/app_streamlit.py
```

## 🔧 What's Fixed

### ✅ API Key Issues
- Enhanced error handling for invalid API keys
- Clear status indicators in the UI
- Graceful fallbacks when services are unavailable

### ✅ Translation System
- Replaced Google Translate with Gemini-based translation
- Support for Hindi, Bengali, and English
- More reliable translation service

### ✅ Deprecation Warnings
- Updated to use `langchain-huggingface` instead of deprecated embeddings
- Backward compatibility maintained

### ✅ Enhanced Prompts
- Specialized prompts for women's health
- Better context understanding
- Evidence-based response generation

### ✅ MCP Integration Ready
- Enhanced retriever with web search capabilities
- Context7 integration framework (ready for implementation)
- Tavily search with advanced options

## 🌟 New Features

### 🎯 Women's Health Specialization
- Focused on maternal and reproductive health
- Gender-specific health conditions
- Cultural and social health factors
- Evidence-based medical information

### 🌍 Multilingual Support
- English, Hindi, and Bengali support
- Gemini-powered translation
- Language detection and response translation

### 🔍 Enhanced Search
- Local vector store + web search combination
- Context-aware query enhancement
- Multiple source integration

### 📊 Better UI/UX
- System status indicators
- Sample questions
- Improved error messages
- Document upload progress

## 🧪 Testing

### Test the System
```bash
python test_rag_system.py
```

### Test Multilingual Features
```bash
python test_multilingual.py
```

### Test Specific Questions
```bash
python test_specific_questions.py
```

## 🔍 Troubleshooting

### Common Issues:

1. **"API key not valid" error**
   - Check your `.env` file has the correct Gemini API key
   - Ensure the key is not truncated or has extra spaces

2. **Translation errors**
   - The new Gemini-based translator should work better
   - If issues persist, check your Gemini API quota

3. **Embedding deprecation warnings**
   - Run `pip install -U langchain-huggingface`
   - The system will automatically use the new package

4. **Web search not working**
   - Check your Tavily API key
   - Web search is optional - the system will work without it

## 📚 Usage Examples

### English Questions:
- "What are the main health challenges faced by women?"
- "What are the key recommendations for maternal health?"

### Hindi Questions:
- "महिलाओं के स्वास्थ्य की मुख्य समस्याएं क्या हैं?"

### Bengali Questions:
- "মহিলাদের স্বাস্থ্যের জন্য কী সুপারিশ করা হয়েছে?"

## 🔮 Future Enhancements

- Context7 MCP full integration
- More language support
- Advanced health condition detection
- Integration with medical databases
- Voice input/output capabilities

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Ensure all dependencies are installed correctly
3. Verify your API keys are valid and have sufficient quota
4. Check the console output for detailed error messages