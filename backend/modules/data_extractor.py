import google.generativeai as genai
import os
import re
from typing import Dict
import logging

from langchain.prompts import PromptTemplate

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY not found in environment variables")
    raise ValueError("GOOGLE_API_KEY is required")

genai.configure(api_key=GOOGLE_API_KEY)

model_name = "gemini-1.5-flash-8b"
model = genai.GenerativeModel(model_name)
logger.info(f"Initialized Gemini model: {model_name}")

def _find_conclusion(content: str) -> str:
    """Extract conclusions from research paper content."""
    logger.info("Starting conclusion extraction")
    
    try:
        prompt_template = PromptTemplate.from_template("""Extract the conclusions or results section from a provided research paper in the field of astronomy or astrophysics.

                                                    Ignore section titles or headings while focusing on the main conclusion of the study. The extracted text should be represented clearly, emphasizing the results and implications presented in the paper, without repetition or unnecessary information.

                                                    # Steps

                                                    1. **Parse the research paper**: Identify different sections, focusing particularly on introduction, methods, results, and conclusions. Give most attention to sections conveying results or analysis.
                                                    2. **Detect the conclusions/results section**: Locate the text that is presented as the primary findings and implications of the paper.
                                                    3. **Summarize, if necessary**: If the conclusions or findings are lengthy or overly detailed, condense them logically without omitting essential information. The emphasis should be on clarity and complete presence of the main results.

                                                    # Output Format

                                                    Provide the conclusions or results as a clear, concise paragraph(s) directly extracted from the research article. Avoid any text that introduces or titles the conclusions, such as "Conclusion", "Results", etc. Ensure to maintain the language integrity without restructuring unless necessary for clarity. 

                                                    # Notes

                                                    - The summarization, if needed, should not distort the scientific meaning or create ambiguity about the findings.
                                                    - Focus only on the scientific implications, avoiding acknowledgments, funding information, or unrelated discussion comments.
                                                    [Research paper:{content}]""")

        prompt = prompt_template.format(content=content)
        logger.debug("Generated prompt for conclusion extraction")
        
        response = model.generate_content(prompt)
        logger.debug("Successfully received response from Gemini")
        
        return response.text
    except Exception as e:
        logger.error(f"Error extracting conclusion: {e}", exc_info=True)
        return ""

def extract_metadata(parsed_content: Dict) -> Dict:
    """Extract metadata from parsed paper content."""
    logger.info("Starting metadata extraction")
    
    try:
        content = '\n\n'.join([doc.text for doc in parsed_content])
        logger.debug("Combined parsed content for processing")
        
        conclusion = _find_conclusion(content)
        if not conclusion:
            logger.warning("No conclusion was extracted")
        
        ref_patterns = [
            r'\[\d+\]',
            r'\(\w+\s*(?:et\s+al\.?)?\s*,\s*\d{4}\w?\)',
            r'(?<!\w)(?:20)\d{2}[a-z]?(?!\d)'
        ]
        
        ref_count = 0
        for pattern in ref_patterns:
            refs = re.findall(pattern, content)
            ref_count = max(ref_count, len(set(refs)))
        
        logger.debug(f"Found {ref_count} references")
        
        metadata = {
            'conclusion': conclusion,
            'ref_count': ref_count
        }
        
        logger.info("Successfully extracted metadata")
        return metadata
        
    except Exception as e:
        logger.error(f"Error extracting metadata: {e}", exc_info=True)
        return {
            'conclusion': '',
            'ref_count': 0
        }