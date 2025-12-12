"""
Optional REST API implementation using FastAPI.
This allows the agent to be exposed as a web service.
"""

from typing import Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Depends, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import jwt
import structlog

from ..agent import BigQueryAgent
from ..config import settings
from ..security import audit_logger

# Initialize logger
logger = structlog.get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="BigQuery LangChain Agent API",
    description="HIPAA-compliant AI agent for querying BigQuery",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,  # Disable docs in production
    redoc_url="/redoc" if not settings.is_production else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not settings.is_production else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()


# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for agent queries."""
    query: str = Field(..., description="Natural language query", min_length=1, max_length=1000)
    user_role: Optional[str] = Field(default="readonly", description="User role for access control")


class QueryResponse(BaseModel):
    """Response model for agent queries."""
    result: str = Field(..., description="Query result")
    execution_time_ms: float = Field(..., description="Execution time in milliseconds")
    timestamp: str = Field(..., description="Response timestamp")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment")
    hipaa_compliant: bool = Field(..., description="HIPAA compliance status")


class TokenRequest(BaseModel):
    """Request model for authentication token."""
    user_id: str = Field(..., description="User identifier")
    user_role: str = Field(..., description="User role")


class TokenResponse(BaseModel):
    """Response model for authentication token."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


# Authentication
def create_access_token(user_id: str, user_role: str) -> str:
    """Create JWT access token."""
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode = {
        "sub": user_id,
        "role": user_role,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        user_id = payload.get("sub")
        user_role = payload.get("role")
        
        if user_id is None or user_role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {"user_id": user_id, "user_role": user_role}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Endpoints
@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "message": "BigQuery LangChain Agent API",
        "version": "1.0.0",
        "documentation": "/docs" if not settings.is_production else "Contact administrator"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment=settings.environment,
        hipaa_compliant=settings.is_hipaa_compliant_config
    )


@app.post("/auth/token", response_model=TokenResponse)
async def get_token(request: TokenRequest):
    """
    Get authentication token.
    
    In production, this should verify user credentials against your auth system.
    This is a simplified implementation for demonstration.
    """
    # In production, verify credentials here
    # For now, we just create a token
    
    if request.user_role not in ["admin", "healthcare_provider", "analyst", "readonly"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user role"
        )
    
    access_token = create_access_token(request.user_id, request.user_role)
    
    audit_logger.log_access(
        user_id=request.user_id,
        action="TOKEN_CREATED",
        resource="auth",
        result="SUCCESS"
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@app.post("/query", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    auth: dict = Depends(verify_token)
):
    """
    Execute a natural language query against BigQuery.
    
    Requires valid JWT token.
    """
    start_time = datetime.utcnow()
    
    try:
        # Initialize agent for this user
        agent = BigQueryAgent(
            user_id=auth["user_id"],
            user_role=auth["user_role"]
        )
        
        # Execute query
        result = agent.query(request.query)
        
        # Calculate execution time
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Log successful query
        audit_logger.log_access(
            user_id=auth["user_id"],
            action="API_QUERY",
            resource="bigquery",
            result="SUCCESS",
            metadata={
                "query_length": len(request.query),
                "execution_time_ms": execution_time
            }
        )
        
        return QueryResponse(
            result=result,
            execution_time_ms=execution_time,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error("query_execution_error", error=str(e), user_id=auth["user_id"])
        
        audit_logger.log_access(
            user_id=auth["user_id"],
            action="API_QUERY",
            resource="bigquery",
            result="ERROR",
            metadata={"error": str(e)}
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(e)}"
        )


@app.get("/schema")
async def get_schema(
    table_name: Optional[str] = None,
    auth: dict = Depends(verify_token)
):
    """
    Get database schema information.
    
    Requires valid JWT token.
    """
    try:
        agent = BigQueryAgent(
            user_id=auth["user_id"],
            user_role=auth["user_role"]
        )
        
        # Use the schema tool
        schema_tool = agent._create_schema_tool()
        result = schema_tool.func(table_name or "")
        
        return {"schema": result}
        
    except Exception as e:
        logger.error("schema_retrieval_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Schema retrieval failed: {str(e)}"
        )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.warning("http_exception", status_code=exc.status_code, detail=exc.detail)
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error("unhandled_exception", error=str(exc))
    return {
        "error": "Internal server error",
        "status_code": 500
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=not settings.is_production,
        log_level=settings.log_level.lower()
    )
