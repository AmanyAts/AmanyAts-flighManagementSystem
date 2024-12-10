import json
import boto3

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Bookings')  # Align table name with booking-handler.py

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event, indent=4))  # Debugging: Log event

        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        booking_id = body.get('bookingId')
        updated_seats = body.get('seats')
        updated_date = body.get('departureDate')

        if not booking_id:
            print("Error: bookingId is required")  # Debugging
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'bookingId is required'})
            }

        print(f"Updating booking with bookingId: {booking_id}")  # Debugging

        # Prepare Update Expression
        update_expression = []
        expression_attribute_values = {}

        if updated_seats:
            update_expression.append("seats = :seats")
            expression_attribute_values[":seats"] = updated_seats

        if updated_date:
            update_expression.append("departureDate = :departureDate")
            expression_attribute_values[":departureDate"] = updated_date

        if not update_expression:
            print("Error: No fields to update")  # Debugging
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No fields to update'})
            }

        # Execute update
        response = table.update_item(
            Key={'bookingId': booking_id},
            UpdateExpression="SET " + ", ".join(update_expression),
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW"
        )

        print(f"Booking updated successfully: {json.dumps(response, indent=4)}")  # Debugging
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Booking updated successfully',
                'updatedAttributes': response.get('Attributes', {})
            })
        }
    except Exception as e:
        print(f"Error updating booking: {str(e)}")  # Debugging
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }
