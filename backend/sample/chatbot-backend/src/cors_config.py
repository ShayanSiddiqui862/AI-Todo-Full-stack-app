from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

def setup_cors(app: FastAPI):
    """Configure CORS middleware to allow Next.js frontend communication as per spec FES.6"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],#Allow all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
        allow_headers=["Content-Type", "Authorization", "Accept"],  # Allow all headers
        # Additional security headers
        expose_headers=["*"],
        allow_origin_regex=r"https?://.*\.vercel\.app(/.*)?",  # Allow Vercel preview deployments
    )

# Example usage in main app
if __name__ == "__main__":
    app = FastAPI(title="RAG Chatbot Backend")
    setup_cors(app)
    print("CORS middleware configured successfully.")