from langchain_groq import ChatGroq
from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import json

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class TextExtractionAgent:
    """Extracts text from a document and sends it to an LLM for structured analysis."""

    def _init_(self, file_path="../data/srd.docx"):
        """Initialize the Text Extraction Agent."""
        self.file_path = file_path

        # Load and process the document
        self.documents = self.load_document()
        print(f"✅ Loaded {len(self.documents)} documents.")

        # Split document into smaller chunks
        self.text_chunks = self.split_texts()
        print(f"✅ Split document into {len(self.text_chunks)} chunks.")

        # Initialize Groq LLM (Llama3-8B)
        self.llm = ChatGroq(model_name="llama3-8b-8192", api_key=GROQ_API_KEY)

    def load_document(self):
        """Loads the .docx document and extracts text."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"⚠ Document not found: {self.file_path}")

        loader = Docx2txtLoader(self.file_path)
        return loader.load()

    def split_texts(self):
        """Splits the document into smaller chunks for better processing."""
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        return text_splitter.split_documents(self.documents)

    def retrieve_answer(self, query):
        """Sends the extracted text to the LLM and retrieves structured response in JSON format."""
        # Combine all chunks into a single document
        document_text = "\n\n".join([text.page_content for text in self.text_chunks])
        prompt = PromptTemplate.from_template(
                """You are an AI specializing in Software Requirements Specification (SRS) analysis.

                Extract the following structured information from the given document:
                - *UI Components* (e.g., buttons, modals, navigation bars, tiles).
                - *State Management Requirements* (e.g., session handling, API integration).
                - *API Endpoints* (including method, headers, parameters, response).
                - *User Roles & Permissions* (e.g., General Users vs. Managers).
                - *Styling & Branding Guidelines* (if applicable).

                The response *must* be in *valid JSON format*.

                Example JSON output:
                json
                {{
                    "UI_Components": ["Dashboard", "Leave Request Form", "Pods Management"],
                    "State_Management": ["NgRx", "Session Storage"],
                    "API_Endpoints": [
                        {{
                            "endpoint": "/api/lms/leaves/apply",
                            "method": "POST",
                            "headers": {{ "Authorization": "Bearer <token>" }},
                            "request_body": {{ "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "reason": "string" }},
                            "response": {{ "message": "Success", "status": "pending" }}
                        }}
                    ],
                    "User_Roles": {{
                        "General_User": ["Apply for leave", "View leave balance"],
                        "Manager": ["Approve/reject leave", "View team reports"]
                    }},
                    "Styling": {{
                        "Primary_Color": "#FF5733",
                        "Font": "Roboto"
                    }}
                }}
                

                Extract and return the details in this JSON format.
                
                Context: {document_text}

                *Strictly output only JSON. Do not add any extra text.*
                """
            )

        # Generate response using Groq LLM
        formatted_prompt = prompt.format(document_text=document_text)
        response = self.llm.invoke(formatted_prompt)

        # Ensure the output is in proper JSON format
        try:
            structured_output = json.loads(response.content.strip())  # Strip any whitespace
        except json.JSONDecodeError:
            structured_output = {
                "error": "Failed to parse response into JSON",
                "raw_response": response.content
            }

        return structured_output

# Test the Enhanced Agent
if _name_ == "_main_":
    agent = TextExtractionAgent()

    print("\n🔹 Extracted Structured Data from Groq:")
    extracted_data = agent.retrieve_answer("Extract UI and API details")
    print(json.dumps(extracted_data, indent=4)) 




# from langchain_groq import ChatGroq
# from langchain_community.document_loaders import Docx2txtLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.prompts import PromptTemplate
# from dotenv import load_dotenv
# import os
# import json

# load_dotenv()

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# class TextExtractionAgent:
#     """Extracts structured information from a Software Requirements Document (SRD) and returns it in JSON format."""

#     def _init_(self, file_path="../data/srd.docx", output_json="../data/extracted_data.json"):
#         """Initialize the Text Extraction Agent."""
#         self.file_path = file_path
#         self.output_json = output_json

#         # Load and process the document
#         self.documents = self.load_document()
#         print(f"✅ Loaded {len(self.documents)} documents.")

#         # Split document into smaller chunks
#         self.text_chunks = self.split_texts()
#         print(f"✅ Split document into {len(self.text_chunks)} chunks.")

#         # Initialize Groq LLM (Llama3-8B)
#         self.llm = ChatGroq(model_name="llama3-8b-8192", api_key=GROQ_API_KEY)

#     def load_document(self):
#         """Loads the .docx document and extracts text."""
#         if not os.path.exists(self.file_path):
#             raise FileNotFoundError(f"⚠ Document not found: {self.file_path}")

#         loader = Docx2txtLoader(self.file_path)
#         return loader.load()

#     def split_texts(self):
#         """Splits the document into smaller chunks for better processing."""
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
#         return text_splitter.split_documents(self.documents)

#     def retrieve_answer(self, query):
#         """Sends the extracted text to the LLM and retrieves a structured response in JSON format."""
#         # Combine all chunks into a single document
#         document_text = "\n\n".join([text.page_content for text in self.text_chunks])

#         # Define structured prompt for Groq LLM
#         prompt = PromptTemplate.from_template(
#             """You are an AI specializing in Software Requirements Specification (SRS) analysis.

#             Extract the following structured information from the given document:
#             - *UI/UX Guidelines* (Color Scheme, Typography, Component Design)
#             - *API Endpoints* (Endpoint URL, Method, Headers, Request/Response Body)
#             - *User Roles & Permissions* (RBAC, JWT Authentication details)
#             - *Authentication Details* (Login, Role-based Access Control)
#             - *Overall Features of Dashboard, LMS, and PODs*

#             The response *must* be in *valid JSON format*.

#             Example JSON output:
#             json
#             {{
#                 "UI_UX_Guidelines": {{
#                     "Color_Scheme": {{
#                         "Primary": "#007bff",
#                         "Secondary": "#6c757d",
#                         "Background": "#f8f9fa",
#                         "Success": "#28a745",
#                         "Error": "#dc3545"
#                     }},
#                     "Typography": {{
#                         "Font": "Inter",
#                         "Heading_Size": "24px",
#                         "Body_Size": "16px"
#                     }},
#                     "Components": ["Buttons", "Modals", "Cards", "Forms"]
#                 }},
#                 "API_Endpoints": [
#                     {{
#                         "endpoint": "/api/dashboard",
#                         "method": "GET",
#                         "headers": {{ "Authorization": "Bearer <token>" }},
#                         "response": {{
#                             "tiles": [
#                                 {{ "id": "1", "title": "Leave Summary", "content": "10 leaves remaining" }},
#                                 {{ "id": "2", "title": "Pod Members", "content": "3 active members" }}
#                             ]
#                         }}
#                     }},
#                     {{
#                         "endpoint": "/api/lms/leave/apply",
#                         "method": "POST",
#                         "headers": {{ "Authorization": "Bearer <token>" }},
#                         "request_body": {{ "startDate": "YYYY-MM-DD", "endDate": "YYYY-MM-DD", "reason": "string" }},
#                         "response": {{ "message": "Leave request submitted successfully", "status": "pending" }}
#                     }}
#                 ],
#                 "User_Roles": {{
#                     "General_User": ["Apply for leave", "View leave balance"],
#                     "Manager": ["Approve/reject leave", "View team reports"]
#                 }},
#                 "Authentication": {{
#                     "Login": {{
#                         "endpoint": "/api/auth/login",
#                         "method": "POST",
#                         "request_body": {{ "email": "user@example.com", "password": "securepassword" }},
#                         "response": {{ "token": "jwt-token-here", "user": {{ "id": "1", "role": "manager" }} }}
#                     }},
#                     "Fetch_User": {{
#                         "endpoint": "/api/auth/me",
#                         "method": "GET",
#                         "headers": {{ "Authorization": "Bearer <token>" }},
#                         "response": {{ "id": "1", "name": "John Doe", "role": "manager" }}
#                     }}
#                 }}
#             }}
#             

#             Extract and return the details in this JSON format.
            
#             Context: {document_text}

#             *Strictly output only JSON. Do not add any extra text.*
#             """
#         )

#         # Generate response using Groq LLM
#         formatted_prompt = prompt.format(document_text=document_text)
#         response = self.llm.invoke(formatted_prompt)

#         return self.clean_json_response(response.content)

#     def clean_json_response(self, raw_response):
#         """
#         Cleans and parses the extracted response into a properly formatted JSON.
#         - Handles cases where Groq returns an invalid JSON.
#         - Attempts to fix minor formatting issues.
#         - Ensures all fields are correctly structured.
#         """
#         try:
#             # First, try to directly parse it as JSON
#             structured_output = json.loads(raw_response.strip())
#         except json.JSONDecodeError:
#             print("⚠ JSON Parsing Error: Attempting to clean the response...")

#             # Remove unwanted text before/after JSON
#             raw_response = raw_response.strip().replace("\n", "").replace("\t", "")

#             # Attempt to find the first and last curly braces to extract JSON
#             start_index = raw_response.find("{")
#             end_index = raw_response.rfind("}")

#             if start_index != -1 and end_index != -1:
#                 json_string = raw_response[start_index:end_index + 1]
#                 try:
#                     structured_output = json.loads(json_string)
#                     print("✅ Successfully cleaned and parsed JSON.")
#                 except json.JSONDecodeError:
#                     structured_output = {"error": "Failed to clean JSON", "raw_response": raw_response}
#             else:
#                 structured_output = {"error": "No valid JSON found", "raw_response": raw_response}

#         # Save cleaned JSON to a file
#         with open(self.output_json, "w", encoding="utf-8") as json_file:
#             json.dump(structured_output, json_file, indent=4, ensure_ascii=False)
        
#         print(f"✅ Cleaned JSON saved to: {self.output_json}")

#         return structured_output

# # Test the Enhanced Agent
# if _name_ == "_main_":
#     agent = TextExtractionAgent()

#     print("\n🔹 Extracted and Cleaned Structured Data:")
#     extracted_data = agent.retrieve_answer("Extract UI and API details")
#     print(json.dumps(extracted_data, indent=4, ensure_ascii=False))





# # Import required modules
# from langchain_groq import ChatGroq
# from langchain_community.document_loaders import Docx2txtLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.prompts import PromptTemplate
# from dotenv import load_dotenv
# import os
# import json

# load_dotenv()

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# class TextExtractionAgent:
#     """Extracts structured data from an SRD document using Groq AI."""

#     def _init_(self, file_path="../data/srd.docx", output_path="../data/extracted_data.json"):
#         """Initialize the agent with the document path and output JSON path."""
#         self.file_path = file_path
#         self.output_path = output_path
#         self.llm = ChatGroq(model_name="llama3-8b-8192", api_key=GROQ_API_KEY)

#         # Load and process document
#         self.documents = self.load_document()
#         self.text_chunks = self.split_texts()

#     def load_document(self):
#         """Loads the .docx document and extracts text."""
#         if not os.path.exists(self.file_path):
#             raise FileNotFoundError(f"⚠ Document not found: {self.file_path}")

#         loader = Docx2txtLoader(self.file_path)
#         return loader.load()

#     def split_texts(self):
#         """Splits the document into smaller chunks for better processing."""
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
#         return text_splitter.split_documents(self.documents)

#     def extract_data(self):
#         """Extracts UI & API details from the document and saves as JSON."""
#         document_text = "\n\n".join([text.page_content for text in self.text_chunks])

#         # Define structured prompt for Groq LLM
#         prompt = PromptTemplate.from_template(
#             """You are an AI specializing in Software Requirements Specification (SRS) analysis.

#             Extract the following structured information from the given document:
#             - *UI Components* (e.g., buttons, modals, navigation bars, tiles).
#             - *State Management Requirements* (e.g., session handling, API integration).
#             - *API Endpoints* (including method, headers, parameters, response).
#             - *User Roles & Permissions* (e.g., General Users vs. Managers).
#             - *Styling & Branding Guidelines* (if applicable).

#             The response *must* be in *valid JSON format*.

#             Example JSON output:
#             json
#             {{
#                 "UI_Components": ["Dashboard", "Leave Request Form", "Pods Management"],
#                 "State_Management": ["NgRx", "Session Storage"],
#                 "API_Endpoints": [
#                     {{
#                         "endpoint": "/api/lms/leaves/apply",
#                         "method": "POST",
#                         "headers": {{ "Authorization": "Bearer <token>" }},
#                         "request_body": {{ "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "reason": "string" }},
#                         "response": {{ "message": "Success", "status": "pending" }}
#                     }}
#                 ],
#                 "User_Roles": {{
#                     "General_User": ["Apply for leave", "View leave balance"],
#                     "Manager": ["Approve/reject leave", "View team reports"]
#                 }},
#                 "Styling": {{
#                     "Primary_Color": "#FF5733",
#                     "Font": "Roboto"
#                 }}
#             }}
#             

#             Extract and return the details in this JSON format.

#             Context: {document_text}

#             *Strictly output only JSON. Do not add any extra text.*
#             """
#         )

#         # Generate response using Groq LLM
#         formatted_prompt = prompt.format(document_text=document_text)
#         response = self.llm.invoke(formatted_prompt)

#         # Ensure the output is in proper JSON format
#         try:
#             structured_output = json.loads(response.content.strip())
#             # Save extracted data to a JSON file
#             with open(self.output_path, "w") as f:
#                 json.dump(structured_output, f, indent=4)
#             print(f"✅ Extracted data saved to {self.output_path}")
#             return structured_output
#         except json.JSONDecodeError:
#             print("⚠ Failed to parse JSON response")
#             return {"error": "Failed to parse response into JSON", "raw_response": response.content}

# def text_extraction_node(state):
#     """LangGraph node function to extract structured data from SRD document."""
#     agent = TextExtractionAgent()
#     extracted_data = agent.extract_data()

#     # ✅ Ensure extracted_data is properly set
#     state["extracted_data"] = extracted_data
#     return state  # ✅ Return updated state dictionary
#  # ✅ Must return a dictionary