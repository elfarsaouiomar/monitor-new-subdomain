from fastapi import FastAPI, HTTPException, Request
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient
from src.config import DB_HOST, DB_NAME, COLLECTION_NAME, DB_PORT
from src.mns import SubDomainMonitoring

app = FastAPI()
mns = SubDomainMonitoring()

# Initialize the MongoDB client
client = MongoClient(f"mongodb://{DB_HOST}:{DB_PORT}")
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


def helper(data):
	if data:
		data['id'] = str(data['_id'])
		del [data['_id']]
	return data


async def get_subdomains_by_domain(domain):
	"""
	Get all domains from the database.

	:return: A list of domain documents.
	"""
	subdomains = collection.find_one({"domain": domain})
	return helper(subdomains)


@app.get("/")
async def index():
	"""
	Root endpoint for testing the API.
	"""
	
	return {"status": "ok"}


async def get_domains():
	"""
	Get all domains from the database.

	:return: A list of domain documents.
	"""
	domains = []
	for doc in collection.find():
		domains.append(doc.get('domain'))
	return domains


@app.get("/domains")
async def list_domains():
	"""
		Endpoint for listing all domains in the database.
	"""
	domains = await get_domains()
	return {"domains": domains}


@app.get("/domain/{domain}")
async def get_domain_by_name(domain: str):
	"""
		Endpoint for getting a domain by name.
	"""
	doc = await get_subdomains_by_domain(domain)
	if not doc:
		raise HTTPException(status_code=404, detail="Domain not found")
	return doc


async def add_domain(domain: str):
	"""
	Add a domain to the database.

	:param domain: The domain to add.
	:raises HTTPException: If the domain already exists in the database.
	"""
	
	subdomains = await get_subdomains_by_domain(domain)
	if subdomains is None:
		mns.add(domain=domain)
		return domain
	return "Domain already exists"


@app.post("/domain")
async def add_new_domain(domain: str):
	"""
		Endpoint for adding a new domain to the database.
	"""
	
	response = await add_domain(domain=domain)
	return response


async def delete_domain(domain):
	result = collection.find_one_and_delete({"domain": domain})
	if result:
		response = {"message": "Document deleted successfully"}
	else:
		response = {"message": "Document not found"}
	return response


@app.delete("/domain/{domain}")
async def delete(domain: str):
	response = await delete_domain(domain=domain)
	return response

"""
TODO: later
async def launch_monitoring():
	mns.monitor()
	return "Start Monitoring"


@app.get("/monitor")
async def monitor():
	"
		Endpoint for launching the Monitoring processes.
	"
	response = await launch_monitoring()
	return response

"""