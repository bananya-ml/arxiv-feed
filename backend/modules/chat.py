import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

import logging

logger = logging.getLogger(__name__)

class Chat:
    def __init__(self, model_name: str = "gemini-1.5-flash-8b") -> None:
        self.model_name = model_name

        self.model = genai.GenerativeModel(self.model_name)
        logger.debug("PaperSummarizer initialization complete")

    def generate_response(self, query: str, context: str):
        prompt = f"""Provide a comprehensive and accurate response to the user's query based on the provided context from research papers.

                            Use the following details to guide your response:

                            - Directly address the user's query.
                            - Use information specifically and only from the provided context.
                            - Maintain an academic tone throughout, ensuring clarity and professionalism.
                            - Cite specific papers using the URLs provided in the context when making key points.

                            # Steps

                            1. Carefully analyze the user's query to understand its main focus.
                            2. Review the context obtained from relevant excerpts of research papers.
                            3. Identify key points from the provided context that directly contribute to answering the query.
                            4. Organize these key points logically to create a cohesive and comprehensive response.
                            5. While quoting or referring to specific findings or claims, ensure to cite the corresponding research paper using the URL provided.
                            6. Maintain an academic and accurate tone, ensuring the response is precise, informative, and directly relevant to the query.

                            # Output Format

                            The output should be a well-structured paragraph or series of paragraphs that:

                            - Clearly communicates the information sought by the user's query.
                            - Incorporates direct references from the provided research papers.
                            - Provides citations by including the relevant URLs when making key points (e.g., "According to [URL], ...").

                            # Example

                            **User Query:** "What are the recent advancements in thermal energy storage systems?"

                            **Context from relevant papers:**
                            - A study published in 2021 explored latent heat-based thermal energy storage, noting improved material efficiency for phase change materials (PCMs) ([URL1]).
                            - Recent research demonstrates that nano-enhancements in storage mediums can significantly increase energy retention capacity ([URL2]).
                            - Advances in thermochemical storage have led to better scalability for industrial applications ([URL3]).

                            **Generated Response:**

                            Recent advancements in thermal energy storage systems primarily focus on improving efficiency and scalability through innovative materials and techniques. A study published in 2021 highlights significant improvements in phase change materials (PCMs) for latent heat-based storage, resulting in enhanced material efficiency ([URL1]). Additionally, recent research indicates that incorporating nano-enhancements into storage mediums can notably improve energy retention capacity, enabling more effective thermal management ([URL2]). There have also been important strides in thermochemical storage, which make the technology more scalable, particularly for industrial applications ([URL3]). These developments collectively illustrate promising trends in optimizing the efficiency and applicability of thermal energy storage technologies.

                            # Notes

                            - Ensure all cited URLs are integrated fluidly within sentences.
                            - Remain objective and ensure all information precisely reflects what is stated in the context without bias or extrapolation.
                             please provide a comprehensive and accurate response to this query: "{query}"

                            Context from relevant papers:
                            {context}
                            """
        response = self.model.generate_content(prompt)
        return response.text