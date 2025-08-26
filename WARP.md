# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Essential Development Commands

### Environment Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Vercel CLI globally 
npm install -g vercel

# Verify Python version (requires 3.9+)
python --version
```

### Local Development
```bash
# Start local development server with hot-reload
vercel dev

# Alternative: Run FastAPI directly for API-only development
uvicorn api.generate:app --reload --port 8000

# Access application at http://localhost:3000
# API documentation at http://localhost:3000/api/docs (when running uvicorn directly)
```

### Testing & Quality
```bash
# Run tests (when implemented)
pytest tests/ -v

# Format Python code (recommended setup)
black api/
isort api/

# Lint Python code
flake8 api/
```

### Deployment
```bash
# Deploy to production
vercel --prod

# Deploy preview (automatic on PR)
vercel

# Check deployment status
vercel ls
```

## Architecture Overview

This is a **stateless web application** with a clear frontend/backend separation designed for Vercel's serverless platform:

### Frontend Layer
- **Static Assets**: `public/` directory served directly by Vercel CDN
- **Vanilla JavaScript**: No framework dependencies, direct DOM manipulation
- **Responsive Design**: CSS Grid/Flexbox with mobile-first approach
- **Client-Side Validation**: Real-time form validation with user feedback

### Backend Layer
- **Serverless Function**: `api/generate.py` runs as Vercel Python function
- **FastAPI Framework**: Provides request validation, CORS, and API documentation
- **Stateless Processing**: Each request is independent, no session storage

### Data Flow
1. **Form Submission** → JavaScript collects form data
2. **API Request** → `fetch('/api/generate')` with JSON payload  
3. **ANSI Conversion** → `build_ansi_data()` formats to ANSI D20 standard
4. **Barcode Generation** → `pdf417gen` creates barcode matrix
5. **Image Rendering** → PIL renders to PNG with quality settings
6. **Base64 Encoding** → Image converted for inline display
7. **Response Handling** → Frontend updates DOM with barcode image

### Key Technical Considerations
- **Cold Starts**: Python functions may have ~1-2s initial latency
- **CORS Configuration**: Wide-open for development (`allow_origins=["*"]`)
- **Memory Constraints**: Vercel functions limited to 1024MB
- **Execution Time**: 10s timeout for serverless functions

## Project Structure & Component Relationships

```
dl-pdf417-app/
├── api/
│   ├── generate.py           # FastAPI serverless function (main backend)
│   └── generate_pdf417.py    # Original script (reference implementation)
├── public/
│   ├── index.html           # Main UI with driver's license form
│   ├── styles.css           # Responsive styling with CSS Grid
│   └── app.js               # Frontend logic, validation, API calls
├── vercel.json              # Deployment configuration
├── requirements.txt         # Python dependencies
└── README.md               # User documentation
```

### Component Relationships
- **`app.js`** → Calls **`/api/generate`** → Executes **`generate.py`**
- **`generate.py`** → Uses **`build_ansi_data()`** → Calls **`pdf417gen`** library
- **Form validation** in `app.js` mirrors **Pydantic model** validation in `generate.py`
- **Height conversion utility** (inches ↔ cm) provides real-time user feedback
- **Copy-to-clipboard** functionality uses modern Clipboard API with fallbacks

## Development Workflow & Testing

### Recommended Development Flow
1. **Feature Branch**: `git checkout -b feature/barcode-enhancement`
2. **Local Testing**: `vercel dev` for full-stack testing
3. **API Testing**: Use browser dev tools or curl for endpoint testing
4. **Frontend Testing**: Browser dev tools for validation, responsive design
5. **Preview Deploy**: Automatic on PR creation
6. **Production Deploy**: Merge to `main` triggers automatic deployment

### Testing Strategy (Recommended Implementation)
```bash
# Unit tests for ANSI data formatting
pytest tests/test_ansi_builder.py

# Integration tests for API endpoints  
pytest tests/test_api.py --httpx-base-url=http://localhost:3000

# Frontend validation testing
# Use browser automation or manual testing checklist
```

### Development Tools
- **Browser Dev Tools**: Essential for frontend debugging and API inspection
- **Vercel CLI**: `vercel logs` for function debugging
- **Python REPL**: Test ANSI formatting and PDF417 generation interactively

## Vercel Deployment Configuration

### `vercel.json` Breakdown
```json
{
  "version": 2,
  "builds": [
    {
      "src": "public/**/*",      // Static files build
      "use": "@vercel/static"
    },
    {
      "src": "api/generate.py",   // Python serverless function
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",         // Route API calls to Python function
      "dest": "/api/generate.py"
    },
    {
      "src": "/(.*)",            // All other requests serve static files
      "dest": "/public/$1"
    }
  ]
}
```

### Deployment Notes
- **No Environment Variables**: App requires no secrets or configuration
- **Python Runtime**: Automatically detected as 3.9+ from `requirements.txt`
- **Build Process**: Vercel installs dependencies and builds functions automatically
- **GitHub Integration**: Push to `main` triggers production deployment
- **Preview Deployments**: Every PR gets a unique preview URL

## PDF417 Generation & ANSI Technical Notes

### PDF417 Generation Pipeline
```python
# Key parameters in api/generate.py
codes = encode(ansi_data)                    # pdf417gen encoding
image = render_image(codes, scale=3, ratio=3) # PIL image rendering
```

**Parameters Impact:**
- **`scale=3`**: Controls barcode module size (higher = larger image)
- **`ratio=3`**: Module height-to-width ratio (affects readability)
- **Final Size**: Typically ~400x200px for driver's license data

### ANSI D20 Driver's License Standard
The `build_ansi_data()` function implements key ANSI fields:

```
DAQ{dl_number}      # Driver License Number
DCS{last_name}      # Customer Last Name  
DAC{first_name}     # Customer First Name
DAD{sex}            # Sex (M/F)
DBB{birth_date}     # Date of Birth (MMDDYYYY)
DBA{expiry_date}    # License Expiry Date
DAU{height_inches}  # Height in Inches (zero-padded to 3 digits)
DAY{eye_color}      # Eye Color (HAZ, BLU, BRN, etc.)
```

### Form Validation Rules
- **Dates**: Must be MMDDYYYY format (e.g., "04151988")
- **Zip Code**: Exactly 5 digits
- **Height**: 36-96 inches (validated range)
- **Required Fields**: All essential DL fields must be populated

### Customization Points
- **Barcode Quality**: Adjust `scale` and `ratio` in `render_image()`
- **Add ANSI Fields**: Extend `DriverLicenseData` model and `build_ansi_data()`
- **Validation Rules**: Modify `validateForm()` in `app.js` and Pydantic model
- **Image Format**: PIL supports multiple formats (PNG, JPEG, etc.)

### Common PDF417 Issues
- **Scanning Problems**: Increase `scale` parameter for better resolution
- **Size Constraints**: Large datasets may hit Vercel function memory limits
- **ANSI Compliance**: Verify field codes against official ANSI D20 specification
