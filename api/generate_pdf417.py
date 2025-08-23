from pdf417gen import encode, render_image

# ANSI driver's license data
ansi_data = """@

ANSI 636053060002DL00410257ZT02980037DL
DAQ091076664
DCSCrooms
DACStanely
DADM
DDFDavid
DBB04151988
DBD07282025
DBA07282033
DBC1
DAU069
DAYHAZ
DAG2110 Old Maple Ln
DAIDurham
DAJTN
DAK37745
DCF252090372892550101
DCGUSA
DCK110250728203364
DDBNONE
DDANONE
DCDNONE
DCENONE"""

try:
    # Encode the data into PDF417 format
    codes = encode(ansi_data)
    
    # Render the PDF417 barcode as an image
    image = render_image(codes, scale=3, ratio=3)
    
    # Save the barcode image
    output_filename = "driver_license_pdf417.png"
    image.save(output_filename)
    
    print(f"PDF417 barcode successfully generated and saved as '{output_filename}'")
    print(f"Image size: {image.size}")
    
except Exception as e:
    print(f"Error generating PDF417 barcode: {e}")
