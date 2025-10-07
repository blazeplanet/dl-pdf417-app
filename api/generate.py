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
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants for validation
VALID_EYE_COLORS = {'BLK', 'BLU', 'BRO', 'GRY', 'GRN', 'HAZ', 'MAR', 'PNK'}
VALID_HAIR_COLORS = {'BAL', 'BLK', 'BLN', 'BRO', 'GRY', 'RED', 'SDY', 'WHI'}
VALID_STATES = {'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN',
                'IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV',
                'NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN',
                'TX','UT','VT','VA','WA','WV','WI','WY'}

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
    donor: str = "No"
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
    restrictions: str = ""
    endorsement: str = ""
    address_2nd_line: Optional[str] = ""
    is_real_id: str = "Yes"

    @validator('dl_number')
    def validate_dl_number(cls, v):
        if not re.match(r'^[A-Z0-9]{1,20}$', v.upper()):
            raise ValueError('Invalid driver license number format')
        return v.upper()

    @validator('birth_date', 'issue_date', 'expiry_date')
    def validate_dates(cls, v, values, field):
        try:
            date = datetime.strptime(v, '%m%d%Y')
            now = datetime.now()
            
            if date.year < 1900 or date.year > 2100:
                raise ValueError('Year must be between 1900 and 2100')
                
            if field.name == 'birth_date' and date > now:
                raise ValueError('Birth date cannot be in the future')
            elif field.name == 'issue_date' and date > now:
                raise ValueError('Issue date cannot be in the future')
            elif field.name == 'expiry_date':
                if 'issue_date' in values:
                    issue_date = datetime.strptime(values['issue_date'], '%m%d%Y')
                    if date <= issue_date:
                        raise ValueError('Expiry date must be after issue date')
                
        except ValueError as e:
            raise ValueError(f'Invalid date format. Must be MMDDYYYY: {str(e)}')
        return v

    @validator('height_inches')
    def validate_height(cls, v):
        try:
            height = int(v)
            if height < 36 or height > 96:
                raise ValueError('Height must be between 36 and 96 inches')
            return str(height).zfill(3)
        except ValueError:
            raise ValueError('Height must be a number')

    @validator('zip_code')
    def validate_zip(cls, v):
        if not re.match(r'^\d{5}$', v):
            raise ValueError('Zip code must be exactly 5 digits')
        return v

    @validator('state')
    def validate_state(cls, v):
        if v.upper() not in VALID_STATES:
            raise ValueError('Invalid state code')
        return v.upper()

    @validator('eye_color')
    def validate_eye_color(cls, v):
        if v.upper() not in VALID_EYE_COLORS:
            raise ValueError('Invalid eye color code')
        return v.upper()

    @validator('hair_color')
    def validate_hair_color(cls, v):
        if v and v.upper() not in VALID_HAIR_COLORS:
            raise ValueError('Invalid hair color code')
        return v.upper() if v else v

def build_ansi_data(data: DriverLicenseData) -> str:
    """Convert form data to ANSI driver's license format with enhanced error checking"""
    try:
        # Get current timestamp for header
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # Standard ANSI header
        ansi_data = f"""@\n
ANSI 636053060002DL00410257ZT02980037DL
DAQ{data.dl_number}
DCS{data.last_name}
DAC{data.first_name}
DAD{data.sex}
DDF{data.middle_name}
DBB{data.birth_date}
DBD{data.issue_date}
DBA{data.expiry_date}
DBC1
DAU{data.height_inches}
DAY{data.eye_color}
DAG{data.address}
DAI{data.city}
DAJ{data.state}
DAK{data.zip_code}
DCF{data.icn if data.icn else f"DL{timestamp}{data.dl_number[-6:]}"}
DCGUSA
DCK{data.dd if data.dd else f"DL{data.expiry_date}"}
DDB{data.restrictions if data.restrictions else "NONE"}
DDA{data.endorsement if data.endorsement else "NONE"}
DCD{data.restrictions if data.restrictions else "NONE"}
DCE{data.endorsement if data.endorsement else "NONE"}"""

        # Optional fields
        if data.weight_lbs:
            ansi_data += f"\nDAW{data.weight_lbs}"
        if data.hair_color:
            ansi_data += f"\nDAZ{data.hair_color}"
        if data.address_2nd_line:
            ansi_data += f"\nDAH{data.address_2nd_line}"

        return ansi_data
    except Exception as e:
        raise ValueError(f"Error building ANSI data: {str(e)}")

@app.get("/")
def read_root():
    return {
        "message": "PDF417 Generator API is running",
        "version": "2.0.0",
        "status": "healthy"
    }

@app.post("/generate")
async def generate_pdf417(data: DriverLicenseData):
    try:
        # Build ANSI format string with validation
        ansi_data = build_ansi_data(data)
        
        # Generate PDF417 barcode with optimal parameters
        try:
            codes = encode(
                ansi_data,
                columns=13,  # Optimal column count for DL data
                security_level=5,  # Higher security level for better error correction
                encoding='utf-8'
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF417 encoding failed: {str(e)}")
        
        # Render as image with optimized quality settings
        try:
            image = render_image(
                codes,
                scale=4,  # Increased scale for better scanning
                ratio=3,  # Standard height/width ratio
                padding=20,  # Added padding for better scanning
                bg_color=(255, 255, 255),  # White background
                fg_color=(0, 0, 0)  # Black foreground
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image rendering failed: {str(e)}")
        
        # Convert image to base64 with optimization
        try:
            buffer = io.BytesIO()
            image.save(
                buffer,
                format="PNG",
                optimize=True,
                quality=95
            )
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image encoding failed: {str(e)}")
        
        # Return successful response with metadata
        return {
            "success": True,
            "barcode": f"data:image/png;base64,{img_base64}",
            "ansi_data": ansi_data,
            "image_size": image.size,
            "metadata": {
                "columns": 13,
                "security_level": 5,
                "scale": 4,
                "ratio": 3,
                "generated_at": datetime.now().isoformat()
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF417 barcode: {str(e)}")
