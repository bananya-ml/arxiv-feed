import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def get_papers(max_results: int = 10, category: str = "astro-ph.SR"):
    """
    Fetch recent papers from arXiv based on the specified category.
    
    Parameters:
        max_results (int): Maximum number of results to return
        category (str): Category of papers to fetch (default is 'astro-ph.SR')
        
    Returns:
        list: List of dictionaries containing paper information
    """
    logger.info(f"Fetching {max_results} papers from arXiv category: {category}")
    
    # Base API URL
    base_url = 'http://export.arxiv.org/api/query?'
    
    search_query = f'cat:{category}'  # Use the category parameter
    
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    query_params = {
        'search_query': search_query,
        'max_results': max_results,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    
    encoded_params = urllib.parse.urlencode(query_params)
    url = base_url + encoded_params
    logger.debug(f"Making request to arXiv API: {url}")
    
    try:
        with urllib.request.urlopen(url) as response:
            response_data = response.read()
        logger.debug("Successfully received response from arXiv")
        
        root = ET.fromstring(response_data)
        
        namespace = {'atom': 'http://www.w3.org/2005/Atom',
                    'arxiv': 'http://arxiv.org/schemas/atom'}

        papers = []
        entries = root.findall('atom:entry', namespace)
        logger.debug(f"Found {len(entries)} entries in XML response")
        
        for entry in entries:
            try:
                paper = {
                    'id': entry.find('atom:id', namespace).text,
                    'title': entry.find('atom:title', namespace).text.strip().replace('\n', ' '),
                    'authors': [author.find('atom:name', namespace).text for author in entry.findall('atom:author', namespace)],
                    'published': entry.find('atom:published', namespace).text,
                    'abstract': entry.find('atom:summary', namespace).text.strip().replace('\n', ' '),
                    'link': entry.find('atom:id', namespace).text,
                    'primary_category': entry.find('arxiv:primary_category', namespace).attrib['term']
                }
                papers.append(paper)
            except AttributeError as e:
                logger.error(f"Error parsing paper entry: {e}", exc_info=True)
                continue
        
        logger.info(f"Successfully fetched {len(papers)} papers")
        return papers
        
    except urllib.error.URLError as e:
        logger.error(f"Failed to fetch papers from arXiv: {e}", exc_info=True)
        return []
    except ET.ParseError as e:
        logger.error(f"Failed to parse XML response: {e}", exc_info=True)
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching papers: {e}", exc_info=True)
        return []

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

def save_results(papers):
    """
    Save papers to a text file
    
    Parameters:
        papers (list): List of paper dictionaries
    """
    logger.info(f"Saving {len(papers)} papers to results file")
    
    existing_papers = []
    try:
        with open('./data/results.json', 'r', encoding='utf-8') as f:
            existing_papers = json.load(f)
            logger.debug(f"Loaded {len(existing_papers)} existing papers from file")
    except FileNotFoundError:
        logger.debug("No existing results file found, creating new")
    except json.JSONDecodeError:
        logger.warning("Existing results file is corrupted, starting fresh")
    
    all_papers = {paper['title']: paper for paper in existing_papers + papers}
    all_papers = list(all_papers.values())
    
    try:
        with open('./data/results.json', 'w', encoding='utf-8') as f:
            json.dump(all_papers, f, ensure_ascii=False, indent=4)
        logger.info(f"Successfully saved {len(all_papers)} papers to results file")
    except Exception as e:
        logger.error(f"Failed to save results: {e}", exc_info=True)

# if __name__ == "__main__":
#     papers = get_papers(max_results=10)
    
#     print(f"\nFound {len(papers)} papers in astro-ph.SR category:")
#     display_papers(papers)
#     save_results(papers)