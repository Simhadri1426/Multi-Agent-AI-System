                                        Multi-Agent AI System

A modular FastAPI-based system that processes different types of files using specialized agents.

## Architecture

### System Overview
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Client Browser │────▶│  FastAPI Server │────▶│  File Storage   │
│                 │     │                 │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │                 │
                        │ Classifier Agent│
                        │                 │
                        └────────┬────────┘
                                 │
                 ┌───────────────┼───────────────┐
                 │               │               │
                 ▼               ▼               ▼
         ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
         │             │ │             │ │             │
         │ PDF Agent   │ │ JSON Agent  │ │ Email Agent │
         │             │ │             │ │             │
         └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
                │               │               │
                └───────────────┼───────────────┘
                                │
                                ▼
                        ┌─────────────────┐
                        │                 │
                        │ Result Storage  │
                        │                 │
                        └─────────────────┘
```

### Detailed Process Flow

1. **File Upload Process**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │    │  FastAPI    │    │  File       │    │  Classifier │
│  Uploads    │───▶│  Receives   │───▶│  Storage    │───▶│   Agent     │
│   File      │    │   File      │    │  Saves      │    │  Analyzes   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

2. **Processing Pipeline**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Classifier  │    │ Specific    │    │ Process     │    │ Store       │
│ Routes to   │───▶│ Agent       │───▶│ Content     │───▶│ Results     │
│ Agent       │    │ Processes   │    │ Extracts    │    │ in DB       │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

3. **Response Flow**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Result      │    │ FastAPI     │    │ Client      │    │ Display     │
│ Storage     │───▶│ Formats     │───▶│ Receives    │───▶│ Results     │
│ Retrieves   │    │ Response    │    │ Response    │    │ in UI       │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Component Interaction

1. **File Processing Flow**
```
Client Request
     │
     ▼
FastAPI Server
     │
     ├───▶ File Validation
     │
     ├───▶ Type Detection
     │
     ├───▶ Route to Agent
     │
     ├───▶ Process Content
     │
     ├───▶ Store Results
     │
     └───▶ Return Response
```

2. **Agent Processing Flow**
```
Input File
     │
     ▼
Classifier Agent
     │
     ├───▶ PDF Agent
     │    ├───▶ Text Extraction
     │    ├───▶ Metadata Analysis
     │    └───▶ Content Processing
     │
     ├───▶ JSON Agent
     │    ├───▶ Structure Validation
     │    ├───▶ Schema Analysis
     │    └───▶ Data Processing
     │
     └───▶ Email Agent
          ├───▶ Header Analysis
          ├───▶ Content Extraction
          ├───▶ Attachment Processing
          └───▶ Metadata Extraction
```

### Data Flow

1. **File Upload to Processing**
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Client     │     │  Server     │     │  Storage    │
│  Upload     │────▶│  Receive    │────▶│  Save       │
└─────────────┘     └─────────────┘     └─────────────┘
                                             │
                                             ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Results    │     │  Server     │     │  Client     │
│  Return     │◀────│  Process    │◀────│  Receive    │
└─────────────┘     └─────────────┘     └─────────────┘
```

2. **Error Handling Flow**
```
Error Occurs
     │
     ├───▶ Validation Error
     │    └───▶ Return 400
     │
     ├───▶ Processing Error
     │    └───▶ Return 500
     │
     └───▶ System Error
          └───▶ Log & Return 500
```

### System Components

1. **FastAPI Backend**
   - RESTful API endpoints for file processing
   - Static file serving for uploads
   - WebSocket support for real-time updates
   - Built-in API documentation (Swagger UI)

2. **File Processing Agents**
   - **Classifier Agent**: Determines file type and routes to appropriate processor
   - **Text Agent**: Processes .txt files with text analysis
   - **PDF Agent**: Extracts and processes PDF content
   - **JSON Agent**: Validates and processes JSON files
   - **Email Agent**: Processes email (.eml) files

3. **Storage System**
   - File storage in `uploads/` directory
   - SQLite database for metadata and processing results
   - In-memory cache for active processing

## Features

### File Processing
- Support for multiple file types:
  - Text files (.txt)
  - PDF documents (.pdf)
  - JSON files (.json)
  - Email files (.eml)
- Automatic file type detection
- Content extraction and analysis
- Error handling and validation

### User Interface
- Modern, responsive web interface
- Drag-and-drop file upload
- Real-time processing status
- File preview capabilities
- Download processed files

### Security
- File type validation
- Size limits
- Secure file storage
- Error handling and logging

## Technical Details

### API Endpoints

1. **File Operations**
   - `POST /upload`: Upload and process files
   - `GET /list-files`: List all processed files
   - `GET /view-content/{filename}`: View file content
   - `DELETE /delete-file/{filename}`: Delete a file

2. **File Processing**
   - Text Analysis: Word count, content summary
   - PDF Processing: Text extraction, metadata
   - JSON Validation: Structure analysis
   - Email Processing: Header analysis, content preview

### Database Schema

```sql
CREATE TABLE processed_files (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    processing_result TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Setup and Installation

1. **Prerequisites**
   - Python 3.8+
   - pip (Python package manager)
   - Virtual environment (recommended)

2. **Installation Steps**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Run the application
   python app.py
   ```

3. **Configuration**
   - Default port: 8000
   - Upload directory: `uploads/`
   - Database: `multi_agent.db`

## Usage

1. **Access the Web Interface**
   - Open `http://localhost:8000` in your browser
   - Use the drag-and-drop interface to upload files

2. **API Documentation**
   - Access Swagger UI at `http://localhost:8000/docs`
   - View OpenAPI specification at `http://localhost:8000/openapi.json`

3. **File Processing**
   - Upload files through the web interface
   - View processing results in real-time
   - Download processed files
   - Delete files when no longer needed

## Error Handling

The system implements comprehensive error handling:

1. **File Validation**
   - Type checking
   - Size limits
   - Content validation

2. **Processing Errors**
   - Graceful failure handling
   - Error logging
   - User-friendly error messages

3. **System Errors**
   - Database connection issues
   - File system errors
   - Network problems

## Performance Considerations

1. **Optimization**
   - Asynchronous processing
   - Efficient file handling
   - Database indexing

2. **Resource Management**
   - Memory usage optimization
   - File cleanup
   - Connection pooling

## Future Enhancements

1. **Planned Features**
   - Additional file type support
   - Advanced content analysis
   - User authentication
   - Batch processing

2. **Scalability**
   - Distributed processing
   - Load balancing
   - Cloud storage integration

## Contributing

1. **Development Setup**
   - Fork the repository
   - Create a feature branch
   - Submit pull requests

2. **Code Standards**
   - Follow PEP 8 guidelines
   - Write unit tests
   - Document new features

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check the documentation
2. Open an issue on GitHub
3. Contact the development team


OUTPUT:
![2025-06-05](https://github.com/user-attachments/assets/b7958418-6ac9-450f-85a8-836224788fe5)

1.INPUTS AND OUTPUTS:

   
