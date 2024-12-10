import json
import boto3

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Bookings')  # Align table name with booking-handler.py

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event, indent=4))  # Debugging: Log event

        # Parse request body
        body = json.loads(event.get('body', '{}'))
        booking_id = body.get('bookingId')

        if not booking_id:
            print("Error: bookingId is required")  # Debugging
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'bookingId is required'})
            }

        print(f"Canceling booking with bookingId: {booking_id}")  # Debugging

        # Update the booking status to "canceled"
        response = table.update_item(
            Key={'bookingId': booking_id},
            UpdateExpression="SET #status = :status",
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':status': 'canceled'},
            ReturnValues="UPDATED_NEW"
        )

        print(f"Booking canceled successfully: {json.dumps(response, indent=4)}")  # Debugging
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Booking canceled successfully',
                'updatedAttributes': response.get('Attributes', {})
            })
        }
    except Exception as e:
        print(f"Error canceling booking: {str(e)}")  # Debugging
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }
