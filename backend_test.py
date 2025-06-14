import requests
import os
import json
import base64
import pytest
import tempfile
from pathlib import Path

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://a5085778-3744-4975-90b0-ad66013b38b6.preview.emergentagent.com"
API_URL = f"{BACKEND_URL}/api"

# Sample data for testing
SAMPLE_RESUME_TEXT = """
John Doe
Software Engineer
john.doe@example.com | (555) 123-4567 | San Francisco, CA | linkedin.com/in/johndoe

SUMMARY
Experienced software engineer with 5+ years of experience in full-stack development, 
specializing in Python, React, and cloud technologies. Passionate about building scalable, 
user-friendly applications that solve real-world problems.

SKILLS
Programming: Python, JavaScript, TypeScript, Java, SQL
Frameworks: React, FastAPI, Django, Express.js
Cloud: AWS (EC2, S3, Lambda), Google Cloud Platform
Tools: Git, Docker, Kubernetes, CI/CD pipelines

EXPERIENCE
Senior Software Engineer | TechCorp Inc. | Jan 2021 - Present
- Led development of a microservices-based e-commerce platform, increasing transaction speed by 40%
- Implemented automated testing framework reducing bug rate by 30%
- Mentored junior developers and conducted code reviews

Software Engineer | InnovateSoft | Mar 2018 - Dec 2020
- Developed RESTful APIs using Django and FastAPI
- Built responsive front-end interfaces with React and Redux
- Optimized database queries, improving application performance by 25%

EDUCATION
Master of Science in Computer Science | Stanford University | 2018
Bachelor of Science in Computer Engineering | UC Berkeley | 2016

PROJECTS
Personal Finance Tracker
- Built a full-stack application using React, Node.js, and MongoDB
- Implemented OAuth authentication and data visualization with D3.js

Open Source Contribution
- Active contributor to Python libraries for data processing
- Created documentation and fixed bugs in popular open-source projects
"""

SAMPLE_JOB_TITLE = "Senior Full Stack Developer"
SAMPLE_JOB_DESCRIPTION = """
We are looking for a Senior Full Stack Developer to join our growing team. The ideal candidate will have:
- 5+ years of experience in full-stack development
- Strong proficiency in Python and JavaScript/TypeScript
- Experience with React and modern backend frameworks
- Knowledge of cloud services (AWS/GCP)
- Experience with CI/CD pipelines and DevOps practices
- Strong problem-solving skills and attention to detail
"""
SAMPLE_COMPANY_NAME = "Innovative Tech Solutions"

# Test functions
def test_api_health():
    """Test the API health endpoint"""
    print("\n--- Testing API Health ---")
    response = requests.get(f"{API_URL}/")
    print(f"Response: {response.status_code} - {response.text}")
    assert response.status_code == 200
    assert "R2OL.ai API" in response.text
    print("✅ API Health check passed")

def test_resume_upload():
    """Test resume upload functionality"""
    print("\n--- Testing Resume Upload ---")
    
    # Create a temporary file with sample resume content
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp:
        temp.write(SAMPLE_RESUME_TEXT.encode('utf-8'))
        temp_path = temp.name
    
    try:
        # Upload the resume
        with open(temp_path, 'rb') as f:
            files = {'file': ('sample_resume.txt', f, 'text/plain')}
            response = requests.post(f"{API_URL}/resume/upload", files=files)
        
        print(f"Response: {response.status_code}")
        print(f"Response content: {response.text[:200]}...")  # Print first 200 chars
        
        assert response.status_code == 200
        response_data = response.json()
        assert "resume_id" in response_data
        assert "parsed_data" in response_data
        
        # Save resume_id for other tests
        resume_id = response_data["resume_id"]
        print(f"✅ Resume upload successful. Resume ID: {resume_id}")
        return resume_id
    
    finally:
        # Clean up the temporary file
        os.unlink(temp_path)

def test_get_resume(resume_id):
    """Test retrieving a resume by ID"""
    print(f"\n--- Testing Get Resume (ID: {resume_id}) ---")
    response = requests.get(f"{API_URL}/resume/{resume_id}")
    print(f"Response: {response.status_code}")
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["resume_id"] == resume_id
    assert "parsed_data" in response_data
    print("✅ Get resume test passed")

def test_improve_resume(resume_id):
    """Test resume improvement functionality"""
    print(f"\n--- Testing Resume Improvement (ID: {resume_id}) ---")
    
    payload = {
        "resume_id": resume_id,
        "job_title": SAMPLE_JOB_TITLE,
        "job_description": SAMPLE_JOB_DESCRIPTION
    }
    
    response = requests.post(f"{API_URL}/resume/improve", json=payload)
    print(f"Response: {response.status_code}")
    
    assert response.status_code == 200
    response_data = response.json()
    assert "response_id" in response_data
    assert "improved_resume" in response_data
    assert len(response_data["improved_resume"]) > 100  # Ensure we got substantial content
    
    print("✅ Resume improvement test passed")
    print(f"Improved resume excerpt: {response_data['improved_resume'][:200]}...")
    return response_data["response_id"]

def test_generate_cover_letter(resume_id):
    """Test cover letter generation functionality"""
    print(f"\n--- Testing Cover Letter Generation (ID: {resume_id}) ---")
    
    payload = {
        "resume_id": resume_id,
        "job_title": SAMPLE_JOB_TITLE,
        "job_description": SAMPLE_JOB_DESCRIPTION,
        "company_name": SAMPLE_COMPANY_NAME
    }
    
    response = requests.post(f"{API_URL}/cover-letter/generate", json=payload)
    print(f"Response: {response.status_code}")
    
    assert response.status_code == 200
    response_data = response.json()
    assert "response_id" in response_data
    assert "cover_letter" in response_data
    assert len(response_data["cover_letter"]) > 100  # Ensure we got substantial content
    
    print("✅ Cover letter generation test passed")
    print(f"Cover letter excerpt: {response_data['cover_letter'][:200]}...")
    return response_data["response_id"]

def test_get_ai_responses(resume_id):
    """Test retrieving AI responses for a resume"""
    print(f"\n--- Testing Get AI Responses (Resume ID: {resume_id}) ---")
    
    response = requests.get(f"{API_URL}/ai-responses/{resume_id}")
    print(f"Response: {response.status_code}")
    
    assert response.status_code == 200
    response_data = response.json()
    assert "responses" in response_data
    assert len(response_data["responses"]) > 0  # Should have at least one response
    
    print("✅ Get AI responses test passed")
    print(f"Found {len(response_data['responses'])} AI responses")

def test_error_handling():
    """Test error handling for invalid inputs"""
    print("\n--- Testing Error Handling ---")
    
    # Test invalid resume ID
    invalid_id = "nonexistent-id-12345"
    response = requests.get(f"{API_URL}/resume/{invalid_id}")
    print(f"Invalid resume ID response: {response.status_code}")
    assert response.status_code == 404
    
    # Test invalid file type for resume upload
    with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as temp:
        temp.write(b"Invalid file type test")
        temp_path = temp.name
    
    try:
        with open(temp_path, 'rb') as f:
            files = {'file': ('invalid.xyz', f, 'application/octet-stream')}
            response = requests.post(f"{API_URL}/resume/upload", files=files)
        
        print(f"Invalid file type response: {response.status_code}")
        assert response.status_code == 400
    
    finally:
        os.unlink(temp_path)
    
    print("✅ Error handling tests passed")

def run_all_tests():
    """Run all tests in sequence"""
    print("\n=== Starting R2OL.ai Backend API Tests ===\n")
    
    try:
        # Test API health
        test_api_health()
        
        # Test resume upload and get resume ID
        resume_id = test_resume_upload()
        
        # Test getting resume by ID
        test_get_resume(resume_id)
        
        # Test resume improvement
        improve_response_id = test_improve_resume(resume_id)
        
        # Test cover letter generation
        cover_letter_response_id = test_generate_cover_letter(resume_id)
        
        # Test getting AI responses
        test_get_ai_responses(resume_id)
        
        # Test error handling
        test_error_handling()
        
        print("\n=== All tests completed successfully! ===")
        return True
    
    except Exception as e:
        print(f"\n❌ Tests failed: {str(e)}")
        return False

if __name__ == "__main__":
    run_all_tests()