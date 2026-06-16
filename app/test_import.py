try:
    from domains.personalities.models import Entity
    print("Successfully imported Entity from domains.personalities.models")
except ImportError as e:
    print(f"Failed to import Entity from domains.personalities.models: {e}")

try:
    from domains.personalities.models.entity import Entity
    print("Successfully imported Entity from domains.personalities.models.entity")
except ImportError as e:
    print(f"Failed to import Entity from domains.personalities.models.entity: {e}")

import domains.personalities.models
print(f"Contents of domains.personalities.models: {dir(domains.personalities.models)}")
