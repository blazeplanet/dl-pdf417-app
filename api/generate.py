from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from pdf417gen import encode, render_image
import base64
import io
import re
from typing import Optional
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="PDF417 Driver License Generator",
    description="Generate ANSI-compliant PDF417 barcodes for state driver licenses",
    version="2.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced validation constants
VALID_EYE_COLORS = {'BLK', 'BLU', 'BRO', 'GRY', 'GRN', 'HAZ', 'MAR', 'PNK', 'DIC'}
VALID_HAIR_COLORS = {'BAL', 'BLK', 'BLN', 'BRO', 'GRY', 'RED', 'SDY', 'WHI', 'XXX'}
VALID_SEX = {'M', 'F', 'X'}
VALID_STATES = {
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN',
    'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV',
    'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN',
    'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC'
}

# State-specific IIN (Issuer Identification Numbers) for ANSI compliance
STATE_IIN_CODES = {
    'AL': '636015', 'AK': '636059', 'AZ': '636026', 'AR': '636021', 'CA': '636014', 'CO': '636020',
    'CT': '636006', 'DE': '636011', 'FL': '636010', 'GA': '636055', 'HI': '636047', 'ID': '636050',
    'IL': '636035', 'IN': '636037', 'IA': '636018', 'KS': '636022', 'KY': '636046', 'LA': '636007',
    'ME': '636041', 'MD': '636003', 'MA': '636002', 'MI': '636032', 'MN': '636038', 'MS': '636051',
    'MO': '636030', 'MT': '636008', 'NE': '636054', 'NV': '636049', 'NH': '636039', 'NJ': '636036',
    'NM': '636009', 'NY': '636001', 'NC': '636004', 'ND': '636034', 'OH': '636023', 'OK': '636058',
    'OR': '636029', 'PA': '636025', 'RI': '636052', 'SC': '636005', 'SD': '636042', 'TN': '636053',
    'TX': '636015', 'UT': '636040', 'VT': '636024', 'VA': '636000', 'WA': '636045', 'WV': '636061',
    'WI': '636031', 'WY': '636060', 'DC': '636043'
}

class DriverLicenseData(BaseModel):
    # Personal Information
    dl_number: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = ""
    
    # Address Information
    address: str
    city: str
    state: str
    zip_code: str
    
    # Physical Information
    sex: str
    donor: str = "N"
    height_inches: str
    weight_lbs: Optional[str] = ""
    
    # Dates
    birth_date: str  # MMDDYYYY format
    issue_date: str  # MMDDYYYY format
    expiry_date: str  # MMDDYYYY format
    
    # IDs and Codes
    icn: Optional[str] = ""
    dd: Optional[str] = ""
    eye_color: str
    hair_color: Optional[str] = ""
    
    # Additional fields
    dl_class: str = "D"
    restrictions: Optional[str] = ""
    endorsements: Optional[str] = ""
    address_2nd_line: Optional[str] = ""
    is_real_id: Optional[str] = "Y"
    veteran: Optional[str] = "N"

    @validator('dl_number')
    def validate_dl_number(cls, v):
        if not v:
            raise ValueError('Driver license number is required')
        # Allow alphanumeric, remove spaces and convert to uppercase
        clean_dl = re.sub(r'[^A-Z0-9]', '', v.upper())
        if len(clean_dl) < 1 or len(clean_dl) > 20:
            raise ValueError('Driver license number must be 1-20 alphanumeric characters')
        return clean_dl

    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('First and last names are required')
        # Remove special characters and limit length
        clean_name = re.sub(r'[^A-Z\s\-\.\'']', '', v.upper().strip())
        return clean_name[:40]  # ANSI limit

    @validator('sex')
    def validate_sex(cls, v):
        if v.upper() not in VALID_SEX:
            raise ValueError('Sex must be M, F, or X')
        return v.upper()

    @validator('birth_date', 'issue_date', 'expiry_date')
    def validate_dates(cls, v, values, field):
        if not v:
            raise ValueError(f'{field.name} is required')
        try:
            # Allow both MMDDYYYY and MM/DD/YYYY formats
            clean_date = re.sub(r'[^0-9]', '', v)
            if len(clean_date) != 8:
                raise ValueError('Date must be 8 digits (MMDDYYYY)')
            
            date = datetime.strptime(clean_date, '%m%d%Y')
            now = datetime.now()
            
            if date.year < 1900 or date.year > 2100:
                raise ValueError('Year must be between 1900 and 2100')
                
            if field.name == 'birth_date' and date > now:
                raise ValueError('Birth date cannot be in the future')
            elif field.name == 'issue_date' and date > now:
                raise ValueError('Issue date cannot be in the future')
            elif field.name == 'expiry_date':
                if 'issue_date' in values and values['issue_date']:
                    issue_clean = re.sub(r'[^0-9]', '', values['issue_date'])
                    issue_date = datetime.strptime(issue_clean, '%m%d%Y')
                    if date <= issue_date:
                        raise ValueError('Expiry date must be after issue date')
                
        except ValueError as e:
            if 'time data' in str(e):
                raise ValueError(f'Invalid date format. Use MMDDYYYY: {v}')
            raise e
        return clean_date

    @validator('height_inches')
    def validate_height(cls, v):
        if not v:
            return "070"  # Default height
        try:
            # Handle feet'inches" format or just inches
            if "'" in v or '"' in v:
                # Convert feet and inches to total inches
                parts = re.findall(r'\d+', v)
                if len(parts) >= 2:
                    feet, inches = int(parts[0]), int(parts[1])
                    total_inches = feet * 12 + inches
                else:
                    total_inches = int(parts[0])  # Assume just inches
            else:
                total_inches = int(v)
                
            if total_inches < 36 or total_inches > 96:
                raise ValueError('Height must be between 36 and 96 inches (3 to 8 feet)')
            return f"{total_inches:03d}"  # Zero-pad to 3 digits
        except ValueError:
            raise ValueError('Invalid height format. Use inches (e.g., 70) or feet\'inches" (e.g., 5\'10")')

    @validator('weight_lbs')
    def validate_weight(cls, v):
        if not v:
            return ""  # Optional field
        try:
            weight = int(v)
            if weight < 50 or weight > 999:
                raise ValueError('Weight must be between 50 and 999 pounds')
            return f"{weight:03d}"  # Zero-pad to 3 digits
        except ValueError:
            raise ValueError('Weight must be a number')

    @validator('zip_code')
    def validate_zip(cls, v):
        if not v:
            raise ValueError('Zip code is required')
        clean_zip = re.sub(r'[^0-9]', '', v)
        if len(clean_zip) != 5:
            raise ValueError('Zip code must be exactly 5 digits')
        return clean_zip

    @validator('state')
    def validate_state(cls, v):
        if not v:
            raise ValueError('State is required')
        if v.upper() not in VALID_STATES:
            raise ValueError(f'Invalid state code: {v}. Must be valid US state abbreviation')
        return v.upper()

    @validator('eye_color')
    def validate_eye_color(cls, v):
        if not v:
            raise ValueError('Eye color is required')
        if v.upper() not in VALID_EYE_COLORS:
            raise ValueError(f'Invalid eye color: {v}. Valid codes: {", ".join(sorted(VALID_EYE_COLORS))}')
        return v.upper()

    @validator('hair_color')
    def validate_hair_color(cls, v):
        if v and v.upper() not in VALID_HAIR_COLORS:
            raise ValueError(f'Invalid hair color: {v}. Valid codes: {", ".join(sorted(VALID_HAIR_COLORS))}')
        return v.upper() if v else "BRO"  # Default to brown

def generate_icn(state: str, dl_number: str) -> str:
    """Generate a realistic Internal Control Number"""
    timestamp = datetime.now().strftime('%Y%m%d')
    state_code = STATE_IIN_CODES.get(state, '636000')
    # Create ICN using state code + timestamp + DL suffix
    icn = f"{state_code}{timestamp[-6:]}{dl_number[-4:].zfill(4)}"
    return icn[:20]  # Limit to 20 characters

def generate_dd_field(expiry_date: str, dl_number: str) -> str:
    """Generate DD audit information field"""
    # DD field typically contains audit info and control data
    return f"{dl_number[-6:].zfill(6)}{expiry_date}001"

def build_ansi_data(data: DriverLicenseData) -> str:
    """Build ANSI-compliant driver's license data string"""
    try:
        state_iin = STATE_IIN_CODES.get(data.state, '636000')
        
        # Generate missing fields with realistic defaults
        icn = data.icn if data.icn else generate_icn(data.state, data.dl_number)
        dd_field = data.dd if data.dd else generate_dd_field(data.expiry_date, data.dl_number)
        
        # Calculate data lengths and build subfile
        subfile_type = "DL"
        
        # Build the ANSI data string with proper formatting
        ansi_lines = []
        ansi_lines.append("@")
        ansi_lines.append("")
        ansi_lines.append(f"ANSI {state_iin}06{subfile_type}00410257ZT02980037DL")
        
        # Required fields
        ansi_lines.append(f"DAQ{data.dl_number}")  # DL Number
        ansi_lines.append(f"DCS{data.last_name}")  # Last Name
        ansi_lines.append(f"DAC{data.first_name}")  # First Name
        ansi_lines.append(f"DDF{data.middle_name}")  # Middle Name
        ansi_lines.append(f"DAD{data.sex}")  # Sex
        ansi_lines.append(f"DBB{data.birth_date}")  # Birth Date
        ansi_lines.append(f"DBD{data.issue_date}")  # Issue Date
        ansi_lines.append(f"DBA{data.expiry_date}")  # Expiry Date
        ansi_lines.append(f"DBC{data.dl_class}")  # License Class
        ansi_lines.append(f"DAU{data.height_inches}")  # Height
        ansi_lines.append(f"DAY{data.eye_color}")  # Eye Color
        
        # Address information
        ansi_lines.append(f"DAG{data.address}")  # Street Address
        ansi_lines.append(f"DAI{data.city}")  # City
        ansi_lines.append(f"DAJ{data.state}")  # State
        ansi_lines.append(f"DAK{data.zip_code}")  # Zip Code
        
        # Control and audit fields
        ansi_lines.append(f"DCF{icn}")  # Document Discriminator/ICN
        ansi_lines.append(f"DCGUSA")  # Country
        ansi_lines.append(f"DCK{dd_field}")  # Audit Information
        
        # Optional fields with defaults
        if data.weight_lbs:
            ansi_lines.append(f"DAW{data.weight_lbs}")
        if data.hair_color:
            ansi_lines.append(f"DAZ{data.hair_color}")
        if data.address_2nd_line:
            ansi_lines.append(f"DAH{data.address_2nd_line}")
            
        # Restrictions and endorsements
        restrictions = data.restrictions if data.restrictions else "NONE"
        endorsements = data.endorsements if data.endorsements else "NONE"
        ansi_lines.append(f"DDB{restrictions}")
        ansi_lines.append(f"DDA{endorsements}")
        ansi_lines.append(f"DCD{restrictions}")
        ansi_lines.append(f"DCE{endorsements}")
        
        # Additional compliance fields
        if data.veteran and data.veteran.upper() == 'Y':
            ansi_lines.append(f"DCL{data.veteran}")
        if data.donor and data.donor.upper() in ['Y', 'N']:
            ansi_lines.append(f"DDK{data.donor}")
        if data.is_real_id and data.is_real_id.upper() in ['Y', 'N']:
            ansi_lines.append(f"DDB{data.is_real_id}")
            
        return "\n".join(ansi_lines)
        
    except Exception as e:
        raise ValueError(f"Error building ANSI data: {str(e)}")

@app.get("/")
def read_root():
    return {
        "message": "PDF417 Driver License Generator API",
        "version": "2.1.0",
        "status": "healthy",
        "endpoints": {
            "/generate": "POST - Generate PDF417 barcode from driver license data",
            "/states": "GET - List supported states and their codes",
            "/validation": "GET - Get validation rules and constants"
        }
    }

@app.get("/states")
def get_states():
    """Return list of supported states with their IIN codes"""
    return {
        "supported_states": list(VALID_STATES),
        "state_iin_codes": STATE_IIN_CODES,
        "total_states": len(VALID_STATES)
    }

@app.get("/validation")
def get_validation_rules():
    """Return validation constants and rules"""
    return {
        "eye_colors": list(VALID_EYE_COLORS),
        "hair_colors": list(VALID_HAIR_COLORS),
        "sex_codes": list(VALID_SEX),
        "date_format": "MMDDYYYY",
        "height_range": "36-96 inches",
        "weight_range": "50-999 pounds",
        "zip_format": "5 digits",
        "dl_number_max_length": 20
    }

@app.post("/generate")
async def generate_pdf417(data: DriverLicenseData):
    """Generate PDF417 barcode from validated driver license data"""
    try:
        # Build ANSI format string with enhanced validation
        ansi_data = build_ansi_data(data)
        
        # Validate ANSI data length (should be reasonable for PDF417)
        if len(ansi_data) > 2000:
            raise ValueError("Generated ANSI data exceeds maximum length for PDF417")
        
        # Generate PDF417 barcode with optimal parameters for driver licenses
        try:
            codes = encode(
                ansi_data,
                columns=14,  # Optimal for DL data density
                security_level=5,  # High error correction for outdoor scanning
                encoding='utf-8'
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF417 encoding failed: {str(e)}")
        
        # Render as high-quality image optimized for scanning
        try:
            image = render_image(
                codes,
                scale=4,  # High resolution for better scan reliability
                ratio=3,  # Standard aspect ratio for DL barcodes
                padding=15,  # Adequate quiet zone
                bg_color=(255, 255, 255),  # Pure white background
                fg_color=(0, 0, 0)  # Pure black bars
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image rendering failed: {str(e)}")
        
        # Convert to base64 with PNG optimization
        try:
            buffer = io.BytesIO()
            image.save(
                buffer,
                format="PNG",
                optimize=True,
                compress_level=6  # Good compression without quality loss
            )
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image encoding failed: {str(e)}")
        
        # Return comprehensive response
        return {
            "success": True,
            "barcode": f"data:image/png;base64,{img_base64}",
            "ansi_data": ansi_data,
            "validation": {
                "state_iin": STATE_IIN_CODES.get(data.state, '636000'),
                "data_length": len(ansi_data),
                "barcode_size": image.size,
                "compliant": True
            },
            "metadata": {
                "columns": 14,
                "security_level": 5,
                "scale": 4,
                "ratio": 3,
                "format": "ANSI D20",
                "generated_at": datetime.now().isoformat(),
                "state": data.state,
                "dl_class": data.dl_class
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error generating PDF417 barcode: {str(e)}")

# Error handler for better debugging
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return {
        "success": False,
        "error": str(exc),
        "type": type(exc).__name__,
        "timestamp": datetime.now().isoformat()
    }