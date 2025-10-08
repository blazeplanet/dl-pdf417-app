from mangum import Mangum
from .generate import app

# Create handler for AWS Lambda / Vercel
handler = Mangum(app)
