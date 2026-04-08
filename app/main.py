from fastapi import FastAPI
from app.database import Base, engine
from app.routes import router

# Create all database tables defined in models if they don't exist yet
Base.metadata.create_all(bind=engine)

# Initialize the FastAPI app
app = FastAPI()

# Register the routes from routes.py so the app knows about our endpoints
app.include_router(router)
