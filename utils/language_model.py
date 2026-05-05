#Version :01

# import os
# import logging
# from dotenv import load_dotenv
# from anthropic import Anthropic
# from utils.prompt import SYSTEM_MESSAGE

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# # Load environment variables
# load_dotenv()

# class LanguageModel:
#     def __init__(self):
#         self.client = self._get_claude_client()
#         self.model = "claude-3-7-sonnet-20250219"

#     def _get_claude_client(self):
#         api_key = os.getenv("ANTHROPIC_API_KEY")
#         if not api_key:
#             error_msg = "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable."
#             logger.error(error_msg)
#             raise ValueError(error_msg)
#         return Anthropic(api_key=api_key)

#     def count_tokens(self, messages):
#         try:
#             response = self.client.messages.count_tokens(
#                 model=self.model,
#                 system=SYSTEM_MESSAGE,
#                 messages=messages
#             )
#             return response.input_tokens
#         except Exception as e:
#             logger.error(f"Error counting tokens: {e}")
#             return None

#     def ask_question(self, question, context, max_tokens=1000):
#         user_message = {
#             "role": "user",
#             "content": f"""
# I need information from some architectural documents.

# Context information:
# {context}

# Question: {question}

# Please provide a detailed and accurate answer based solely on the context provided.
# """
#         }

#         messages = [user_message]
#         token_count = self.count_tokens(messages)

#         try:
#             response = self.client.messages.create(
#                 model=self.model,
#                 max_tokens=max_tokens,
#                 system=SYSTEM_MESSAGE,
#                 messages=messages
#             )

#             answer = response.content[0].text
#             output_tokens = response.usage.output_tokens

#             return {
#                 "answer": answer,
#                 "input_tokens": token_count,
#                 "output_tokens": output_tokens
#             }
#         except Exception as e:
#             logger.error(f"Error in language model API call: {e}")
#             return {
#                 "answer": f"Sorry, an error occurred: {str(e)}",
#                 "input_tokens": token_count,
#                 "output_tokens": None
#             }

#     def search_and_answer(self, question, similar_docs, max_tokens=1000):
#         combined_context = "\n\n".join([doc.page_content for doc in similar_docs])
#         return self.ask_question(question, combined_context, max_tokens=max_tokens)

#Version :02
# import os
# import logging
# import re
# from dotenv import load_dotenv
# from anthropic import Anthropic
# from utils.prompt import SYSTEM_MESSAGE

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# # Load environment variables
# load_dotenv()

# class LanguageModel:
#     def __init__(self):
#         self.client = self._get_claude_client()
#         self.model = "claude-3-7-sonnet-20250219"

#     def _get_claude_client(self):
#         api_key = os.getenv("ANTHROPIC_API_KEY")
#         if not api_key:
#             error_msg = "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable."
#             logger.error(error_msg)
#             raise ValueError(error_msg)
#         return Anthropic(api_key=api_key)

#     def count_tokens(self, messages):
#         try:
#             response = self.client.messages.count_tokens(
#                 model=self.model,
#                 system=SYSTEM_MESSAGE,
#                 messages=messages
#             )
#             return response.input_tokens
#         except Exception as e:
#             logger.error(f"Error counting tokens: {e}")
#             return None

#     def post_process_response(self, text):
#         """
#         Clean up the response to make it more suitable for display
#         - Fix table formatting
#         - Remove escape characters
#         - Ensure proper markdown structure
#         """
#         # Replace any table with a properly formatted one
#         # Match markdown tables and ensure they have proper formatting
#         table_pattern = r"(\|\s*(.+?)\s*\|\s*\n\|[-:|\s]+\|\s*\n)((.*\|\s*\n)+)"
        
#         def fix_table(match):
#             header = match.group(1)
#             rows = match.group(3)
            
#             # Clean up the header
#             clean_header = re.sub(r'\s{2,}', ' ', header)
            
#             # Clean up the rows
#             clean_rows = ""
#             for row in rows.strip().split('\n'):
#                 clean_row = re.sub(r'\s{2,}', ' ', row)
#                 clean_rows += clean_row + "\n"
                
#             return clean_header + clean_rows
        
#         processed_text = re.sub(table_pattern, fix_table, text)
        
#         # Remove any \n characters that are visible in the text
#         processed_text = processed_text.replace('\\n', '')
        
#         # Ensure proper spacing after headers
#         processed_text = re.sub(r'(#{1,6}\s.+?)(\n)(?!\n)', r'\1\n\n', processed_text)
        
#         return processed_text

#     def ask_question(self, question, context, max_tokens=1000):
#         user_message = {
#             "role": "user",
#             "content": f"""
#     I need information from some architectural documents.

#     Context information:
#     {context}

#     Question: {question}

#     Please provide a detailed and accurate answer based solely on the context provided.
#     """
#         }

#         messages = [user_message]
#         token_count = self.count_tokens(messages)

#         try:
#             response = self.client.messages.create(
#                 model=self.model,
#                 max_tokens=max_tokens,
#                 system=SYSTEM_MESSAGE,
#                 messages=messages
#             )

#             # Access the tokens directly from the response object (don't use .get())
#             answer = response.content[0].text
            
#             # Post-process the answer to clean up formatting
#             processed_answer = self.post_process_response(answer)
            
#             input_tokens = response.usage.input_tokens  
#             output_tokens = response.usage.output_tokens  

#             return {
#                 "answer": processed_answer,
#                 "input_tokens": input_tokens,
#                 "output_tokens": output_tokens
#             }
#         except Exception as e:
#             logger.error(f"Error in language model API call: {e}")
#             return {
#                 "answer": f"Sorry, an error occurred: {str(e)}",
#                 "input_tokens": token_count,
#                 "output_tokens": None
#             }


#     def search_and_answer(self, question, similar_docs, max_tokens=1000):
#         combined_context = "\n\n".join([doc.page_content for doc in similar_docs])
#         return self.ask_question(question, combined_context, max_tokens=max_tokens)

import os
import logging
import re
from dotenv import load_dotenv
from anthropic import Anthropic
from utils.prompt import SYSTEM_MESSAGE

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class LanguageModel:
    def __init__(self):
        self.client = self._get_claude_client()
        self.model = "claude-3-7-sonnet-20250219"

    def _get_claude_client(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            error_msg = "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable."
            logger.error(error_msg)
            raise ValueError(error_msg)
        return Anthropic(api_key=api_key)

    def count_tokens(self, messages):
        try:
            response = self.client.messages.count_tokens(
                model=self.model,
                system=SYSTEM_MESSAGE,
                messages=messages
            )
            return response.input_tokens
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            return None

    def post_process_response(self, text):
        """
        Post-process the response to ensure clean markdown formatting:
        - Fix markdown tables alignment and spacing.
        - Remove unwanted escape characters.
        - Ensure proper markdown headings and lists formatting.
        """

        # Correct markdown tables
        def fix_markdown_tables(text):
            table_regex = re.compile(r'(?:\|.*?\|.*?\|\n)+', re.MULTILINE)
            tables = table_regex.findall(text)
            for table in tables:
                lines = [line.strip() for line in table.strip().split('\n')]
                header = lines[0]
                separator = '|'.join(['---' for _ in header.split('|') if _]) 
                rows = lines[1:]
                clean_table = [header, separator] + rows
                formatted_table = '\n'.join(clean_table)
                text = text.replace(table, formatted_table)
            return text

        # Remove visible escape characters
        text = text.replace('\\n', '').replace('\\', '')

        # Ensure proper spacing after markdown headings
        text = re.sub(r'(#{1,6} .+)(?=\S)', r'\1\n\n', text)

        # Correct markdown table formatting
        text = fix_markdown_tables(text)

        # Ensure lists are properly spaced
        text = re.sub(r'(\n- .+)(?=\S)', r'\1\n', text)

        return text.strip()

    def ask_question(self, question, context, max_tokens=1000):
        user_message = {
            "role": "user",
            "content": f"""
You are provided with architectural document excerpts. Use this context carefully to answer the user's question.

### Context Information:
{context}

### Question:
{question}

### Answer Instructions:
- Answer immediately with relevant and accurate information.
- Clearly differentiate and properly format structured data (like tables, lists, legal descriptions) in markdown.
- Explicitly mention page numbers and document sections if provided in the context.
- Do not fabricate information—if insufficient data is present, clearly state: "I don't have enough information to answer this question."

### Your Answer:
"""
        }

        messages = [user_message]
        token_count = self.count_tokens(messages)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=SYSTEM_MESSAGE,
                messages=messages
            )

            answer = response.content[0].text

            # Improved post-processing of markdown response
            processed_answer = self.post_process_response(answer)

            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            return {
                "answer": processed_answer,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens
            }
        except Exception as e:
            logger.error(f"Error in language model API call: {e}")
            return {
                "answer": f"Sorry, an error occurred: {str(e)}",
                "input_tokens": token_count,
                "output_tokens": None
            }

    def search_and_answer(self, question, similar_docs, max_tokens=1000):
        combined_context_parts = []
        for doc in similar_docs:
            page_number = doc.metadata.get("page_number", "Unknown")
            content = doc.page_content
            combined_context_parts.append(f"(Page {page_number})\n{content}")

        combined_context = "\n\n".join(combined_context_parts)

        return self.ask_question(question, combined_context, max_tokens=max_tokens)
