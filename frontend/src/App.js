import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const App = () => {
  const [currentStep, setCurrentStep] = useState('upload');
  const [resumeId, setResumeId] = useState(null);
  const [parsedData, setParsedData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [improvedResume, setImprovedResume] = useState('');
  const [coverLetter, setCoverLetter] = useState('');
  const [error, setError] = useState('');

  // Form states
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [companyName, setCompanyName] = useState('');

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API}/resume/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResumeId(response.data.resume_id);
      setParsedData(response.data.parsed_data);
      setCurrentStep('review');
      
    } catch (error) {
      console.error('Upload error:', error);
      setError(error.response?.data?.detail || 'Error uploading resume');
    } finally {
      setIsLoading(false);
    }
  };

  const handleImproveResume = async () => {
    if (!resumeId) return;

    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/resume/improve`, {
        resume_id: resumeId,
        job_title: jobTitle || null,
        job_description: jobDescription || null
      });

      setImprovedResume(response.data.improved_resume);
      setCurrentStep('results');
      
    } catch (error) {
      console.error('Improve resume error:', error);
      setError(error.response?.data?.detail || 'Error improving resume');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateCoverLetter = async () => {
    if (!resumeId || !jobTitle || !companyName) {
      setError('Please fill in job title and company name for cover letter generation');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/cover-letter/generate`, {
        resume_id: resumeId,
        job_title: jobTitle,
        job_description: jobDescription || 'No specific job description provided',
        company_name: companyName
      });

      setCoverLetter(response.data.cover_letter);
      
    } catch (error) {
      console.error('Cover letter error:', error);
      setError(error.response?.data?.detail || 'Error generating cover letter');
    } finally {
      setIsLoading(false);
    }
  };

  const resetApp = () => {
    setCurrentStep('upload');
    setResumeId(null);
    setParsedData(null);
    setImprovedResume('');
    setCoverLetter('');
    setError('');
    setJobTitle('');
    setJobDescription('');
    setCompanyName('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">R2</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">R2OL.ai</h1>
                <p className="text-sm text-gray-600">Resume to Offer Letter</p>
              </div>
            </div>
            {resumeId && (
              <button
                onClick={resetApp}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
              >
                Start Over
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        {currentStep === 'upload' && (
          <div className="text-center mb-12">
            <div 
              className="relative h-64 bg-cover bg-center rounded-2xl mb-8 flex items-center justify-center"
              style={{
                backgroundImage: 'linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url(https://images.unsplash.com/photo-1659019729966-826c8f562847)',
              }}
            >
              <div className="text-white text-center">
                <h2 className="text-4xl font-bold mb-4">Transform Your Resume with AI</h2>
                <p className="text-xl opacity-90">Upload your resume and get AI-powered improvements + personalized cover letters</p>
              </div>
            </div>
          </div>
        )}

        {/* Progress Steps */}
        <div className="flex justify-center mb-8">
          <div className="flex items-center space-x-4">
            <div className={`flex items-center space-x-2 ${currentStep === 'upload' ? 'text-blue-600' : currentStep === 'review' || currentStep === 'results' ? 'text-green-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep === 'upload' ? 'bg-blue-600 text-white' : currentStep === 'review' || currentStep === 'results' ? 'bg-green-600 text-white' : 'bg-gray-200'}`}>
                1
              </div>
              <span className="font-medium">Upload</span>
            </div>
            <div className="w-8 h-px bg-gray-300"></div>
            <div className={`flex items-center space-x-2 ${currentStep === 'review' ? 'text-blue-600' : currentStep === 'results' ? 'text-green-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep === 'review' ? 'bg-blue-600 text-white' : currentStep === 'results' ? 'bg-green-600 text-white' : 'bg-gray-200'}`}>
                2
              </div>
              <span className="font-medium">Review</span>
            </div>
            <div className="w-8 h-px bg-gray-300"></div>
            <div className={`flex items-center space-x-2 ${currentStep === 'results' ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep === 'results' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
                3
              </div>
              <span className="font-medium">Results</span>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Upload Step */}
        {currentStep === 'upload' && (
          <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-xl shadow-lg p-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">Upload Your Resume</h3>
              
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
                <div className="mb-4">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <input
                  type="file"
                  id="resume-upload"
                  accept=".pdf,.doc,.docx,.txt"
                  onChange={handleFileUpload}
                  disabled={isLoading}
                  className="hidden"
                />
                <label
                  htmlFor="resume-upload"
                  className={`cursor-pointer inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {isLoading ? 'Processing...' : 'Choose Resume File'}
                </label>
                <p className="mt-2 text-sm text-gray-500">PDF, DOC, DOCX, or TXT files supported</p>
              </div>
            </div>
          </div>
        )}

        {/* Review Step */}
        {currentStep === 'review' && parsedData && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-xl shadow-lg p-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Review Parsed Information</h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                {/* Parsed Data Preview */}
                <div>
                  <h4 className="text-lg font-semibold text-gray-800 mb-4">Extracted Information</h4>
                  <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                    {parsedData.personal_info?.name && (
                      <div>
                        <span className="font-medium text-gray-700">Name:</span>
                        <span className="ml-2 text-gray-600">{parsedData.personal_info.name}</span>
                      </div>
                    )}
                    {parsedData.personal_info?.email && (
                      <div>
                        <span className="font-medium text-gray-700">Email:</span>
                        <span className="ml-2 text-gray-600">{parsedData.personal_info.email}</span>
                      </div>
                    )}
                    {parsedData.skills && parsedData.skills.length > 0 && (
                      <div>
                        <span className="font-medium text-gray-700">Skills:</span>
                        <div className="mt-1">
                          {parsedData.skills.slice(0, 5).map((skill, index) => (
                            <span key={index} className="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm mr-2 mb-1">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Job Details Form */}
                <div>
                  <h4 className="text-lg font-semibold text-gray-800 mb-4">Job Details (Optional)</h4>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Job Title</label>
                      <input
                        type="text"
                        value={jobTitle}
                        onChange={(e) => setJobTitle(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., Software Engineer"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Company Name</label>
                      <input
                        type="text"
                        value={companyName}
                        onChange={(e) => setCompanyName(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., Google, Microsoft"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Job Description</label>
                      <textarea
                        value={jobDescription}
                        onChange={(e) => setJobDescription(e.target.value)}
                        rows={4}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Paste the job description here for better tailoring..."
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex justify-center">
                <button
                  onClick={handleImproveResume}
                  disabled={isLoading}
                  className={`px-8 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {isLoading ? 'Generating...' : 'Improve My Resume with AI'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Results Step */}
        {currentStep === 'results' && (
          <div className="max-w-6xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Improved Resume */}
              {improvedResume && (
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold text-gray-900">AI-Improved Resume</h3>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(improvedResume);
                        alert('Resume copied to clipboard!');
                      }}
                      className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                    >
                      Copy
                    </button>
                  </div>
                  <div className="max-h-96 overflow-y-auto bg-gray-50 rounded-lg p-4">
                    <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
                      {improvedResume}
                    </pre>
                  </div>
                </div>
              )}

              {/* Cover Letter */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-bold text-gray-900">AI Cover Letter</h3>
                  {coverLetter && (
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(coverLetter);
                        alert('Cover letter copied to clipboard!');
                      }}
                      className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                    >
                      Copy
                    </button>
                  )}
                </div>
                
                {!coverLetter ? (
                  <div className="text-center py-8">
                    <p className="text-gray-600 mb-4">Generate a personalized cover letter</p>
                    <button
                      onClick={handleGenerateCoverLetter}
                      disabled={isLoading || !jobTitle || !companyName}
                      className={`px-6 py-2 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors ${(isLoading || !jobTitle || !companyName) ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                      {isLoading ? 'Generating...' : 'Generate Cover Letter'}
                    </button>
                    {(!jobTitle || !companyName) && (
                      <p className="text-sm text-red-600 mt-2">Please fill in job title and company name above</p>
                    )}
                  </div>
                ) : (
                  <div className="max-h-96 overflow-y-auto bg-gray-50 rounded-lg p-4">
                    <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
                      {coverLetter}
                    </pre>
                  </div>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="mt-8 text-center space-x-4">
              <button
                onClick={resetApp}
                className="px-6 py-2 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700 transition-colors"
              >
                Upload Another Resume
              </button>
              {(improvedResume || coverLetter) && (
                <button
                  onClick={() => {
                    const content = `${improvedResume}\n\n---\n\n${coverLetter}`;
                    const blob = new Blob([content], { type: 'text/plain' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'resume-and-cover-letter.txt';
                    a.click();
                    URL.revokeObjectURL(url);
                  }}
                  className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Download All
                </button>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">
            <p className="text-gray-600">© 2025 R2OL.ai - Powered by AI</p>
            <p className="text-sm text-gray-500 mt-1">Transform your career with intelligent resume optimization</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;