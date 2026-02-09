import argparse
import sys
import os
from typing import Optional
import logging

# Add the parent directory to the path to import other modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ingestion.main import DocumentIngestionPipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser"""
    parser = argparse.ArgumentParser(
        description="RAG Chatbot Document Ingestion Pipeline CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s run                    # Run the full ingestion pipeline
  %(prog)s validate               # Validate the pipeline configuration
  %(prog)s run --docs-path /path/to/docs    # Use custom docs path
  %(prog)s run --model all-MiniLM-L6-v2     # Use specific model
        """
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Run command
    run_parser = subparsers.add_parser('run', help='Run the document ingestion pipeline')
    run_parser.add_argument(
        '--docs-path',
        type=str,
        default="Phase-2 Chatbot using Nextjs/docs",
        help='Path to the documents directory (default: Phase-2 Chatbot using Nextjs/docs)'
    )
    run_parser.add_argument(
        '--model',
        type=str,
        default="all-MiniLM-L6-v2",
        help='Embedding model name (default: all-MiniLM-L6-v2)'
    )
    run_parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-processing even if content is already indexed'
    )

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate pipeline configuration')
    validate_parser.add_argument(
        '--docs-path',
        type=str,
        default="Phase-2 Chatbot using Nextjs/docs",
        help='Path to the documents directory (default: Phase-2 Chatbot using Nextjs/docs)'
    )

    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear the Qdrant collection')
    clear_parser.add_argument(
        '--confirm',
        action='store_true',
        help='Confirm that you want to clear the collection (required for safety)'
    )

    return parser

def run_pipeline(args: argparse.Namespace) -> bool:
    """Run the document ingestion pipeline"""
    try:
        logger.info(f"Starting ingestion pipeline with docs path: {args.docs_path}")
        logger.info(f"Using model: {args.model}")

        pipeline = DocumentIngestionPipeline(
            docs_path=args.docs_path,
            model_name=args.model
        )

        # Validate pipeline before running
        validation_results = pipeline.validate_pipeline()
        logger.info(f"Pipeline validation results: {validation_results}")

        if not validation_results['docs_path_exists']:
            logger.error(f"Docs path does not exist: {args.docs_path}")
            return False

        if validation_results['documents_count'] == 0:
            logger.warning(f"No documents found in {args.docs_path}")
            return False

        # Run the ingestion pipeline
        success = pipeline.run_ingestion_pipeline()

        if success:
            logger.info("Ingestion pipeline completed successfully!")
            return True
        else:
            logger.error("Ingestion pipeline failed!")
            return False

    except Exception as e:
        logger.error(f"Error running ingestion pipeline: {str(e)}")
        return False

def validate_pipeline(args: argparse.Namespace) -> bool:
    """Validate the pipeline configuration"""
    try:
        logger.info(f"Validating pipeline with docs path: {args.docs_path}")

        pipeline = DocumentIngestionPipeline(docs_path=args.docs_path)

        validation_results = pipeline.validate_pipeline()
        logger.info("Pipeline validation results:")
        for key, value in validation_results.items():
            logger.info(f"  {key}: {value}")

        # Check if critical validations pass
        critical_checks = [
            ('docs_path_exists', validation_results['docs_path_exists']),
            ('docs_path_readable', validation_results['docs_path_readable']),
            ('embedding_service_loaded', validation_results['embedding_service_loaded']),
            ('qdrant_connection', validation_results['qdrant_connection']),
            ('correct_embedding_dimension', validation_results['correct_embedding_dimension'])
        ]

        all_passed = True
        for check_name, passed in critical_checks:
            if not passed:
                logger.error(f"Critical validation failed: {check_name}")
                all_passed = False

        if all_passed:
            logger.info("All critical validations passed!")
        else:
            logger.error("Some critical validations failed!")

        return all_passed

    except Exception as e:
        logger.error(f"Error validating pipeline: {str(e)}")
        return False

def clear_collection(args: argparse.Namespace) -> bool:
    """Clear the Qdrant collection"""
    if not args.confirm:
        logger.error("Please use --confirm flag to clear the collection (safety measure)")
        return False

    try:
        logger.info("Clearing Qdrant collection...")

        # Import here to avoid circular imports
        from ingestion.qdrant_uploader import QdrantUploader

        uploader = QdrantUploader()
        success = uploader.clear_collection()

        if success:
            logger.info("Qdrant collection cleared successfully!")
        else:
            logger.error("Failed to clear Qdrant collection!")

        return success

    except Exception as e:
        logger.error(f"Error clearing collection: {str(e)}")
        return False

def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()

    # Check if command was provided
    if not args.command:
        parser.print_help()
        return 1

    # Execute the appropriate command
    if args.command == 'run':
        success = run_pipeline(args)
    elif args.command == 'validate':
        success = validate_pipeline(args)
    elif args.command == 'clear':
        success = clear_collection(args)
    else:
        logger.error(f"Unknown command: {args.command}")
        return 1

    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)