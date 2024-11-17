from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from typing import Optional, List
import os

from modules.api import get_papers, save_results
from modules.summarization import save_summaries, PaperSummarizer
from modules.data_extractor import extract_metadata
from modules.utils import download_pdf

from dotenv import load_dotenv
import time
import logging
from datetime import datetime

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

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

@app.post("/process_papers/", 
    response_model=List[PaperResponse],
    responses={
        200: {"description": "Successfully processed papers"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Process research papers",
    description="Downloads and processes research papers, generating summaries and extracting metadata."
)
async def process_papers(max_results: int = 10, category: str = "astro-ph.SR"):
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
        processed_papers = []
        for index, paper in enumerate(papers, 1):
            while True:  # Infinite retry loop for parsing
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
                        # Retry parsing the same paper
                        continue
                    
                    logger.debug("Successfully parsed PDF content")
                    metadata = extract_metadata(parsed_content)
                    paper.update({
                        'conclusion': metadata['conclusion'],
                        'ref_count': metadata['ref_count']
                    })
                    save_results([paper])
                    logger.debug("Saved paper results")

                    summary, insight = summarizer.summarize_paper(parsed_content)
                    save_summaries(paper['link'], summary, insight)
                    logger.debug("Saved paper summaries")
                    
                    processed_papers.append(paper)
                    logger.info(f"Successfully processed paper {index}/{len(papers)}")
                    break  # Exit the retry loop on success
            
                except Exception as e:
                    logger.error(f"Error processing paper {paper['link']}: {str(e)}", exc_info=True)
                    if "LlamaParse" in str(e):  # Check if the error is related to LlamaParse
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