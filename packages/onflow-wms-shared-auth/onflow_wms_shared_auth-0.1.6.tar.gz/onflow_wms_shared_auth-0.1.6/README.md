# 🧩 Onflow WMS Shared Auth

**Onflow WMS Shared Auth** is a shared **JWT** authentication library for the **Django** and **FastAPI** services in the **Onflow** ecosystem. It ensures a consistent user authentication mechanism across microservices.

---

## 🚀 Installation

```bash
pip install onflow-wms-shared-auth
```

---

## ⚙️ Django Configuration

Add `OnflowJWTAuthentication` to `REST_FRAMEWORK` in `settings.py`:

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "shared_auth.backends_django.OnflowJWTAuthentication",
    ),
}
```

**Example usage:**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "email": request.user.email,
            "warehouse": getattr(request.user, "warehouse_id", None),
        })
```

---

## ⚡ FastAPI Configuration

Import the `get_current_user` dependency to validate and decode JWTs in requests:

```python
from fastapi import FastAPI, Depends
from shared_auth.dependencies_fastapi import get_current_user

app = FastAPI()

@app.get("/me")
async def me(user=Depends(get_current_user)):
    return user
```

**How it works:**
- Automatically reads the `Authorization: Bearer <token>` header.
- Decodes the JWT via `decode_access_token` provided by the library.
- Returns `401 Unauthorized` if the token is invalid.

---

## 🧠 Token Requirement

Any API using this middleware or dependency must receive the header:

```
Authorization: Bearer <JWT_TOKEN>
```

---

## 🧩 Module Structure

```
shared_auth/
│
├── jwt_handler.py              # Encode/decode JWT
├── backends_django.py          # Django authentication backend
├── dependencies_fastapi.py     # FastAPI dependency
└── exceptions.py               # Authentication error definitions
```

---

## 🛠️ Versions

| Version | Description |
|---------|-------------|
| **0.1.4** | Added FastAPI support and standardized error messages |
| **0.1.1** | Initial release with Django support |

---

## 👨‍💻 Authors & Contributions

**Onflow Dev Team**
Contact: [dev@onflow.vn](mailto:dev@onflow.vn)

---

## 📄 License

Released under the **MIT License** – free to use and modify for commercial or personal projects.
