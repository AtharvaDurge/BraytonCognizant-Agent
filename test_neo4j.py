from neo4j import GraphDatabase, TrustAll
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

# Change URI scheme to neo4j so we can pass SSL settings
driver = GraphDatabase.driver(
    uri.replace("neo4j+s://", "neo4j://"),
    auth=(username, password),
    encrypted=True,
    trusted_certificates=TrustAll()
)
driver.verify_connectivity()
print("✅ Connected!")