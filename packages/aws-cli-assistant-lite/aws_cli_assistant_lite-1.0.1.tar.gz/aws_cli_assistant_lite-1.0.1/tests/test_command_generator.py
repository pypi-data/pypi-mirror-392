"""Parametrized pytest suite for all AWS service parsers.

This converts the old script-style runner into a proper pytest test so
`pytest` can discover and run the checks reliably.
"""
from pathlib import Path
import sys
import pytest

# Ensure local package is importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aws_cli_assistant.core.aws_parsers.s3_parser import parse_s3_intent
from aws_cli_assistant.core.aws_parsers.ec2_parser import parse_ec2_intent
from aws_cli_assistant.core.aws_parsers.lambda_parser import parse_lambda_intent
from aws_cli_assistant.core.aws_parsers.dynamodb_parser import parse_dynamodb_intent
from aws_cli_assistant.core.aws_parsers.iam_parser import parse_iam_intent
from aws_cli_assistant.core.aws_validator import validate_command_safe


TEST_CASES = [
    # S3
    ("s3", "create_s3_bucket", {"bucket": "phase3-test-bucket", "region": "us-west-1"}),
    ("s3", "list_s3_buckets", {}),

    # EC2
    ("ec2", "list_ec2_instances", {"region": "us-west-1"}),
    ("ec2", "start_ec2_instance", {"instance_id": "i-1234567890abcdef0", "region": "us-west-1"}),

    # Lambda
    ("lambda", "list_lambda_functions", {"region": "us-west-1"}),
    ("lambda", "invoke_lambda", {"function_name": "test-function", "region": "us-west-1"}),

    # DynamoDB
    ("dynamodb", "list_dynamodb_tables", {}),
    ("dynamodb", "create_dynamodb_table", {"table": "test-table", "region": "us-west-1"}),

    # IAM
    ("iam", "list_iam_users", {}),
    ("iam", "create_iam_user", {"user_name": "test-user"}),
]


@pytest.mark.parametrize("service,intent,entities", TEST_CASES)
def test_service_command(service, intent, entities):
    """Ensure each service parser produces a command-like result and validation returns a dict.

    This test is intentionally light-weight: it checks that a parser returns a result
    (string/dict/list) and that `validate_command_safe` returns a dict containing at
    least a 'status' key. Heavier integration tests (actual AWS calls) belong in
    a separate integration suite.
    """
    parser_funcs = {
        "s3": parse_s3_intent,
        "ec2": parse_ec2_intent,
        "lambda": parse_lambda_intent,
        "dynamodb": parse_dynamodb_intent,
        "iam": parse_iam_intent,
    }

    parser = parser_funcs.get(service)
    assert parser is not None, f"No parser available for service: {service}"

    command = parser(intent, entities)
    assert command is not None, "Parser returned None"
    assert isinstance(command, (str, dict, list)), f"Unexpected command type: {type(command)}"

    validation = validate_command_safe(intent, entities)
    assert isinstance(validation, dict), "Validation should return a dict"
    assert "status" in validation, "Validation result missing 'status'"
