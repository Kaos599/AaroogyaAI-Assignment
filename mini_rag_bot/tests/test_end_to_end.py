import unittest
import os
from unittest.mock import patch, MagicMock
from mini_rag_bot.src.app import main

class TestEndToEnd(unittest.TestCase):

    @patch('builtins.print')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('mini_rag_bot.src.retriever.Retriever.query')
    def test_pcos_symptoms_faq(self, mock_query, mock_parse_args, mock_print):
        """Test a sample FAQ on PCOS symptoms."""
        mock_parse_args.return_value = MagicMock(command='ask', question="What are the symptoms of PCOS?", lang='en')
        mock_query.return_value = []

        with patch('mini_rag_bot.src.app.generate_answer') as mock_generate_answer:
            mock_generate_answer.return_value = {
                "answer": "The symptoms of PCOS include irregular periods, excess androgen, and polycystic ovaries [source: 1].",
                "citations": ["[1] https://example.com/pcos"]
            }
            main()
            mock_print.assert_any_call("Answer:", "The symptoms of PCOS include irregular periods, excess androgen, and polycystic ovaries [source: 1].")

    @patch('builtins.print')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('mini_rag_bot.src.retriever.Retriever.query')
    def test_anemia_dietary_advice(self, mock_query, mock_parse_args, mock_print):
        """Test a sample FAQ on anemia dietary advice."""
        mock_parse_args.return_value = MagicMock(command='ask', question="What to eat for anemia?", lang='en')
        mock_query.return_value = []

        with patch('mini_rag_bot.src.app.generate_answer') as mock_generate_answer:
            mock_generate_answer.return_value = {
                "answer": "For anemia, it is recommended to eat iron-rich foods like spinach, red meat, and lentils [source: 1].",
                "citations": ["[1] https://example.com/anemia_diet"]
            }
            main()
            mock_print.assert_any_call("Answer:", "For anemia, it is recommended to eat iron-rich foods like spinach, red meat, and lentils [source: 1].")

    @patch('builtins.print')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('mini_rag_bot.src.retriever.Retriever.query')
    def test_menstrual_hygiene_hindi(self, mock_query, mock_parse_args, mock_print):
        """Test a sample FAQ on menstrual hygiene in Hindi."""
        mock_parse_args.return_value = MagicMock(command='ask', question="मासिक धर्म स्वच्छता प्रथाएं", lang='hi')
        mock_query.return_value = []

        with patch('mini_rag_bot.src.app.translate_to_english') as mock_translate_to_english, \
             patch('mini_rag_bot.src.app.translate_from_english') as mock_translate_from_english, \
             patch('mini_rag_bot.src.app.generate_answer') as mock_generate_answer:

            mock_translate_to_english.return_value = "menstrual hygiene practices"
            mock_generate_answer.return_value = {
                "answer": "Menstrual hygiene practices include using clean sanitary products and washing hands regularly [source: 1].",
                "citations": ["[1] https://example.com/menstrual_hygiene"]
            }
            mock_translate_from_english.return_value = "मासिक धर्म स्वच्छता प्रथाओं में स्वच्छ सैनिटरी उत्पादों का उपयोग करना और नियमित रूप से हाथ धोना शामिल है [स्रोत: 1]।"

            main()
            mock_print.assert_any_call("Answer:", "मासिक धर्म स्वच्छता प्रथाओं में स्वच्छ सैनिटरी उत्पादों का उपयोग करना और नियमित रूप से हाथ धोना शामिल है [स्रोत: 1]।" )

if __name__ == '__main__':
    unittest.main()
