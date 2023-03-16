from fastapi import FastAPI, HTTPException, BackgroundTasks
from pymongo import MongoClient
from src.config import DB_HOST, DB_NAME, COLLECTION_NAME, DB_PORT
from src.db import db
from src.mns import SubDomainMonitoring

app = FastAPI()
mns = SubDomainMonitoring()


# TODO Try to use the /app/logs/api.log to save logs



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


def response_with_success(message, code=200):
	"""
	response with success
	
	Args:
	    code:int -> status code, default is 200
		message:str -> custom message

	Returns: dict()

	"""
	return {
		"success": True,
		"code": code,
		"message": message
	}


def response_with_error(message, code):
	"""
	response with error
	
	Args:
		code:int -> status code
		message:str -> custom message

	Returns: dict()
	"""
	return {
		"success": False,
		"code": code,
		"message": message
	}


async def get_subdomains_by_domain(domain):
	"""
	Get all domains from the database.

	:return: A list of domain documents.
	"""
	subdomains = collection.find_one({"domain": domain})
	print(subdomains)
	if subdomains:
		if len(subdomains) == 0:
			return response_with_error(message="domain not found", code=404)
	return response_with_success(message=helper(subdomains), code=200)


@app.get("/ping")
async def index():
	"""
	Root endpoint for testing the API.
	"""
	print()
	for route in app.routes:
		print(route.path)
	return response_with_success(message="pong", code=200)


async def get_domains():
	"""
	Get all domains from the database.

	Returns A list of domain documents.
	"""

	domains = [ target.get('domain') for target in collection.find() ]
	return response_with_success(message=domains)


@app.get("/domains")
async def list_domains():
	"""
		Endpoint for listing all domains in the database.
	"""
	domains = await get_domains()
	return domains


@app.get("/domain/{domain}")
async def get_domain_by_name(domain: str):
	"""
		Endpoint for getting subdomains list a domain by name.
	"""
	response = await get_subdomains_by_domain(domain)
	return response
	#if not response:
		#raise HTTPException(status_code=404, detail="Domain not found")



async def add_domain(domain: str):
	"""
	Add a domain to the database.

	:param domain: The domain to add.
	"""
	
	subdomains = await get_subdomains_by_domain(domain)
	print(subdomains)
	print(subdomains.get('subdomains'))
	if subdomains.get('subdomains') is None:
		BackgroundTasks(mns.add(domain=domain))
		return response_with_success(message=domain, code=201)
	return response_with_error(message="Domain already exists", code=409)


@app.post("/domain")
async def add_new_domain(domain: str):
	"""
		Endpoint for adding a new domain to the database.
	"""
	response = await add_domain(domain=domain)
	return response


async def delete_domain(domain):
	"""
	This function used to delete domain from the database
	Args:
		domain:str -> domain name

	Returns: success if the domain exist else nor found

	"""
	result = collection.find_one_and_delete({"domain": domain})
	if result:
		return response_with_success(message="domain deleted successfully", code=204)
	return response_with_error(message="Domain not found", code=404)


@app.delete("/domain/{domain}")
async def delete(domain: str):
	"""
		Endpoint to delete domain from the database
	"""
	response = await delete_domain(domain=domain)
	return response


async def launch_monitoring():
	"""
	This function used to launch The Monitoring Process
	Returns: Str -> Start Monitoring

	"""
	BackgroundTasks(mns.monitor())
	return response_with_success(message="start Monitoring")


@app.get("/monitor")
async def monitor():
	"""
		Endpoint for launching the Monitoring processes.
	"""
	response = await launch_monitoring()
	return response
