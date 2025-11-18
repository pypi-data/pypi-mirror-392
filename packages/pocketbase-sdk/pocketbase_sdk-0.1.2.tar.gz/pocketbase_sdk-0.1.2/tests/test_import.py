import sys
sys.path.insert(0, '../src')
from pocketbase import Client
print("Import successful")
client = Client("http://127.0.0.1:8090")
print("Client created")
print("Collections service:", type(client.collections))
print("Circular dependency resolved!")
