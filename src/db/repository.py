import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from src.core.config import settings
from src.core.exceptions import DatabaseException, DomainNotFoundException

logger = logging.getLogger(__name__)


class MongoRepository:
    """Async MongoDB repository for domain operations"""

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.collection: Optional[AsyncIOMotorCollection] = None

    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(
                settings.mongodb_url, serverSelectionTimeoutMS=5000
            )

            self.collection = self.client[settings.DB_NAME][settings.COLLECTION_NAME]

            # Create index on domain field
            await self.collection.create_index("domain", unique=True)

            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise DatabaseException(f"Database connection failed: {e}")

    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all domains with pagination"""
        try:
            cursor = self.collection.find().skip(skip).limit(limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Error finding all domains: {e}")
            raise DatabaseException(f"Failed to retrieve domains: {e}")

    async def find_one(self, domain: str) -> Optional[Dict[str, Any]]:
        """Find domain by name"""
        try:
            return await self.collection.find_one({"domain": domain})
        except Exception as e:
            logger.error(f"Error finding domain {domain}: {e}")
            raise DatabaseException(f"Failed to find domain: {e}")

    async def exists(self, domain: str) -> bool:
        """Check if domain exists"""
        try:
            count = await self.collection.count_documents({"domain": domain}, limit=1)
            return count > 0
        except Exception as e:
            logger.error(f"Error checking domain existence: {e}")
            return False

    async def count(self) -> int:
        """Count total domains"""
        try:
            return await self.collection.count_documents({})
        except Exception as e:
            logger.error(f"Error counting domains: {e}")
            return 0

    async def add_domain(self, domain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add new domain"""
        try:
            domain_data["created_at"] = datetime.utcnow()
            domain_data["updated_at"] = datetime.utcnow()
            result = await self.collection.insert_one(domain_data)
            domain_data["_id"] = result.inserted_id
            return domain_data
        except Exception as e:
            logger.error(f"Error adding domain: {e}")
            raise DatabaseException(f"Failed to add domain: {e}")

    async def update_subdomains(self, domain: str, new_subdomains: List[str]) -> bool:
        """Add new subdomains to existing domain"""
        try:
            result = await self.collection.update_one(
                {"domain": domain},
                {
                    "$addToSet": {"subdomains": {"$each": new_subdomains}},
                    "$set": {"updated_at": datetime.utcnow()},
                },
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating subdomains for {domain}: {e}")
            raise DatabaseException(f"Failed to update subdomains: {e}")

    async def delete_domain(self, domain: str) -> bool:
        """Delete domain"""
        try:
            result = await self.collection.delete_one({"domain": domain})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting domain {domain}: {e}")
            raise DatabaseException(f"Failed to delete domain: {e}")

    async def get_all_domains_list(self) -> List[str]:
        """Get list of all domain names"""
        try:
            cursor = self.collection.find({}, {"domain": 1, "_id": 0})
            docs = await cursor.to_list(length=None)
            return [doc["domain"] for doc in docs]
        except Exception as e:
            logger.error(f"Error getting domain list: {e}")
            raise DatabaseException(f"Failed to get domain list: {e}")

    async def get_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_domains": {"$sum": 1},
                        "total_subdomains": {"$sum": {"$size": "$subdomains"}},
                        "last_updated": {"$max": "$updated_at"},
                    }
                }
            ]
            result = await self.collection.aggregate(pipeline).to_list(length=1)
            if result:
                return result[0]
            return {"total_domains": 0, "total_subdomains": 0, "last_updated": None}
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"total_domains": 0, "total_subdomains": 0, "last_updated": None}


# Global repository instance
repository = MongoRepository()
