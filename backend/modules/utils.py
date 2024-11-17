from typing import Optional
import tempfile
import requests

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