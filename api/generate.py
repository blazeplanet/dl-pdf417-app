from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pdf417gen import encode, render_image
import base64
import io
from typing import Optional

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

class DriverLicenseData(BaseModel):
    # Personal Information
    dl_number: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = ""
    
    # Address Information
    address: str
    city: str
    zip_code: str
    
    # Physical Information
    sex: str
    donor: str = "No"
    height_inches: str
    
    # Dates
    birth_date: str  # MMDDYYYY format
    issue_date: str  # MMDDYYYY format
    expiry_date: str  # MMDDYYYY format
    
    # IDs and Codes
    icn: Optional[str] = ""
    dd: Optional[str] = ""
    eye_color: str = "HAZ"
    
    # Additional fields
    dl_class: str = "D"
    restrictions: str = "NONE"
    endorsement: str = "NONE"
    address_2nd_line: Optional[str] = ""
    is_real_id: str = "Yes"

def build_ansi_data(data: DriverLicenseData) -> str:
    """Convert form data to ANSI driver's license format"""
    
    # ANSI header and format
    ansi_data = f"""@

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
DAU{data.height_inches.zfill(3)}
DAY{data.eye_color}
DAG{data.address}
DAI{data.city}
DAJTN
DAK{data.zip_code}
DCF{data.icn if data.icn else "252090372892550101"}
DCGUSA
DCK{data.dd if data.dd else "110250728203364"}
DDB{data.restrictions}
DDA{data.endorsement}
DCD{data.restrictions}
DCE{data.endorsement}"""
    
    return ansi_data

@app.get("/")
def read_root():
    return {"message": "PDF417 Generator API is running"}

@app.post("/generate")
async def generate_pdf417(data: DriverLicenseData):
    try:
        # Build ANSI format string
        ansi_data = build_ansi_data(data)
        
        # Generate PDF417 barcode
        codes = encode(ansi_data)
        
        # Render as image with good quality settings
        image = render_image(codes, scale=3, ratio=3)
        
        # Convert image to base64
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "success": True,
            "barcode": f"data:image/png;base64,{img_base64}",
            "ansi_data": ansi_data,
            "image_size": image.size
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF417 barcode: {str(e)}")

# For Vercel serverless function compatibility
def handler(request):
    return app(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
