# 🧠 MomentoAI — Python SDK

MomentoAI is a lightweight Python SDK that connects to the hosted MomentoAI FastAPI backend and uses **your own Supabase project** to store images and embeddings.
 
## Official PyPi published library: https://pypi.org/project/momentoai/

---

## 📦 Installation

Install MomentoAI via PyPI:

```bash
pip install momentoai
```

---

# ⚙️ Initialize the Client

```python
from MomentoAI import MomentoAIClient

client = MomentoAIClient(
    api_key="public-access",   # default key for open access
    api_url="https://momento-ai-1-42230574747.asia-south1.run.app",

    # — your own Supabase credentials —
    supabase_url="https://yourproject.supabase.co",
    supabase_service_key="YOUR_SUPABASE_SERVICE_KEY",
    supabase_bucket="YOUR_BUCKET_NAME"
)
```

---

# 🩺 Check Backend Status

Use `.health()` to verify the backend is live:

```python
print(client.health())
```

**Expected output:**

```json
{
  "models_loaded": true
}
```

---

# 📸 Core SDK Functions

Below are the main operations supported by the MomentoAI SDK.

---

## 1️⃣ `vectorize_image()`

Uploads an image → extracts embeddings → stores them in your Supabase project.

```python
response = client.vectorize_image(
    "me.jpg",
    event_id="event1",
    business_id="business1"
)

print(response)
```

---

## 2️⃣ `find_face()`

Finds similar faces in your stored Supabase embeddings.

```python
matches = client.find_face(
    "person.jpg",
    event_id="event1",
    business_id="business1"
)

print(matches)
```

---

## 3️⃣ `search_images()`

Text → Image retrieval using CLIP embeddings.

```python
results = client.search_images(
    "a man smiling outdoors",
    event_id="event1",
    business_id="business1"
)

print(results)
```

---

## 4️⃣ `list_embeddings()`

Retrieve all embeddings for a specific event + business.

```python
records = client.list_embeddings(
    event_id="event1",
    business_id="business1"
)

print(records)
```

---

## 5️⃣ `delete_embedding()`

Delete a specific embedding record from Supabase.

```python
client.delete_embedding("some-embedding-id")
```

---

# 🪪 License

MIT License  
© 2025 — Manil Modi
