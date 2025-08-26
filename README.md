# 🆔 PDF417 Driver's License Generator

A modern web application that generates PDF417 barcodes from driver's license form data. Built with FastAPI, vanilla JavaScript, and deployed on Vercel.

![PDF417 Generator Demo](https://raw.githubusercontent.com/blazeplanet/dl-pdf417-app/main/public/pdf417-demo.png)

## ✨ Features

- 📋 **Interactive Form**: Clean, responsive driver's license form interface
- 🔄 **PDF417 Generation**: Convert form data to ANSI format and generate PDF417 barcodes
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices
- 📥 **Download Support**: Download generated barcodes as PNG images
- 📋 **Copy to Clipboard**: One-click copy functionality for generated barcodes
- ✅ **Form Validation**: Client-side validation with helpful error messages
- 🧪 **Demo Data**: Quick-fill with sample data for testing (localhost only)
- 🎨 **Modern UI**: Beautiful gradient design with smooth animations

## 🏗️ Tech Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python FastAPI (serverless functions)
- **PDF417 Generation**: `pdf417gen` library
- **Image Processing**: Pillow (PIL)
- **Deployment**: Vercel
- **Version Control**: Git + GitHub

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ 
- Node.js 18+ (for Vercel CLI)
- Git

### Local Development

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd dl-pdf417-app
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

4. **Run local development server:**
   ```bash
   vercel dev
   ```

5. **Open your browser:**
   Navigate to `http://localhost:3000`

### Testing the Application

1. Fill out the driver's license form with valid data
2. Click "Generate PDF417 Barcode"
3. View the generated barcode and download if needed
4. Use the "Fill Demo Data" button (localhost only) for quick testing

## 📁 Project Structure

```
dl-pdf417-app/
├── api/
│   ├── generate.py          # FastAPI serverless function
│   └── generate_pdf417.py   # Original PDF417 generation script
├── public/
│   ├── index.html          # Main application page
│   ├── styles.css          # Responsive CSS styles
│   └── app.js              # Frontend JavaScript logic
├── vercel.json             # Vercel deployment configuration
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🔧 API Endpoints

### `POST /api/generate`

Generate a PDF417 barcode from driver's license data.

**Request Body:**
```json
{
  "dl_number": "091076664",
  "first_name": "STANLEY",
  "last_name": "Crooms",
  "middle_name": "David",
  "address": "2110 Old Maple Ln",
  "city": "Durham",
  "zip_code": "37745",
  "sex": "M",
  "height_inches": "69",
  "birth_date": "04151988",
  "issue_date": "07282025",
  "expiry_date": "07282033",
  "eye_color": "HAZ",
  "dl_class": "D",
  "donor": "No",
  "restrictions": "NONE",
  "endorsement": "NONE"
}
```

**Response:**
```json
{
  "success": true,
  "barcode": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "ansi_data": "@\n\nANSI 636053060002DL00410257ZT02980037DL\nDAQ091076664\n...",
  "image_size": [400, 200]
}
```

## 🌍 Deployment

This application is configured for automatic deployment on Vercel:

### Deploy to Vercel

1. **Connect GitHub Repository:**
   - Visit [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Vercel will automatically detect the project settings

2. **Configure Environment:**
   - No environment variables required for basic functionality
   - Python runtime is automatically detected

3. **Deploy:**
   - Push to `main` branch for automatic deployment
   - Or use `vercel --prod` for manual deployment

### Manual Deployment Steps

```bash
# Login to Vercel
vercel login

# Deploy to production
vercel --prod

# Follow the prompts to configure your project
```

## 🛠️ Configuration

### Vercel Configuration (`vercel.json`)

```json
{
  "version": 2,
  "functions": {
    "api/generate.py": { 
      "runtime": "python3.9"
    }
  },
  "routes": [
    { "src": "/api/(.*)", "dest": "/api/generate.py" },
    { "handle": "filesystem" },
    { "src": "/(.*)", "dest": "/public/$1" }
  ]
}
```

### Python Dependencies (`requirements.txt`)

```
fastapi==0.104.1
pdf417gen==0.8.1
pillow==10.0.1
uvicorn==0.24.0
```

## 🎯 Form Validation

The application includes comprehensive form validation:

- **Required Fields**: All essential driver's license fields must be filled
- **Date Format**: Dates must be in MMDDYYYY format (e.g., 04151988)
- **Zip Code**: Must be exactly 5 digits
- **Height**: Must be between 36-96 inches
- **Real-time Feedback**: Immediate validation with helpful error messages

## 📱 Responsive Design

The application is fully responsive and works on:

- **Desktop**: Full-featured experience with grid layout
- **Tablet**: Adaptive layout with touch-friendly controls
- **Mobile**: Single-column layout optimized for small screens

## 🔒 Security Considerations

- Client-side validation only (server-side validation recommended for production)
- No sensitive data storage (form data is processed in memory only)
- CORS headers configured for cross-origin requests
- Input sanitization through Pydantic models

## 🐛 Troubleshooting

### Common Issues

1. **API not working locally:**
   - Ensure Python dependencies are installed: `pip install -r requirements.txt`
   - Check that `vercel dev` is running on port 3000

2. **Barcode not generating:**
   - Verify all required fields are filled
   - Check browser console for JavaScript errors
   - Ensure date formats are correct (MMDDYYYY)

3. **Styling issues:**
   - Clear browser cache and refresh
   - Check that `styles.css` is loading properly

### Development Tips

- Use the "Fill Demo Data" button for quick testing on localhost
- Open browser developer tools to view API requests/responses
- Check the Network tab for any failed requests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PDF417Gen**: Python library for PDF417 barcode generation
- **FastAPI**: Modern Python web framework
- **Vercel**: Deployment platform
- **ANSI D20**: Driver's license data standard

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](../../issues) page
2. Create a new issue with detailed information
3. Include browser console output and steps to reproduce

---

**Built with 💻 by [Your Name] using FastAPI, PDF417Gen, and deployed on Vercel**
