import sys
import os
print("Current Working Directory:", os.getcwd())
print("Sys Path:", sys.path)
try:
    import domains.email_service
    print("Successfully imported domains.email_service")
except ImportError as e:
    print("Failed to import domains.email_service:", e)
