"""Exercise the real vector wrapper in two fresh containers sharing one disk."""
import sys
from pathlib import Path

import django


def main():
    django.setup()
    from django.conf import settings

    from restaurantBE.chatbot.rag.vector_db import VectorDBService

    assert not settings.DEBUG, "The image must default to production settings"
    assert not Path("/app/.env").exists(), "Local secrets leaked into the image"
    assert not list(Path("/app").glob("sinuous-maker-*.json")), "Google credentials leaked into the image"
    db = VectorDBService(collection_name="deployment_persistence_test")
    if sys.argv[1] == "write":
        db.upsert_documents([{
            "id": "persistent-document",
            "content": "Chroma survives replacement of the application container",
            "embedding": [1.0, 0.0, 0.0],
            "metadata": {"source": "deployment-test"},
        }])
    else:
        assert db.count() == 1, "Persisted data disappeared after container replacement"
        results = db.query(query_embedding=[1.0, 0.0, 0.0], top_k=1)
        assert results[0]["id"] == "persistent-document"
        assert results[0]["metadata"]["source"] == "deployment-test"
    print("Persistence check passed:", sys.argv[1])


if __name__ == "__main__":
    main()
