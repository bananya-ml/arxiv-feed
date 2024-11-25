from fastapi import FastAPI, HTTPException, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from typing import Optional, List
import os
import json

from modules.api import get_papers
from modules.summarization import PaperSummarizer
from modules.data_extractor import extract_metadata
from modules.embeddings import EmbeddingsManager
from modules.chat import generate_response
from modules.utils import download_pdf, save_results, save_summaries

from dotenv import load_dotenv
import time
import logging
import yaml

load_dotenv()

# Load configuration from YAML file
with open("chromadb_config.yaml", "r") as config_file:
    yaml_config = yaml.safe_load(config_file)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

RESULTS_FILE_PATH = "./data/results.json"
SUMMARIES_FILE_PATH = "./data/summaries.json"
LOCAL_VECTORSTORE_PATH = "./data/db/chromadb_storage"

def get_cors_origins():
    origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    return [origin.strip() for origin in origins_str.split(",")]

def get_cors_methods():
    methods_str = os.getenv("CORS_METHODS", "GET,POST,PUT,DELETE")
    return [method.strip() for method in methods_str.split(",")]

def get_cors_headers():
    headers_str = os.getenv("CORS_HEADERS", "*")
    return [header.strip() for header in headers_str.split(",")] if headers_str != "*" else ["*"]

app = FastAPI(
    title="Research Paper Processing API",
    description="""
    This API processes research papers by:
    - Downloading PDFs
    - Extracting metadata
    - Generating summaries and insights
    - Saving results
    """,
    version="1.0.0",
    contact={
        "name": "Ananya Bhatnagar",
        "email": "bhatnagarananya64@gmail.com",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=os.getenv("ALLOW_CREDENTIALS", "true").lower() == "true",
    allow_methods=get_cors_methods(),
    allow_headers=get_cors_headers(),
)

summarizer = PaperSummarizer()

summarizer = PaperSummarizer()
embeddings_manager = EmbeddingsManager(config=yaml_config, path=LOCAL_VECTORSTORE_PATH)

class ErrorResponse(BaseModel):
    detail: str

class PaperResponse(BaseModel):
    title: str
    authors: List[str]
    published: str
    abstract: str
    link: str
    primary_category: str
    conclusion: Optional[str]
    ref_count: Optional[int]

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Example Research Paper",
                "authors": ["John Doe", "Jane Smith"],
                "published": "2024-03-20",
                "abstract": "This paper discusses...",
                "link": "https://example.com/paper.pdf",
                "primary_category": "Computer Science",
                "conclusion": "We demonstrated that...",
                "ref_count": 42
            }
        }

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query or prompt", min_length=1, max_length=500)
    paper_url: Optional[str] = Field(default=None, description="Optional URL to filter search results")
    top_k: int = Field(default=5, ge=1, le=10, description="Number of top results to return")

class SearchResult(BaseModel):
    chunk_text: str
    distance: float
    doc_id: str
    paper_url: str

    class Config:
        json_schema_extra = {
            "example": {
                "chunk_text": "A sample text chunk from the research paper",
                "distance": 0.75,
                "doc_id": "unique-document-id",
                "paper_url": "https://example.com/paper.pdf"
            }
        }

class ChatResponse(BaseModel):
    similar_chunks: List[SearchResult]
    llm_response: str

    class Config:
        json_schema_extra = {
            "example": {
                "similar_chunks": [
                    {
                        "chunk_text": "A sample text chunk from the research paper",
                        "distance": 0.75,
                        "doc_id": "unique-document-id",
                        "paper_url": "https://example.com/paper.pdf"
                    }
                ],
                "llm_response": "Based on the relevant papers, the answer to your query is..."
            }
        }

@app.post("/process_papers", 
    response_model=List[PaperResponse],
    responses={
        200: {"description": "Successfully processed papers"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Process research papers",
    description="Downloads and processes research papers, generating summaries and extracting metadata."
)

async def process_papers(background_tasks: BackgroundTasks, max_results: int = 10, category: str = "astro-ph.SR"):
    try:
        logger.info(f"Starting to process {max_results} papers from category: {category}")
        
        if max_results <= 0 or max_results > 10:
            logger.warning(f"Invalid max_results value: {max_results}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="max_results must be between 1 and 10"
            )

        papers = get_papers(max_results=max_results, category=category)
        if not papers:
            logger.warning("No papers found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No papers found"
            )
        
        logger.info(f"Found {len(papers)} papers to process")
        
        # check for existing results
        existing_results = []
        for paper in papers:
            if os.path.exists(RESULTS_FILE_PATH):
                with open(RESULTS_FILE_PATH, 'r') as results_file:
                    existing_data = json.load(results_file)
                    if paper in existing_data:
                        existing_results.append(paper)

        if existing_results:
            summaries_exist = True
            for paper in existing_results:
                if not os.path.exists(SUMMARIES_FILE_PATH):
                    summaries_exist = False
                    break
                with open(SUMMARIES_FILE_PATH, 'r') as summaries_file:
                    summaries_data = json.load(summaries_file)
                    if paper['link'] not in summaries_data:
                        summaries_exist = False
                        break
            
            if summaries_exist:
                logger.info("Returning existing results and summaries.")
                for paper in existing_results:
                    paper['summary'] = summaries_data[paper['link']]['summary']
                    paper['insight'] = summaries_data[paper['link']]['insight']
                return existing_results

        processed_papers = []
        for index, paper in enumerate(papers, 1):
            while True:
                try:
                    logger.info(f"Processing paper {index}/{len(papers)}: {paper.get('title', 'Unknown Title')}")
                    
                    pdf_path = download_pdf(paper['link'])
                    if not pdf_path:
                        logger.error(f"Failed to download paper: {paper['link']}")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to download paper: {paper['link']}"
                        )
                    
                    logger.debug(f"Successfully downloaded PDF to {pdf_path}")
                    parsed_content = summarizer.parse_pdf(pdf_path)
                    if not parsed_content:
                        logger.error(f"Failed to parse paper: {paper['link']}")
                        continue  # Retry parsing the same paper
                    
                    logger.debug("Successfully parsed PDF content")
                    metadata = extract_metadata(parsed_content)
                    paper.update({
                        'conclusion': metadata['conclusion'],
                        'ref_count': metadata['ref_count']
                    })
                    save_results([paper], RESULTS_FILE_PATH)
                    logger.debug("Saved paper results")

                    summary, insight, full_text = summarizer.summarize_paper(parsed_content)
                    save_summaries(paper['link'], summary, insight, full_text, SUMMARIES_FILE_PATH)
                    logger.debug("Saved paper summaries")

                    background_tasks.add_task(
                        embeddings_manager.store_document_embeddings, 
                        text=full_text, 
                        url=paper['link']
                    )
                    logger.debug("Embedding task added to background")

                    processed_papers.append(paper)
                    logger.info(f"Successfully processed paper {index}/{len(papers)}")
                    break  # Exit the retry loop on success
            
                except Exception as e:
                    logger.error(f"Error processing paper {paper['link']}: {str(e)}", exc_info=True)
                    if "LlamaParse" in str(e):
                        logger.warning("Retrying due to LlamaParse communication issue...")
                        continue  # Retry if LlamaParse fails
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to process paper: {paper['link']} - {str(e)}"
                        )
        
        logger.info(f"Successfully processed all {len(processed_papers)} papers")

        return processed_papers
    
    except Exception as e:
        logger.error(f"Error in process_papers: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process papers - {str(e)}"
        )

@app.post("/chat", 
    response_model=ChatResponse,
    responses={
        200: {"description": "Successfully generated response with similar text chunks"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Search similar text chunks and generate response",
    description="Search for text chunks similar to the given prompt and generate an LLM response using the chunks as context."
)
async def search_similar_chunks(search_request: SearchRequest):
    try:
        logger.info(f"Searching for similar chunks with prompt: {search_request.query}")
        
        if not search_request.query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query must not be empty"
            )

        results = embeddings_manager.search_similar_chunks(
            query=search_request.query, 
            top_k=search_request.top_k, 
            url=search_request.paper_url or ""
        )
        
        search_results = [
            SearchResult(
                chunk_text=result['chunk_text'],
                distance=result['distance'],
                doc_id=result['doc_id'],
                paper_url=result['paper_url']
            ) for result in results
        ]
        
        logger.info(f"Found {len(search_results)} similar chunks")
        context = "\n\n".join([result.chunk_text for result in search_results])
        
        try:
            logger.info("Generating LLM response using context")
            response = generate_response(search_request.query, context)
            logger.debug("Successfully generated LLM response")
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate response - {str(e)}"
            )
        
        return ChatResponse(
            similar_chunks=search_results,
            llm_response=response
        )
    
    except Exception as e:
        logger.error(f"Error in search_similar_chunks: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request - {str(e)}"
        )

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Processing {request.method} request to {request.url.path}")
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Request processed in {process_time:.2f} seconds")
    return response

@app.get("/",
    response_model=dict,
    summary="Health Check",
    description="Returns the health status of the API",
    responses={
        200: {
            "description": "API is healthy",
            "content": {
                "application/json": {
                    "example": {"status": "healthy", "version": "1.0.0"}
                }
            }
        }
    }
)
async def health_check():
    return {
        "status": "healthy",
        "version": app.version
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"An unexpected error occurred: {str(exc)}"}
    )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)