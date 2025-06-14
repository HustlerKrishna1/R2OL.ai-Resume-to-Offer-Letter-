from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import base64
import json
import asyncio
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class ResumeUpload(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    content: str  # base64 encoded
    parsed_data: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ResumeImproveRequest(BaseModel):
    resume_id: str
    job_title: Optional[str] = None
    job_description: Optional[str] = None

class CoverLetterRequest(BaseModel):
    resume_id: str
    job_title: str
    job_description: str
    company_name: str

class AIResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resume_id: str
    response_type: str  # "resume_improvement" or "cover_letter"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# AI Integration Functions
async def get_gemini_response(system_message: str, user_message: str, session_id: str = None) -> str:
    try:
        # Get API key from environment
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
        session_id = session_id or str(uuid.uuid4())
        
        # Initialize Gemini chat
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=system_message
        ).with_model("gemini", "gemini-2.5-pro-preview-05-06").with_max_tokens(8192)
        
        # Create user message
        user_msg = UserMessage(text=user_message)
        
        # Send message and get response
        response = await chat.send_message(user_msg)
        return response
        
    except Exception as e:
        logger.error(f"Error in Gemini API call: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

async def parse_resume_text(content: str) -> Dict[str, Any]:
    """Parse resume text and extract structured information"""
    system_message = """You are an expert resume parser. Extract structured information from the resume text provided. 
    Return a JSON object with the following structure:
    {
        "personal_info": {
            "name": "",
            "email": "",
            "phone": "",
            "location": "",
            "linkedin": "",
            "portfolio": ""
        },
        "summary": "",
        "skills": [],
        "experience": [
            {
                "title": "",
                "company": "",
                "duration": "",
                "responsibilities": []
            }
        ],
        "education": [
            {
                "degree": "",
                "institution": "",
                "year": "",
                "gpa": ""
            }
        ],
        "projects": [
            {
                "name": "",
                "description": "",
                "technologies": []
            }
        ],
        "certifications": []
    }
    Fill in only the information that is available in the resume. Leave empty strings or arrays for missing information."""
    
    user_message = f"Parse this resume and extract structured information:\n\n{content}"
    
    try:
        response = await get_gemini_response(system_message, user_message)
        # Try to parse JSON response
        return json.loads(response)
    except json.JSONDecodeError:
        # If JSON parsing fails, return basic structure
        return {
            "personal_info": {},
            "summary": "",
            "skills": [],
            "experience": [],
            "education": [],
            "projects": [],
            "certifications": []
        }

async def improve_resume(parsed_data: Dict[str, Any], job_title: str = None, job_description: str = None) -> str:
    """Generate improved resume based on parsed data and job requirements"""
    system_message = """You are an expert resume writer and career coach. Create a professional, ATS-friendly resume that highlights the candidate's strengths and aligns with job requirements when provided. 
    Format the resume in clean, professional format with clear sections. Focus on quantifiable achievements and impact."""
    
    context = f"Original resume data: {json.dumps(parsed_data, indent=2)}"
    
    if job_title and job_description:
        user_message = f"""Based on the following resume data, create an improved, tailored resume for the position: {job_title}

Job Description: {job_description}

{context}

Create a complete, professional resume that:
1. Highlights relevant skills and experience for this specific role
2. Uses keywords from the job description
3. Quantifies achievements where possible
4. Is ATS-friendly
5. Has a compelling summary section

Format as a complete resume with all sections."""
    else:
        user_message = f"""Based on the following resume data, create an improved, professional resume:

{context}

Create a complete, professional resume that:
1. Has a compelling summary section
2. Highlights key skills and achievements
3. Uses strong action verbs
4. Quantifies achievements where possible
5. Is ATS-friendly

Format as a complete resume with all sections."""
    
    return await get_gemini_response(system_message, user_message)

async def generate_cover_letter(parsed_data: Dict[str, Any], job_title: str, job_description: str, company_name: str) -> str:
    """Generate personalized cover letter"""
    system_message = """You are an expert cover letter writer. Create personalized, compelling cover letters that demonstrate the candidate's fit for the specific role and company. The cover letter should be professional, engaging, and highlight relevant experience."""
    
    user_message = f"""Based on the following candidate information, write a compelling cover letter for the position: {job_title} at {company_name}

Job Description: {job_description}

Candidate Information: {json.dumps(parsed_data, indent=2)}

Create a cover letter that:
1. Opens with a strong hook that shows enthusiasm for the role
2. Highlights 2-3 most relevant experiences/achievements that match the job requirements
3. Shows knowledge of the company (you can make reasonable assumptions)
4. Closes with a strong call to action
5. Is professional yet personable
6. Is approximately 3-4 paragraphs

Format as a complete cover letter with proper business letter structure."""
    
    return await get_gemini_response(system_message, user_message)

# API Routes
@api_router.get("/")
async def root():
    return {"message": "R2OL.ai API - Resume to Offer Letter"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

@api_router.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.doc', '.docx', '.txt')):
            raise HTTPException(status_code=400, detail="Only PDF, DOC, DOCX, and TXT files are supported")
        
        # Read file content
        content = await file.read()
        
        # Convert to base64
        base64_content = base64.b64encode(content).decode('utf-8')
        
        # For this MVP, we'll treat the file as text content
        # In a real implementation, you'd use proper parsing for PDF/DOC files
        try:
            text_content = content.decode('utf-8') if file.filename.lower().endswith('.txt') else "Resume content uploaded successfully"
        except UnicodeDecodeError:
            text_content = "Binary file uploaded successfully"
        
        # Parse resume content
        parsed_data = await parse_resume_text(text_content)
        
        # Create resume record
        resume = ResumeUpload(
            filename=file.filename,
            content=base64_content,
            parsed_data=parsed_data
        )
        
        # Save to database
        await db.resumes.insert_one(resume.dict())
        
        return JSONResponse(content={
            "message": "Resume uploaded and parsed successfully",
            "resume_id": resume.id,
            "filename": resume.filename,
            "parsed_data": parsed_data
        })
        
    except Exception as e:
        logger.error(f"Error uploading resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

@api_router.get("/resume/{resume_id}")
async def get_resume(resume_id: str):
    try:
        resume = await db.resumes.find_one({"id": resume_id})
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        return JSONResponse(content={
            "resume_id": resume["id"],
            "filename": resume["filename"],
            "parsed_data": resume.get("parsed_data", {}),
            "created_at": resume["created_at"].isoformat()
        })
    except Exception as e:
        logger.error(f"Error retrieving resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving resume: {str(e)}")

@api_router.post("/resume/improve")
async def improve_resume_endpoint(request: ResumeImproveRequest):
    try:
        # Get resume from database
        resume = await db.resumes.find_one({"id": request.resume_id})
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Generate improved resume
        improved_content = await improve_resume(
            resume.get("parsed_data", {}),
            request.job_title,
            request.job_description
        )
        
        # Save AI response
        ai_response = AIResponse(
            resume_id=request.resume_id,
            response_type="resume_improvement",
            content=improved_content
        )
        
        await db.ai_responses.insert_one(ai_response.dict())
        
        return JSONResponse(content={
            "response_id": ai_response.id,
            "resume_id": request.resume_id,
            "improved_resume": improved_content
        })
        
    except Exception as e:
        logger.error(f"Error improving resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error improving resume: {str(e)}")

@api_router.post("/cover-letter/generate")
async def generate_cover_letter_endpoint(request: CoverLetterRequest):
    try:
        # Get resume from database
        resume = await db.resumes.find_one({"id": request.resume_id})
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Generate cover letter
        cover_letter_content = await generate_cover_letter(
            resume.get("parsed_data", {}),
            request.job_title,
            request.job_description,
            request.company_name
        )
        
        # Save AI response
        ai_response = AIResponse(
            resume_id=request.resume_id,
            response_type="cover_letter",
            content=cover_letter_content
        )
        
        await db.ai_responses.insert_one(ai_response.dict())
        
        return JSONResponse(content={
            "response_id": ai_response.id,
            "resume_id": request.resume_id,
            "cover_letter": cover_letter_content
        })
        
    except Exception as e:
        logger.error(f"Error generating cover letter: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating cover letter: {str(e)}")

@api_router.get("/ai-responses/{resume_id}")
async def get_ai_responses(resume_id: str):
    try:
        responses = await db.ai_responses.find({"resume_id": resume_id}).to_list(100)
        return JSONResponse(content={
            "resume_id": resume_id,
            "responses": [
                {
                    "id": resp["id"],
                    "type": resp["response_type"],
                    "content": resp["content"],
                    "created_at": resp["created_at"].isoformat()
                }
                for resp in responses
            ]
        })
    except Exception as e:
        logger.error(f"Error retrieving AI responses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving AI responses: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
