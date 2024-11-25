from typing import Optional, List
import tempfile
import requests
import json
import logging

logger = logging.getLogger(__name__)

def download_pdf(arxiv_id: str) -> Optional[str]:
        """
        Download PDF from arXiv
        
        Parameters:
            arxiv_id (str): arXiv ID extracted from the paper link
            
        Returns:
            str: Path to temporary PDF file
        """
        if "arxiv.org" in arxiv_id:
            arxiv_id = arxiv_id.split('/')[-1]
        
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        
        try:
            response = requests.get(pdf_url)
            response.raise_for_status()
            
            # Create temporary file
            temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_pdf.write(response.content)
            temp_pdf.close()
            
            return temp_pdf.name
        except Exception as e:
            print(f"Error downloading PDF: {e}")
            return None

def save_results(papers:List=[], path:str='../data/results.json'):
    """
    Save fetched papers to a text file
    
    Parameters:
        papers (list): List of paper dictionaries
    """
    logger.info(f"Saving {len(papers)} papers to results file")
    
    existing_papers = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            existing_papers = json.load(f)
            logger.debug(f"Loaded {len(existing_papers)} existing papers from file")
    except FileNotFoundError:
        logger.debug("No existing results file found, creating new")
    except json.JSONDecodeError:
        logger.warning("Existing results file is corrupted, starting fresh")
    
    all_papers = {paper['title']: paper for paper in existing_papers + papers}
    all_papers = list(all_papers.values())
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(all_papers, f, ensure_ascii=False, indent=4)
        logger.info(f"Successfully saved {len(all_papers)} papers to results file")
    except Exception as e:
        logger.error(f"Failed to save results: {e}", exc_info=True)
    
def display_papers(papers):
    """
    Display papers in a readable format
    
    Parameters:
        papers (list): List of paper dictionaries
    """
    logger.info(f"Displaying {len(papers)} papers")
    for i, paper in enumerate(papers, 1):
        print(f"\n{'-'*80}\nPaper {i}:")
        print(f"Title: {paper['title']}")
        print(f"Authors: {', '.join(paper['authors'])}")
        print(f"Published: {paper['published']}")
        print(f"Link: {paper['link']}")
        print(f"Primary Category: {paper['primary_category']}")
        print("\nAbstract:")
        print(paper['abstract'])

def save_summaries(paper_link: str, summary: str, insights: str, full_text: str, path:str='../data/summaries.json'):
    """
    Save summaries and insights to a JSON file
    """
    logger.info(f"Saving summaries for paper: {paper_link}")
    try:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                summaries = json.load(f)
                if not isinstance(summaries, dict):
                    logger.warning("Existing summaries file is not a dictionary, creating new")
        except (FileNotFoundError, json.JSONDecodeError):
            summaries = {}

        summaries[paper_link] = {
            'full_text': full_text,
            'summary': summary,
            'insights': insights
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(summaries, f, ensure_ascii=False, indent=4)
            
    except Exception as e:
        logger.error(f"Error saving summaries: {e}", exc_info=True)