"""
BigQuery LangChain Agent implementation.
Provides natural language interface to BigQuery with HIPAA compliance.
"""

import hashlib
import time
from typing import Any, Dict, List, Optional
from datetime import datetime

from google.cloud import bigquery
from google.oauth2 import service_account
from langchain_core.tools import Tool
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import structlog

from ..config import settings
from ..security import audit_logger, access_control

logger = structlog.get_logger(__name__)


class BigQueryAgent:
    """
    LangChain agent for querying BigQuery with HIPAA compliance.
    
    This agent provides a natural language interface to BigQuery while
    maintaining audit trails and security controls required for HIPAA compliance.
    """
    
    def __init__(
        self,
        user_id: str = "system",
        user_role: str = "admin",
        credentials_path: Optional[str] = None
    ):
        """
        Initialize the BigQuery agent.
        
        Args:
            user_id: Identifier for the user making requests
            user_role: Role of the user (admin, healthcare_provider, analyst, readonly)
            credentials_path: Path to GCP service account credentials
        """
        self.user_id = user_id
        self.user_role = user_role
        
        # Initialize BigQuery client
        credentials_path = credentials_path or settings.google_application_credentials
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        
        self.bq_client = bigquery.Client(
            credentials=credentials,
            project=settings.gcp_project_id,
            location=settings.gcp_location
        )
        
        # Initialize LLM - Vertex AI (Canadian compliance)
        self.llm = ChatVertexAI(
            model_name=settings.vertex_ai_model,
            temperature=settings.llm_temperature,
            max_output_tokens=settings.max_tokens,
            location=settings.vertex_ai_location,
            project=settings.gcp_project_id,
            credentials=credentials
        )
        
        logger.info(
            "agent_initialized",
            user_id=user_id,
            user_role=user_role,
            project=settings.gcp_project_id
        )
    
    def _execute_query(self, query: str) -> str:
        """Execute a SQL query against BigQuery."""
        try:
            if not self._validate_query(query):
                return "Query validation failed. Query may contain unauthorized operations."
            
            start_time = time.time()
            query_job = self.bq_client.query(
                query,
                timeout=settings.bigquery_timeout_seconds
            )
            results = query_job.result(max_results=settings.bigquery_max_results)
            execution_time = (time.time() - start_time) * 1000
            
            rows = [dict(row) for row in results]
            
            query_hash = hashlib.sha256(query.encode()).hexdigest()
            phi_fields = self._detect_phi_fields(rows)
            
            audit_logger.log_query(
                user_id=self.user_id,
                query=access_control.sanitize_query(query),
                query_hash=query_hash,
                result_count=len(rows),
                execution_time_ms=execution_time,
                phi_fields_accessed=phi_fields
            )
            
            if not rows:
                return "Query executed successfully. No results found."
            
            display_rows = rows[:10]
            result_text = f"Found {len(rows)} results. Showing first {len(display_rows)}:\n\n"
            
            for i, row in enumerate(display_rows, 1):
                result_text += f"Row {i}:\n"
                for key, value in row.items():
                    result_text += f"  {key}: {value}\n"
                result_text += "\n"
            
            return result_text
            
        except Exception as e:
            error_msg = f"Query execution failed: {str(e)}"
            logger.error("query_execution_error", error=str(e), user_id=self.user_id)
            
            audit_logger.log_access(
                user_id=self.user_id,
                action="QUERY_EXECUTE",
                resource="bigquery",
                result="ERROR",
                metadata={"error": str(e)}
            )
            
            return error_msg
    
    def _get_schema(self, table_name: str = "") -> str:
        """Get schema information for tables."""
        try:
            dataset_ref = self.bq_client.dataset(settings.gcp_dataset_id)
            
            if table_name:
                table_ref = dataset_ref.table(table_name)
                table = self.bq_client.get_table(table_ref)
                
                schema_text = f"Schema for table '{table_name}':\n\n"
                for field in table.schema:
                    schema_text += f"  {field.name}: {field.field_type}"
                    if field.mode != "NULLABLE":
                        schema_text += f" ({field.mode})"
                    if field.description:
                        schema_text += f" - {field.description}"
                    schema_text += "\n"
                
                return schema_text
            else:
                tables = list(self.bq_client.list_tables(dataset_ref))
                
                if not tables:
                    return f"No tables found in dataset '{settings.gcp_dataset_id}'"
                
                schema_text = f"Tables in dataset '{settings.gcp_dataset_id}':\n\n"
                for table in tables:
                    schema_text += f"  - {table.table_id}\n"
                
                schema_text += "\nAsk me for schema of a specific table to see details."
                return schema_text
                
        except Exception as e:
            error_msg = f"Failed to retrieve schema: {str(e)}"
            logger.error("schema_retrieval_error", error=str(e))
            return error_msg
    
    def _validate_query(self, query: str) -> bool:
        """Validate SQL query for security and compliance."""
        query_upper = query.upper().strip()
        
        destructive_keywords = [
            "DELETE", "DROP", "TRUNCATE", "UPDATE", "INSERT",
            "ALTER", "CREATE", "REPLACE", "MERGE"
        ]
        
        for keyword in destructive_keywords:
            if keyword in query_upper:
                logger.warning(
                    "destructive_query_blocked",
                    user_id=self.user_id,
                    keyword=keyword
                )
                return False
        
        return True
    
    def _detect_phi_fields(self, rows: List[Dict[str, Any]]) -> List[str]:
        """Detect PHI fields in query results."""
        if not rows:
            return []
        
        phi_fields_set = set(settings.phi_fields)
        result_fields = set(rows[0].keys())
        
        return list(phi_fields_set & result_fields)
    
    def query(self, user_input: str) -> str:
        """
        Process a natural language query.
        
        Args:
            user_input: Natural language query from user
            
        Returns:
            Response from the agent
        """
        try:
            audit_logger.log_access(
                user_id=self.user_id,
                action="AGENT_QUERY",
                resource="bigquery_agent",
                result="STARTED",
                metadata={"input": user_input[:100]}
            )
            
            # Step 1: Check if asking for schema/tables
            if "table" in user_input.lower() and any(word in user_input.lower() for word in ["what", "show", "list", "available"]):
                if "schema" in user_input.lower():
                    # Extract table name if specified
                    words = user_input.split()
                    for i, word in enumerate(words):
                        if word.lower() in ["for", "of"] and i + 1 < len(words):
                            table_name = words[i + 1].strip("?.,")
                            response = self._get_schema(table_name)
                            return response
                    response = self._get_schema()
                else:
                    response = self._get_schema()
                
                audit_logger.log_access(
                    user_id=self.user_id,
                    action="AGENT_QUERY",
                    resource="bigquery_agent",
                    result="SUCCESS"
                )
                return response
            
            # Step 2: Use LLM to generate SQL query
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"""You are a SQL query generator for BigQuery. 

Dataset: {settings.gcp_dataset_id}
User role: {self.user_role}

RULES:
1. Generate ONLY SELECT queries (read-only)
2. Never use DELETE, UPDATE, DROP, INSERT, ALTER, CREATE
3. Always use LIMIT clause (default LIMIT 100)
4. Be mindful of PHI fields: {', '.join(settings.phi_fields)}
5. Return ONLY the SQL query, no explanation

Generate a safe SELECT query for the user's request."""),
                ("human", "{input}")
            ])
            
            chain = prompt | self.llm | StrOutputParser()
            sql_query = chain.invoke({"input": user_input}).strip()
            
            # Clean up the SQL (remove markdown code blocks if present)
            if "```" in sql_query:
                sql_query = sql_query.split("```")[1]
                if sql_query.startswith("sql"):
                    sql_query = sql_query[3:]
                sql_query = sql_query.strip()
            
            logger.info("generated_query", query=sql_query, user_id=self.user_id)
            
            # Step 3: Execute the query
            result = self._execute_query(sql_query)
            
            # Step 4: Use LLM to explain results
            explain_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are explaining query results to a user. Be concise and helpful."),
                ("human", f"User asked: {user_input}\n\nSQL Query: {sql_query}\n\nResults: {result}\n\nProvide a natural language summary:")
            ])
            
            explain_chain = explain_prompt | self.llm | StrOutputParser()
            explanation = explain_chain.invoke({})
            
            audit_logger.log_access(
                user_id=self.user_id,
                action="AGENT_QUERY",
                resource="bigquery_agent",
                result="SUCCESS"
            )
            
            return f"{explanation}\n\n---\nSQL Query Used: {sql_query}"
            
        except Exception as e:
            error_msg = f"Agent execution failed: {str(e)}"
            logger.error("agent_execution_error", error=str(e), user_id=self.user_id)
            
            audit_logger.log_access(
                user_id=self.user_id,
                action="AGENT_QUERY",
                resource="bigquery_agent",
                result="ERROR",
                metadata={"error": str(e)}
            )
            
            return error_msg