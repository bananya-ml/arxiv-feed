import os
import json
import logging

import google.generativeai as genai
from llama_parse import LlamaParse
from typing import Dict

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate

from dotenv import load_dotenv
load_dotenv()

import nest_asyncio
nest_asyncio.apply()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

logger = logging.getLogger(__name__)

class PaperSummarizer:
    def __init__(self, model_name: str = "gemini-1.5-flash-8b"):
        logger.info(f"Initializing PaperSummarizer with model: {model_name}")
        self.model_name = model_name
        self.parsing_instructions = ""
        self.parser = LlamaParse(result_type="markdown", parsing_instruction=self.parsing_instructions, show_progress=True)

        self.model = genai.GenerativeModel(self.model_name)
        logger.debug("PaperSummarizer initialization complete")

    def parse_pdf(self, pdf_path: str) -> Dict:
        """
        Parse PDF content using LlamaParse
        
        Parameters:
            pdf_path (str): Path to PDF file
            
        Returns:
            dict: Structured content from the PDF
        """
        logger.info(f"Starting PDF parsing: {pdf_path}")
        try:
            parsed_content = self.parser.load_data(pdf_path)
            logger.debug("PDF parsing successful")
            return parsed_content
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}", exc_info=True)
            return {}
        finally:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                logger.debug(f"Cleaned up temporary file: {pdf_path}")

    def generate_insights(self, content: Dict) -> str:
        logger.info("Starting insight generation")
        full_text = "\n\n".join([doc.text for doc in content])
        
        prompt = f"""Please summarize the paper by author(s) in one concise sentence. Then, list key insights and lessons learned from the paper. 
                    Next, generate 3-5 questions that you would like to ask the authors about their work. Finally, provide 3-5 suggestions for 
                    related topics or future research directions based on the content of the paper. If applicable, list at least 5 relevant 
                    references from the field of study of the paper. Here is the paper. If the last sentence provided is incomplete just ignore
                    it for summarizing: {full_text}"""

        try:
            response = self.model.generate_content(prompt)
            logger.debug("Successfully generated insights")
            return response.text
        except Exception as e:
            logger.error(f"Error generating insights: {e}", exc_info=True)
            return "Error generating insights"
        
    def generate_summary(self, content: Dict, recursive:bool=False) -> str:
        logger.info(f"Starting summary generation (recursive={recursive})")
        
        full_text = "\n\n".join([doc.text for doc in content])

        if recursive:
            logger.debug("Using recursive summarization approach")
            prompt_template = PromptTemplate.from_template("""Summarize a given document chunk clearly and succinctly.
                        Each input will be a part of a longer document, presented in chunks. Your goal is to summarize the content of each chunk in a way that maintains the overall meaning and ensures that important context is preserved for future summarization steps. Focus on capturing the core themes, essential details, and relevant points in each chunk, while avoiding redundancy.
                        Keep the summary short, highlight only the most crucial information, and avoid including minor details unless absolutely necessary for comprehension.

                        # Steps

                        1. **Read the Chunk Thoroughly**: Understand the content, context, and intent of the given document snippet.
                        2. **Identify Key Themes and Details**: Distill the primary subjects, essential arguments, and most significant points.
                        3. **Formulate a Summary**: Present these key themes clearly and concisely, capturing the core information of the given chunk.

                        # Output Format

                        - Provide the summary in 2-4 sentences.
                        - Make sure the summary is expressive enough that the next summarization step can understand the key aspects of the chunk.
                        - Avoid unnecessary details or overly verbose explanations.

                        # Examples

                        **Input:**
                        "[Document Chunk: The latest artificial intelligence techniques, particularly in machine learning, have resulted in notable advancements in areas such as language modeling, predictive analytics, and computer vision. Language models, specifically, show significant capability to understand and generate human-like text, while predictive analytics is being refined to improve decision-making processes in healthcare systems.]"

                        **Output:**
                        "The latest AI techniques, notably in machine learning, are enhancing language modeling, predictive analytics, and computer vision. Language models are advancing significantly in human-like text generation, and predictive analytics is becoming more effective within healthcare decision-making."

                        # Notes

                        - Avoid summarizing in a manner that removes important context necessary for understanding subsequent chunks.
                        - Make sure to use concise language that does not sacrifice content quality.
                        - If a chunk appears to be connected to previous content, ensure the summary remains coherent for eventual recursive summarization.
                        [Document chunk: {chunk}]""")
            
            text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=200,
            length_function=len,
            )
            
            chunks = text_splitter.split_text(full_text)
            logger.debug(f"Split text into {len(chunks)} chunks")
            
            summaries = []
            for i, chunk in enumerate(chunks, 1):
                logger.debug(f"Processing chunk {i}/{len(chunks)}")
                try:
                    response = self.model.generate_content(prompt)
                    summaries.append(response.text)
                except Exception as e:
                    logger.error(f"Error in first-level summarization: {e}", exc_info=True)
                    continue
            
            combined_summary = "\n\n".join(summaries)
            while len(combined_summary) > 4000:
                chunks = text_splitter.split_text(combined_summary)
                summaries = []
                for chunk in chunks:
                    # prompt = f"""Create a high-level summary of this text, preserving key concepts and relationships:
                    #             [Previous Summary Chunk: {chunk}]"""
                    prompt = prompt_template(chunk=chunk)
                    try:
                        response = self.model.generate_content(prompt)
                        summaries.append(response.text)
                    except Exception as e:
                        logger.error(f"Error in recursive summarization: {e}", exc_info=True)
                        continue
                combined_summary = "\n\n".join(summaries)
            
            return combined_summary

        else:
            logger.debug("Using single-pass summarization")
            prompt = f"""Please provide a comprehensive summary of this scientific paper:

                        Please structure the summary as follows:
                        1. Main objective and motivation
                        2. Key methods and approaches
                        3. Principal findings and results
                        4. Significance and implications

                        Keep the summary focused and technical but accessible to researchers in related fields.: {full_text}"""
            try:
                response = self.model.generate_content(prompt)
                logger.debug("Successfully generated summary")
                return response.text
            except Exception as e:
                logger.error(f"Error generating summary: {e}", exc_info=True)
                return "Error generating summary"

    def summarize_paper(self, parsed_content:str) -> str:
        """
        Main function to summarize a paper from its arXiv link
        
        Parameters:
            paper_link (str): arXiv link to the paper
            model_name (str): Name of the Ollama model to use
            
        Returns:
            str: Generated summary
        """
        
        summary = self.generate_summary(parsed_content, recursive=False)
        insights = self.generate_insights(parsed_content)
        
        return summary, insights

def save_summaries(paper_link: str, summary: str, insights: str):
    """
    """
    logger.info(f"Saving summaries for paper: {paper_link}")
    try:
        try:
            with open('./data/summaries.json', 'r', encoding='utf-8') as f:
                summaries = json.load(f)
                if not isinstance(summaries, dict):
                    logger.warning("Existing summaries file is not a dictionary, creating new")
        except (FileNotFoundError, json.JSONDecodeError):
            summaries = {}

        summaries[paper_link] = {
            'summary': summary,
            'insights': insights
        }

        with open('./data/summaries.json', 'w', encoding='utf-8') as f:
            json.dump(summaries, f, ensure_ascii=False, indent=4)
            
    except Exception as e:
        logger.error(f"Error saving summaries: {e}", exc_info=True)
    
 
# if __name__ == "__main__":
#     # import json
#     # with open('./data/results.json', 'r', encoding='utf-8') as f:
#     #         papers = json.load(f)
#     # for paper in papers:
#     #     paper_link = paper['link']
#     paper_link = "https://arxiv.org/abs/2311.12886"
#     summary, insights = summarize_paper(paper_link)
#     print("\nPaper Summary:")
#     print("-" * 80)
#     print(summary)
#     print("\nPaper Insights:")
#     print("-" * 80)
#     print(insights)
#     save_summaries(paper_link, summary, insights)