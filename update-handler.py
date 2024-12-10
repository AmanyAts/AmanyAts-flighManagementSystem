import json
import boto3

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('flight_bookings')

def lambda_handler(event, context):
    try:
        # Parse the request body
        body = json.loads(event['body'])
        booking_id = body.get('booking_id')
        updated_flight_details = body.get('flight_details', {})
        updated_passengers = body.get('passengers', None)

        # Validate input
        if not booking_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'booking_id is required'})
            }

        # Prepare Update Expression
        update_expression = []
        expression_attribute_values = {}

        if updated_flight_details:
            update_expression.append("#flight_details = :flight_details")
            expression_attribute_values[":flight_details"] = updated_flight_details

        if updated_passengers is not None:
            update_expression.append("passengers = :passengers")
            expression_attribute_values[":passengers"] = updated_passengers

        if not update_expression:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No fields to update'})
            }

        # Execute update
        response = table.update_item(
            Key={'booking_id': booking_id},
            UpdateExpression="SET " + ", ".join(update_expression),
            ExpressionAttributeNames={"#flight_details": "flight_details"},
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW"
        )

        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Booking updated successfully',
                'updated_attributes': response['Attributes']
            })
        }
    except Exception as e:
        # Handle errors
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
