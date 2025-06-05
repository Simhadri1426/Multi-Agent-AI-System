from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
import uvicorn
import json
from datetime import datetime
import os
from typing import Optional, Dict, Any
import PyPDF2
import io

app = FastAPI(title="Multi-Agent AI System")

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Mount the uploads directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Simple in-memory storage for demo purposes
file_store: Dict[str, Dict[str, Any]] = {}

def extract_pdf_content(pdf_bytes: bytes) -> str:
    """Extract text content from PDF bytes."""
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error extracting PDF content: {str(e)}"

@app.get("/", response_class=HTMLResponse)
async def get_upload_form():
    """Serve the upload form."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Multi-Agent AI System</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 min-h-screen">
        <div class="container mx-auto px-4 py-8">
            <h1 class="text-3xl font-bold text-center mb-8">Multi-Agent AI System</h1>
            
            <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
                <form id="uploadForm" class="space-y-4">
                    <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center" id="dropZone">
                        <input type="file" id="fileInput" class="hidden" />
                        <label for="fileInput" class="cursor-pointer">
                            <div class="text-gray-600">
                                <p class="mb-2">Drag and drop your file here or click to select</p>
                                <p class="text-sm">Supported formats: TXT, PDF, JSON, EML</p>
                            </div>
                        </label>
                    </div>
                    
                    <div id="fileInfo" class="hidden">
                        <p class="text-sm text-gray-600">Selected file: <span id="fileName"></span></p>
                        <button type="button" onclick="removeFile()" class="text-red-500 text-sm">Remove</button>
                    </div>
                    
                    <button type="submit" class="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600">
                        Process File
                    </button>
                </form>
                
                <div id="result" class="hidden mt-6">
                    <h2 class="text-xl font-semibold mb-2">Processing Result:</h2>
                    <div id="resultContent" class="bg-gray-100 p-4 rounded-lg overflow-x-auto"></div>
                    <div id="filePreview" class="mt-4"></div>
                </div>

                <div class="mt-8">
                    <h2 class="text-xl font-semibold mb-4">Uploaded Files</h2>
                    <div id="fileList" class="space-y-2">
                        <!-- Files will be listed here -->
                    </div>
                </div>
            </div>
        </div>

        <script>
            const dropZone = document.getElementById('dropZone');
            const fileInput = document.getElementById('fileInput');
            const fileInfo = document.getElementById('fileInfo');
            const fileName = document.getElementById('fileName');
            const uploadForm = document.getElementById('uploadForm');
            const result = document.getElementById('result');
            const resultContent = document.getElementById('resultContent');
            const filePreview = document.getElementById('filePreview');
            const fileList = document.getElementById('fileList');

            // Function to update file list
            async function updateFileList() {
                try {
                    const response = await fetch('/list-files');
                    const files = await response.json();
                    fileList.innerHTML = files.map(file => `
                        <div class="flex items-center justify-between p-2 bg-gray-50 rounded">
                            <span>${file}</span>
                            <div class="space-x-2">
                                <button onclick="viewFile('${file}')" class="text-blue-500 hover:underline">View Content</button>
                                <a href="/uploads/${file}" target="_blank" class="text-green-500 hover:underline">Download</a>
                                <button onclick="deleteFile('${file}')" class="text-red-500 hover:underline">Delete</button>
                            </div>
                        </div>
                    `).join('');
                } catch (error) {
                    console.error('Error fetching file list:', error);
                }
            }

            // Function to view file content
            async function viewFile(filename) {
                try {
                    const response = await fetch(`/view-content/${filename}`);
                    const data = await response.json();
                    resultContent.innerHTML = `<pre>${data.content}</pre>`;
                    result.classList.remove('hidden');
                } catch (error) {
                    console.error('Error viewing file:', error);
                    alert('Error viewing file content');
                }
            }

            // Function to delete file
            async function deleteFile(filename) {
                if (confirm('Are you sure you want to delete this file?')) {
                    try {
                        await fetch(`/delete-file/${filename}`, { method: 'DELETE' });
                        updateFileList();
                    } catch (error) {
                        console.error('Error deleting file:', error);
                    }
                }
            }

            // Handle drag and drop
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('border-blue-500');
            });

            dropZone.addEventListener('dragleave', () => {
                dropZone.classList.remove('border-blue-500');
            });

            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('border-blue-500');
                const file = e.dataTransfer.files[0];
                fileInput.files = e.dataTransfer.files;
                fileName.textContent = file.name;
                fileInfo.classList.remove('hidden');
            });

            // Handle file selection
            fileInput.addEventListener('change', () => {
                if (fileInput.files.length > 0) {
                    fileName.textContent = fileInput.files[0].name;
                    fileInfo.classList.remove('hidden');
                }
            });

            // Handle form submission
            uploadForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const file = fileInput.files[0];
                if (!file) return;

                const formData = new FormData();
                formData.append('file', file);

                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });

                    const data = await response.json();
                    resultContent.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
                    result.classList.remove('hidden');
                    updateFileList();
                } catch (error) {
                    console.error('Error:', error);
                    alert('An error occurred while processing the file.');
                }
            });

            function removeFile() {
                fileInput.value = '';
                fileInfo.classList.add('hidden');
                result.classList.add('hidden');
                filePreview.innerHTML = '';
            }

            // Initial file list load
            updateFileList();
        </script>
    </body>
    </html>
    """

@app.get("/view-content/{filename}")
async def view_file_content(filename: str):
    """View the content of a file."""
    file_path = os.path.join("uploads", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    file_type = filename.split(".")[-1].lower()
    
    try:
        if file_type == "pdf":
            with open(file_path, "rb") as f:
                content = extract_pdf_content(f.read())
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list-files")
async def list_files():
    """List all uploaded files."""
    files = []
    for filename in os.listdir("uploads"):
        if os.path.isfile(os.path.join("uploads", filename)):
            files.append(filename)
    return files

@app.delete("/delete-file/{filename}")
async def delete_file(filename: str):
    """Delete a file."""
    file_path = os.path.join("uploads", filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"message": "File deleted successfully"}
    raise HTTPException(status_code=404, detail="File not found")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a file."""
    try:
        # Read file content
        content = await file.read()
        filename = file.filename
        
        # Save file
        file_path = f"uploads/{filename}"
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Determine file type and process accordingly
        file_type = filename.split(".")[-1].lower()
        
        if file_type == "txt":
            result = process_text_file(content.decode())
        elif file_type == "json":
            result = process_json_file(content.decode())
        elif file_type == "pdf":
            result = process_pdf_file(content)
        elif file_type == "eml":
            result = process_email_file(content.decode())
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Store result
        file_id = str(datetime.now().timestamp())
        file_store[file_id] = {
            "filename": filename,
            "file_type": file_type,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "message": "File processed successfully",
            "file_id": file_id,
            "filename": filename,
            "file_type": file_type,
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{file_id}")
async def get_status(file_id: str):
    """Get processing status for a file."""
    if file_id not in file_store:
        raise HTTPException(status_code=404, detail="File not found")
    
    return file_store[file_id]

@app.get("/download/{file_id}")
async def download_file(file_id: str):
    """Download a processed file."""
    if file_id not in file_store:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = file_store[file_id]
    file_path = f"uploads/{file_info['filename']}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server")
    
    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=file_info['filename']
    )

@app.get("/view/{file_id}")
async def view_file(file_id: str):
    """View a file in the browser."""
    if file_id not in file_store:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = file_store[file_id]
    file_path = f"uploads/{file_info['filename']}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server")
    
    return FileResponse(
        file_path,
        media_type="application/pdf" if file_info['file_type'] == 'pdf' else "text/plain",
        filename=file_info['filename']
    )

def process_text_file(content: str) -> dict:
    """Process text file content."""
    # Simple text analysis
    words = content.split()
    return {
        "word_count": len(words),
        "summary": " ".join(words[:10]) + "..." if len(words) > 10 else content,
        "type": "text"
    }

def process_json_file(content: str) -> dict:
    """Process JSON file content."""
    try:
        data = json.loads(content)
        return {
            "structure": "valid JSON",
            "keys": list(data.keys()),
            "type": "json"
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")

def process_pdf_file(content: bytes) -> dict:
    """Process PDF file content."""
    try:
        text = extract_pdf_content(content)
        words = text.split()
        return {
            "size": len(content),
            "type": "pdf",
            "word_count": len(words),
            "preview": text[:200] + "..." if len(text) > 200 else text
        }
    except Exception as e:
        return {
            "size": len(content),
            "type": "pdf",
            "error": str(e)
        }

def process_email_file(content: str) -> dict:
    """Process email file content."""
    return {
        "type": "email",
        "message": "Email file received",
        "content_preview": content[:200] + "..." if len(content) > 200 else content
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 