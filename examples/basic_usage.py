"""
Example usage of the BigQuery LangChain Agent.
This script demonstrates basic agent functionality.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agent import BigQueryAgent
from src.config import settings
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger(__name__)


def main():
    """Main function demonstrating agent usage."""
    # Load environment variables
    load_dotenv()
    
    print("=" * 60)
    print("BigQuery LangChain Agent - HIPAA Compliant")
    print("=" * 60)
    print(f"Environment: {settings.environment}")
    print(f"Project: {settings.gcp_project_id}")
    print(f"Dataset: {settings.gcp_dataset_id}")
    print(f"HIPAA Compliant Config: {settings.is_hipaa_compliant_config}")
    print("=" * 60)
    print()
    
    try:
        # Initialize agent
        print("Initializing agent...")
        agent = BigQueryAgent(
            user_id="demo_user",
            user_role="admin"
        )
        print("✓ Agent initialized successfully!\n")
        
        # Example queries
        example_queries = [
            "What tables are available in the database?",
            "Show me the schema for the first table",
            # Add your custom queries here
        ]
        
        # Interactive mode
        print("Agent is ready! You can now ask questions.")
        print("Type 'quit' or 'exit' to stop.\n")
        
        # Run example queries first
        print("Running example queries...\n")
        for i, query in enumerate(example_queries, 1):
            print(f"Example {i}: {query}")
            print("-" * 60)
            response = agent.query(query)
            print(f"Response:\n{response}\n")
            print("=" * 60)
            print()
        
        # Interactive loop
        while True:
            try:
                user_input = input("Your question: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break
                
                print("\nProcessing...\n")
                response = agent.query(user_input)
                print(f"Response:\n{response}\n")
                print("=" * 60)
                print()
                
            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Goodbye!")
                break
            except Exception as e:
                logger.error("query_error", error=str(e))
                print(f"\nError: {str(e)}\n")
        
    except Exception as e:
        logger.error("initialization_error", error=str(e))
        print(f"\n❌ Error: {str(e)}")
        print("\nPlease check:")
        print("1. Your .env file is configured correctly")
        print("2. GCP credentials are valid and have BigQuery access")
        print("3. BigQuery dataset exists and is accessible")
        print("4. All required environment variables are set")
        sys.exit(1)


if __name__ == "__main__":
    main()
