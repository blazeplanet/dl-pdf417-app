# PDF417 Driver License Generator 🆔

A robust, ANSI-compliant PDF417 barcode generator specifically designed for US state driver licenses. This application generates high-quality PDF417 barcodes that match the format and standards used by state DMVs.

## ✨ Features

- **ANSI D20 Compliant**: Generates barcodes following official ANSI standards
- **50+ States Supported**: All US states with correct IIN codes
- **Comprehensive Validation**: Input validation for all driver license fields
- **High-Quality Output**: Optimized for scanning with proper error correction
- **Real-time Generation**: Fast API with instant barcode creation
- **State-Specific**: Correct formatting for each state's requirements
- **Error Handling**: Robust validation and clear error messages

## 🚀 Live Demo

**API Endpoint**: `https://dl-pdf417-app.vercel.app`

### Quick Test
```bash
curl -X POST https://dl-pdf417-app.vercel.app/generate \
  -H "Content-Type: application/json" \
  -d '{
    "dl_number": "091076664",
    "first_name": "JOHN",
    "last_name": "DOE",
    "address": "123 MAIN ST",
    "city": "NASHVILLE",
    "state": "TN",
    "zip_code": "37203",
    "sex": "M",
    "height_inches": "72",
    "birth_date": "01151990",
    "issue_date": "10012023",
    "expiry_date": "10012028",
    "eye_color": "BRO"
  }'
```

## 📚 API Documentation

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API health and info |
| `/generate` | POST | Generate PDF417 barcode |
| `/states` | GET | List supported states |
| `/validation` | GET | Get validation rules |

### Generate Barcode

**POST** `/generate`

#### Required Fields
```json
{
  "dl_number": "string (1-20 chars)",
  "first_name": "string",
  "last_name": "string",
  "address": "string",
  "city": "string",
  "state": "string (2-letter code)",
  "zip_code": "string (5 digits)",
  "sex": "M|F|X",
  "height_inches": "string (36-96)",
  "birth_date": "string (MMDDYYYY)",
  "issue_date": "string (MMDDYYYY)",
  "expiry_date": "string (MMDDYYYY)",
  "eye_color": "string (BLK|BLU|BRO|GRY|GRN|HAZ|MAR|PNK)"
}
```

#### Optional Fields
```json
{
  "middle_name": "string",
  "weight_lbs": "string (50-999)",
  "hair_color": "string (BAL|BLK|BLN|BRO|GRY|RED|SDY|WHI)",
  "dl_class": "string (default: D)",
  "restrictions": "string",
  "endorsements": "string",
  "address_2nd_line": "string",
  "donor": "Y|N (default: N)",
  "veteran": "Y|N (default: N)",
  "is_real_id": "Y|N (default: Y)",
  "icn": "string (auto-generated if empty)",
  "dd": "string (auto-generated if empty)"
}
```

#### Response Format
```json
{
  "success": true,
  "barcode": "data:image/png;base64,iVBORw0KGgo...",
  "ansi_data": "@\n\nANSI 636053060...",
  "validation": {
    "state_iin": "636053",
    "data_length": 245,
    "barcode_size": [520, 200],
    "compliant": true
  },
  "metadata": {
    "columns": 14,
    "security_level": 5,
    "scale": 4,
    "ratio": 3,
    "format": "ANSI D20",
    "generated_at": "2025-10-09T17:30:00Z",
    "state": "TN",
    "dl_class": "D"
  }
}
```

## 📝 Field Reference

### Eye Color Codes
- `BLK` - Black
- `BLU` - Blue  
- `BRO` - Brown
- `GRY` - Gray
- `GRN` - Green
- `HAZ` - Hazel
- `MAR` - Maroon
- `PNK` - Pink
- `DIC` - Dichromatic

### Hair Color Codes
- `BAL` - Bald
- `BLK` - Black
- `BLN` - Blond
- `BRO` - Brown
- `GRY` - Gray
- `RED` - Red
- `SDY` - Sandy
- `WHI` - White
- `XXX` - Unknown

### Height Format
- **Inches only**: `"72"` (72 inches)
- **Feet and inches**: `"6'0"` or `"6'0\"` (6 feet 0 inches)
- **Range**: 36-96 inches (3-8 feet)

### Date Format
- **Format**: `MMDDYYYY`
- **Examples**: 
  - `"01151990"` (January 15, 1990)
  - `"12252025"` (December 25, 2025)

## 📊 State Support

All 50 US states plus DC supported with correct IIN codes:

| State | IIN Code | State | IIN Code | State | IIN Code |
|-------|----------|-------|----------|-------|-----------|
| AL | 636015 | AK | 636059 | AZ | 636026 |
| AR | 636021 | CA | 636014 | CO | 636020 |
| CT | 636006 | DE | 636011 | FL | 636010 |
| GA | 636055 | HI | 636047 | ID | 636050 |
| IL | 636035 | IN | 636037 | IA | 636018 |
| KS | 636022 | KY | 636046 | LA | 636007 |
| ME | 636041 | MD | 636003 | MA | 636002 |
| MI | 636032 | MN | 636038 | MS | 636051 |
| MO | 636030 | MT | 636008 | NE | 636054 |
| NV | 636049 | NH | 636039 | NJ | 636036 |
| NM | 636009 | NY | 636001 | NC | 636004 |
| ND | 636034 | OH | 636023 | OK | 636058 |
| OR | 636029 | PA | 636025 | RI | 636052 |
| SC | 636005 | SD | 636042 | TN | 636053 |
| TX | 636015 | UT | 636040 | VT | 636024 |
| VA | 636000 | WA | 636045 | WV | 636061 |
| WI | 636031 | WY | 636060 | DC | 636043 |

## 🚀 Development

### Prerequisites
- Python 3.12+
- pip or pipenv

### Local Setup
```bash
# Clone the repository
git clone https://github.com/blazeplanet/dl-pdf417-app.git
cd dl-pdf417-app

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn api.generate:app --host 0.0.0.0 --port 8000 --reload
```

### Testing
```bash
# Run the comprehensive test suite
python test_api.py

# Test specific functionality
curl http://localhost:8000/
curl http://localhost:8000/states
curl http://localhost:8000/validation
```

### Deployment

The app is configured for Vercel deployment:

```bash
# Deploy to Vercel
vercel deploy

# Production deployment
vercel --prod
```

## 🔍 Technical Details

### ANSI Compliance
- **Standard**: ANSI/AAMVA DL/ID Card Design Standard
- **Version**: D20
- **Subfile**: DL (Driver License)
- **Security**: Level 5 error correction
- **Encoding**: UTF-8

### PDF417 Specifications
- **Columns**: 14 (optimized for DL data)
- **Error Correction**: Level 5 (high reliability)
- **Scale**: 4x (high resolution)
- **Aspect Ratio**: 3:1 (standard DL format)
- **Quiet Zone**: 15 pixels
- **Colors**: Black bars on white background

### Data Fields (ANSI Tags)
- `DAQ` - Driver License Number
- `DCS` - Last Name
- `DAC` - First Name
- `DDF` - Middle Name
- `DAD` - Sex
- `DBB` - Birth Date
- `DBA` - Expiry Date
- `DBD` - Issue Date
- `DBC` - License Class
- `DAU` - Height
- `DAY` - Eye Color
- `DAZ` - Hair Color
- `DAW` - Weight
- `DAG` - Address
- `DAI` - City
- `DAJ` - State
- `DAK` - Zip Code
- `DCF` - Document Discriminator/ICN
- `DCK` - Audit Information
- `DDB` - Restrictions
- `DDA` - Endorsements

## ⚠️ Important Notes

1. **Legal Use Only**: This tool is for educational, testing, and legitimate development purposes only
2. **Not for Fraud**: Creating fake identification documents is illegal
3. **Compliance**: Ensure compliance with local and federal laws
4. **Data Security**: Do not transmit sensitive personal information
5. **Testing**: Use fictitious data for testing purposes

## 🐛 Error Handling

The API provides detailed error messages for:
- **400**: Validation errors (invalid data format)
- **422**: Unprocessable entity (missing required fields)
- **500**: Server errors (PDF417 generation issues)

Example error response:
```json
{
  "success": false,
  "error": "Invalid eye color: PURPLE. Valid codes: BLK, BLU, BRO, GRY, GRN, HAZ, MAR, PNK",
  "type": "ValueError",
  "timestamp": "2025-10-09T17:30:00Z"
}
```

## 📜 Example Usage

### JavaScript (Frontend)
```javascript
const generateBarcode = async (licenseData) => {
  try {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(licenseData)
    });
    
    const result = await response.json();
    
    if (result.success) {
      // Display the barcode image
      document.getElementById('barcode').src = result.barcode;
      console.log('Generated ANSI data:', result.ansi_data);
    } else {
      console.error('Generation failed:', result.error);
    }
  } catch (error) {
    console.error('Request failed:', error);
  }
};
```

### Python (Backend)
```python
import requests
import json

def generate_pdf417(license_data):
    url = "https://dl-pdf417-app.vercel.app/generate"
    response = requests.post(url, json=license_data)
    
    if response.status_code == 200:
        result = response.json()
        return result['barcode']  # Base64 encoded image
    else:
        raise Exception(f"API Error: {response.text}")

# Example usage
license_data = {
    "dl_number": "D123456789",
    "first_name": "JANE",
    "last_name": "SMITH",
    # ... other required fields
}

barcode_image = generate_pdf417(license_data)
```

## 🔗 Resources

- [AAMVA DL/ID Card Design Standard](https://www.aamva.org/)
- [PDF417 Specification](https://en.wikipedia.org/wiki/PDF417)
- [ANSI D20 Standard](https://webstore.ansi.org/)
- [Vercel Documentation](https://vercel.com/docs)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

🚀 **Ready to generate ANSI-compliant PDF417 barcodes!** 🚀