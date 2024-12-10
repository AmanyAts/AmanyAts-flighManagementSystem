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
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

# Lambda Function for Booking Service
resource "aws_lambda_function" "booking_service" {
  function_name = "bookingService"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "handler.bookFlight"
  runtime       = "python3.9"
  filename      = "${path.module}/handler.zip"

  environment {
    variables = {
      BOOKINGS_TABLE = "Bookings" # DynamoDB table for bookings
      FLIGHTS_TABLE  = "Flights"  # DynamoDB table for flights
    }
  }

  tags = {
    Environment = "dev"
  }
}

# Reference the existing REST API by ID
resource "aws_api_gateway_rest_api" "flight_management_api" {
  name = "flightManagementAPIs" # Use the name of the existing REST API you are importing
}


# Add a new resource for /bookFlight
resource "aws_api_gateway_resource" "bookFlight_resource" {
  rest_api_id = aws_api_gateway_rest_api.flight_management_api.id
  parent_id   = aws_api_gateway_rest_api.flight_management_api.root_resource_id
  path_part   = "bookFlight"
}

# API Gateway Method for POST /bookFlight
resource "aws_api_gateway_method" "post_bookFlight" {
  rest_api_id   = aws_api_gateway_rest_api.flight_management_api.id
  resource_id   = aws_api_gateway_resource.bookFlight_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# API Gateway Integration with Lambda
resource "aws_api_gateway_integration" "bookFlight_integration" {
  rest_api_id             = aws_api_gateway_rest_api.flight_management_api.id
  resource_id             = aws_api_gateway_resource.bookFlight_resource.id
  http_method             = aws_api_gateway_method.post_bookFlight.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.booking_service.invoke_arn
}

# Lambda Permission for API Gateway
resource "aws_lambda_permission" "apigw_invoke_booking" {
  statement_id  = "AllowAPIGatewayInvokeBooking"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.booking_service.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:eu-north-1:${data.aws_caller_identity.current.account_id}:vxcfjfon57/*/*" # Use existing REST API ID
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.flight_management_api.id
  stage_name  = "dev"

  depends_on = [
    aws_api_gateway_integration.bookFlight_integration
  ]
}

# Output the API Gateway endpoint for booking
output "booking_api_endpoint" {
  value = "${aws_api_gateway_deployment.api_deployment.invoke_url}bookFlight"
}
