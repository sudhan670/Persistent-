# Persistent 
Set up environment variables in .env:

CopyOPENAI_API_KEY=your_openai_api_key
MONGODB_URI=your_mongodb_uri

Install dependencies:
For Frontend (React):

bashCopynpm install react lucide-react tailwindcss
For Backend (FastAPI):
bashCopypip install fastapi uvicorn openai motor python-dotenv

Implementation steps:


Start the FastAPI backend server
Run the React development server
Set up MongoDB database
Test the chatbot locally
Deploy to your preferred hosting service


To embed the chatbot in a website:


Get the embed code from the /api/embed endpoint
Add the iframe code to your website
Style as needed using the provided CSS classes

Key features:

Real-time chat interface with typing indicators
Session persistence in MongoDB
OpenAI integration for intelligent responses
Responsive design
Easy website embedding
Chat history
Error handling
Loading states
