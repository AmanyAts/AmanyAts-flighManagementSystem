import boto3
import json
from boto3.dynamodb.conditions import Attr
from decimal import Decimal

# Helper function to convert Decimal to native Python types
def decimal_to_native(obj):
    if isinstance(obj, list):
        return [decimal_to_native(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        # Convert Decimal to int if it has no fractional part, otherwise float
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj

def searchFlights(event, context):
    print("Received event:", json.dumps(event))  # Debugging: Log the incoming event

    # Initialize the DynamoDB resource
    dynamodb = boto3.resource('dynamodb')
    table_name = 'Flights'  # Ensure this matches your DynamoDB table name
    print(f"Using DynamoDB table: {table_name}")  # Debugging: Log table name

    table = dynamodb.Table(table_name)

    # Extract query parameters from the event
    params = event.get('queryStringParameters', {})
    print("Query parameters:", params)  # Debugging: Log query parameters

    departure_city = params.get('departureCity')
    destination_city = params.get('destinationCity')
    departure_date = params.get('departureDate')

    # Validate input parameters
    if not (departure_city and destination_city and departure_date):
        print("Error: Missing required query parameters")  # Debugging: Log missing parameters
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing required query parameters"})
        }

    try:
        # Query DynamoDB with the provided parameters
        print("Querying DynamoDB with filters...")  # Debugging: Log query filters
        response = table.scan(
            FilterExpression=Attr('departureCity').eq(departure_city) &
                             Attr('destinationCity').eq(destination_city) &
                             Attr('departureDate').eq(departure_date)
        )
        print("DynamoDB response:", response)  # Debugging: Log DynamoDB response

        # Convert DynamoDB response to JSON-serializable format
        flights = response.get('Items', [])
        if not flights:
            print("No flights found.")  # Debugging: Log no results found
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "No flights found"})
            }

        flights_serialized = decimal_to_native(flights)
        return {
            "statusCode": 200,
            "body": json.dumps(flights_serialized)
        }

    except Exception as e:
        # Log and return an error response in case of exceptions
        print(f"Error querying DynamoDB: {str(e)}")  # Debugging: Log exceptions
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error"})
        }
