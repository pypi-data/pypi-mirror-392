# src/core/command_generator.py
# Use package-root imports (when `src` is on PYTHONPATH) — avoid importing `src.` prefix which breaks
# when running files under `src/` directly.
from loguru import logger
from aws_cli_assistant.core.aws_parsers.s3_parser import parse_s3_intent
from aws_cli_assistant.core.aws_parsers.ec2_parser import parse_ec2_intent
from aws_cli_assistant.core.aws_parsers.lambda_parser import parse_lambda_intent
from aws_cli_assistant.core.aws_parsers.dynamodb_parser import parse_dynamodb_intent
from aws_cli_assistant.core.aws_parsers.iam_parser import parse_iam_intent

def list_supported_services():
    return ["s3", "ec2", "dynamodb", "iam", "lambda"]

def generate_command(intent: str, entities: dict):
    """Generate AWS CLI commands based on intent and entities.
    
    Args:
        intent: The classified intent string
        entities: Dict of extracted entities
        
    Returns:
        tuple: (command_str, description_str)
    """
    if "s3" in intent:
        return parse_s3_intent(intent, entities), f"S3 operation: {intent}"
    if "ec2" in intent:
        return parse_ec2_intent(intent, entities), f"EC2 operation: {intent}"
    if "lambda" in intent:
        return parse_lambda_intent(intent, entities), f"Lambda operation: {intent}"
    if "dynamodb" in intent:
        return parse_dynamodb_intent(intent, entities), f"DynamoDB operation: {intent}"
    if "iam" in intent:
        return parse_iam_intent(intent, entities), f"IAM operation: {intent}"

    logger.warning("Unsupported intent: %s", intent)
    return "echo 'Unknown service intent'", "Service not supported or intent unclear"
