from fastapi import FastAPI, BackgroundTasks, APIRouter, status
from pymongo import MongoClient
from .config import DB_HOST, DB_NAME, COLLECTION_NAME, DB_PORT
from .mns import SubDomainMonitoring
from fastapi.responses import JSONResponse

mns = SubDomainMonitoring()
router = APIRouter(
    prefix="/v1",
)

# Initialize the FlstAPI() App
def create_app():
    app = FastAPI()
    app.include_router(router, prefix="/api")
    return app


# Initialize the MongoDB client
client = MongoClient(f"mongodb://{DB_HOST}:{DB_PORT}")
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


def helper(data):
	"""
		Delete the _id from Mongo Collection
	"""
	if data:
		data['id'] = str(data['_id'])
		del [data['_id']]
	return data


def response_with_success(message, code=status.HTTP_200_OK):
	"""
	response with success
	
	Args:
	    code:int -> status code, default is 200
		message:str -> custom message

	Returns: dict()

	"""
	return JSONResponse(status_code=code,
		     			content={
							"success": True,
							"code": code,
							"message": message
						})


def response_with_error(message, code):
	"""
	response with error
	
	Args:
		code:int -> status code
		message:str -> custom message

	Returns: dict()
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

	:return: A list of domain documents.
	"""
	subdomains = collection.find_one({"domain": domain})

	if subdomains is not None:
			return response_with_success(message=helper(subdomains), code=status.HTTP_200_OK)
	return response_with_error(message="not found", code=status.HTTP_404_NOT_FOUND)


@router.get("/ping")
async def index():
	"""
	Root endpoint for testing the API.
	"""
	return response_with_success(message="pong", code=status.HTTP_200_OK)


async def get_domains():
	"""
	Get all domains from the database.

	Returns A list of domain documents.
	"""
	domains = [ target.get('domain') for target in collection.find() ]
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
		Endpoint for getting subdomains list a domain by name.
	"""
	response = await list_subdomains_by_domain(domain)
	return response



async def add_domain(domain: str):
	"""
	Add a domain to the database.

	:param domain: The domain name
	"""
	
	# subdomains = await list_subdomains_by_domain(domain)
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
	This function used to delete domain from the database
	Args:
		domain:str -> domain name

	Returns: success if the domain exist else nor found

	"""
	subdomains = collection.find_one_and_delete({"domain": domain})
	if subdomains:
		BackgroundTasks(mns.delete_domain(domain=domain))
		return response_with_success(message="domain deleted successfully", code=status.HTTP_204_NO_CONTENT)
	return response_with_error(message="not found", code=status.HTTP_404_NOT_FOUND)


@router.delete("/domain/{domain}")
async def delete(domain: str):
	"""
		Endpoint to delete domain from the database
	"""
	response = await delete_domain(domain=domain)
	return response


async def launch_monitoring():
	"""
	This function used to launch The Monitoring Process
	Returns: string -> Start Monitoring

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