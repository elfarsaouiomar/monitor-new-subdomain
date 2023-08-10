from fastapi import FastAPI, BackgroundTasks, APIRouter, status
from pymongo import MongoClient
from fastapi.responses import JSONResponse
import uvicorn
from src.mns import SubDomainMonitoring
from src.db.MnsRepository import MnsRepository
from src.config.Config import DB_HOST, DB_NAME, DB_PORT, DB_USER, DB_PWD, COLLECTION_NAME

client = MongoClient(host=DB_HOST, port=DB_PORT, username=DB_USER, password=DB_PWD, serverSelectionTimeoutMS=3000)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

mns = SubDomainMonitoring()
router = APIRouter(prefix="/v1")

def create_app():
    """
    Initialize the FastAPI() App
    """
    app = FastAPI()
    app.include_router(router, prefix="/api")
    return app

def helper(data):
    """
    Delete the _id from Mongo Collection
    """
    if data:
        data['id'] = str(data['_id'])
        del data['_id']
    return data

def response_with_success(message, code=status.HTTP_200_OK):
    """
    Create a JSON response for successful requests

    Args:
        message (str): Custom message
        code (int, optional): Status code, default is 200. 

    Returns:
        dict: Response content
    """
    return JSONResponse(status_code=code,
                        content={
                            "success": True,
                            "code": code,
                            "message": message
                        })

def response_with_error(message, code):
    """
    Create a JSON response for error requests

    Args:
        message (str): Custom message
        code (int): Status code

    Returns:
        dict: Response content
    """
    return JSONResponse(status_code=code,
                        content={
                            "success": False,
                            "code": code,
                            "message": message
                        })

async def list_subdomains_by_domain(domain: str):
    """
    Get all domains from the database.

    Args:
        domain (str): Domain name

    Returns:
        dict: Response content
    """
    subdomains = collection.find_one({"domain": domain})
    if subdomains is not None:
        return response_with_success(message=helper(subdomains), code=status.HTTP_200_OK)
    return response_with_error(message="not found", code=status.HTTP_404_NOT_FOUND)

@router.get("/ping")
async def index():
    """
    Endpoint for testing the API.
    """
    return response_with_success(message="pong", code=status.HTTP_200_OK)

async def get_domains():
    """
    Get all domains from the database.

    Returns:
        dict: Response content
    """
    domains = [target.get('domain') for target in collection.find()]
    return response_with_success(message=domains, code=status.HTTP_200_OK)

@router.get("/domains")
async def list_domains() -> list:
    """
    Endpoint for listing all domains in the database.
    """
    domains = await get_domains()
    return domains

@router.get("/subdomains/{domain}")
async def get_subdomains_by_domain(domain: str) -> list:
    """
    Endpoint for getting subdomains list for a domain by name.
    """
    response = await list_subdomains_by_domain(domain)
    return response

async def add_domain(domain: str):
    """
    Add a domain to the database.

    Args:
        domain (str): The domain name
    """
    subdomains = collection.find_one({"domain": domain})
    if subdomains is None:
        BackgroundTasks(mns.add(domain=domain))
        return response_with_success(message=domain, code=status.HTTP_201_CREATED)
    return response_with_error(message="Domain already exists", code=status.HTTP_409_CONFLICT)

@router.post("/domain")
async def add_new_domain(domain: str):
    """
    Endpoint for adding a new domain to the database.
    """
    response = await add_domain(domain=domain)
    return response

async def delete_domain(domain: str):
    """
    Delete a domain from the database.

    Args:
        domain (str): Domain name

    Returns:
        dict: Response content
    """
    subdomains = collection.find_one({"domain": domain})
    if subdomains:
        collection.delete_one({"domain": domain})
        return response_with_success(message="domain deleted successfully", code=status.HTTP_204_NO_CONTENT)
    return response_with_error(message="not found", code=status.HTTP_404_NOT_FOUND)

@router.delete("/domain/{domain}")
async def delete(domain: str):
    """
    Endpoint to delete a domain from the database.
    """
    response = await delete_domain(domain=domain)
    return response

async def launch_monitoring():
    """
    Launch the Monitoring Process

    Returns:
        dict: Response content
    """
    BackgroundTasks(mns.monitor())
    return response_with_success(message="start Monitoring", code=status.HTTP_201_CREATED)

@router.get("/monitor")
async def monitor():
    """
    Endpoint for launching the Monitoring processes.
    """
    response = await launch_monitoring()
    return response

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1337)
