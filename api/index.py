from mangum import Mangum
from .generate import app

# Create handler for Vercel serverless functions
handler = Mangum(app, lifespan="off")

# Export as default function for Vercel
def handler_func(event, context):
    return handler(event, context)

# Ensure the app is properly exposed
__all__ = ['handler', 'handler_func', 'app']