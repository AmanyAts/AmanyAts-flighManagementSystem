provider "aws" {
  region = "eu-north-1" # Adjust to your AWS region
}

# Data source to retrieve the AWS account ID
data "aws_caller_identity" "current" {}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_execution_role" {
  name = "lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}



# Attach Policy to IAM Role
resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBReadOnlyAccess"
}

# Lambda Function for Search Flights
resource "aws_lambda_function" "searchFlights" {
  function_name = "searchFlights"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "handler.searchFlights"
  runtime       = "python3.9"
  filename      = "${path.module}/handler.zip"

  environment {
    variables = {
      DYNAMODB_TABLE = "Flights" # Ensure this matches your DynamoDB table name
    }
  }

  tags = {
    Environment = "dev"
  }
}

# REST API Gateway
resource "aws_api_gateway_rest_api" "flight_management_api" {
  name = "flightManagementAPIs"
}

# API Gateway Resource for /searchFlights
resource "aws_api_gateway_resource" "searchFlights_resource" {
  rest_api_id = aws_api_gateway_rest_api.flight_management_api.id
  parent_id   = aws_api_gateway_rest_api.flight_management_api.root_resource_id
  path_part   = "searchFlights"
}

# API Gateway Method for GET /searchFlights
resource "aws_api_gateway_method" "get_searchFlights" {
  rest_api_id   = aws_api_gateway_rest_api.flight_management_api.id
  resource_id   = aws_api_gateway_resource.searchFlights_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

# API Gateway Integration with Lambda
resource "aws_api_gateway_integration" "searchFlights_integration" {
  rest_api_id             = aws_api_gateway_rest_api.flight_management_api.id
  resource_id             = aws_api_gateway_resource.searchFlights_resource.id
  http_method             = aws_api_gateway_method.get_searchFlights.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.searchFlights.invoke_arn
}

# Lambda Permission for API Gateway
resource "aws_lambda_permission" "apigw_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.searchFlights.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:eu-north-1:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.flight_management_api.id}/*/*"
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.flight_management_api.id
  stage_name  = "dev"

  depends_on = [
    aws_api_gateway_integration.searchFlights_integration
  ]
}

# Output the API Gateway endpoint
output "api_endpoint" {
  value = "${aws_api_gateway_deployment.api_deployment.invoke_url}searchFlights"
}
