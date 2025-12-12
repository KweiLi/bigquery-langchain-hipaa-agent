"""
Tests for BigQuery LangChain Agent.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.agent.bigquery_agent import BigQueryAgent


class TestBigQueryAgent:
    """Tests for BigQueryAgent."""
    
    @pytest.fixture
    def agent(self, test_env, mock_bigquery_client, mock_openai, mock_credentials):
        """Create a test agent instance."""
        with patch('src.agent.bigquery_agent.ChatOpenAI'), \
             patch('src.agent.bigquery_agent.service_account.Credentials'):
            agent = BigQueryAgent(
                user_id="test_user",
                user_role="admin"
            )
            agent.bq_client = mock_bigquery_client
            return agent
    
    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.user_id == "test_user"
        assert agent.user_role == "admin"
        assert agent.bq_client is not None
        assert agent.llm is not None
    
    def test_validate_query_select_allowed(self, agent):
        """Test that SELECT queries are allowed."""
        query = "SELECT * FROM patients LIMIT 10"
        assert agent._validate_query(query) is True
    
    def test_validate_query_delete_blocked(self, agent):
        """Test that DELETE queries are blocked."""
        query = "DELETE FROM patients WHERE id = 1"
        assert agent._validate_query(query) is False
    
    def test_validate_query_update_blocked(self, agent):
        """Test that UPDATE queries are blocked."""
        query = "UPDATE patients SET name = 'Test' WHERE id = 1"
        assert agent._validate_query(query) is False
    
    def test_validate_query_drop_blocked(self, agent):
        """Test that DROP queries are blocked."""
        query = "DROP TABLE patients"
        assert agent._validate_query(query) is False
    
    def test_validate_query_insert_blocked(self, agent):
        """Test that INSERT queries are blocked."""
        query = "INSERT INTO patients (name) VALUES ('Test')"
        assert agent._validate_query(query) is False
    
    def test_detect_phi_fields_present(self, agent):
        """Test PHI field detection when present."""
        rows = [
            {"id": 1, "name": "John Doe", "ssn": "123-45-6789"},
            {"id": 2, "name": "Jane Smith", "ssn": "987-65-4321"}
        ]
        
        phi_fields = agent._detect_phi_fields(rows)
        assert "name" in phi_fields
        assert "ssn" in phi_fields
    
    def test_detect_phi_fields_absent(self, agent):
        """Test PHI field detection when absent."""
        rows = [
            {"id": 1, "count": 10, "avg_age": 45},
            {"id": 2, "count": 20, "avg_age": 50}
        ]
        
        phi_fields = agent._detect_phi_fields(rows)
        assert len(phi_fields) == 0
    
    def test_detect_phi_fields_empty_results(self, agent):
        """Test PHI field detection with empty results."""
        rows = []
        phi_fields = agent._detect_phi_fields(rows)
        assert len(phi_fields) == 0
    
    @patch('src.agent.bigquery_agent.audit_logger')
    def test_query_execution_with_audit(self, mock_audit, agent):
        """Test that queries are properly audited."""
        # Mock the agent executor
        agent.agent_executor = MagicMock()
        agent.agent_executor.invoke.return_value = {"output": "Test result"}
        
        result = agent.query("Show me all patients")
        
        # Verify audit logging was called
        assert mock_audit.log_access.called
        assert result == "Test result"
    
    @patch('src.agent.bigquery_agent.audit_logger')
    def test_query_execution_error_handling(self, mock_audit, agent):
        """Test error handling during query execution."""
        # Mock the agent executor to raise an exception
        agent.agent_executor = MagicMock()
        agent.agent_executor.invoke.side_effect = Exception("Test error")
        
        result = agent.query("Show me all patients")
        
        # Should return error message
        assert "failed" in result.lower()
        
        # Verify error was logged
        assert mock_audit.log_access.called
