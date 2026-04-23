Secure API Gateway

Overview:
This project implements a Secure API Gateway using FastAPI. The
gateway sits in front of backend services and handles authentication,
authorization, and rate limiting. The goal is to centralize security at
the gateway so backend services do not need to manage their own security
logic.

The gateway helps protect backend APIs from: 
- Unauthorized access
- Credential abuse
- Excessive request flooding

Technologies Used 
- Python
-  FastAPI
- JWT (JSON Web Tokens)
-  Uvicorn

Project Structure

secure-api-gateway │
├── app │ 
├── auth.py │ 
├── authorization.py │ 
├──
backend.py │
├── main.py │ 
├── models.py 
│ └── rate_limiter.py │
└──
requirements.txt

Implemented Features

Authentication Users log in through a login endpoint and receive a JWT
token.

Endpoint: POST /login

File: app/auth.py

Token Verification Protected routes require a valid JWT token. Requests
must include:

Authorization: Bearer

Authorization Basic role-based access control is implemented to restrict
which users can access certain endpoints.

File: app/authorization.py

Backend Service A simple backend endpoint simulates a protected service
behind the gateway.

File: app/backend.py

Rate Limiting Basic request rate limiting prevents users from making too
many requests in a short period of time.

File: app/rate_limiter.py

Running the Project:

>Install dependencies: pip install -r requirements.txt

>Start the server: uvicorn app.main:app -–reload

>Open the API documentation: http://127.0.0.1:8000/docs

Current Status:
The gateway is operational with authentication, token
verification, protected routes, and rate limiting implemented.

Where Development Stopped Users can log in to generate a JWT token and
access protected endpoints through the gateway.

Possible Next Steps - Expand role-based access control
(admin, user, guest) - Connect authentication to a database instead of
hardcoded users - Improve the rate limiting system - Add additional
protected backend endpoints

Basic Test Flow 1. Start the server 2. Navigate to /docs 3. Use the
/login endpoint to generate a token 4. Copy the token and click
Authorize in Swagger 5. Test protected endpoints

Authors:
Summer
Alex
