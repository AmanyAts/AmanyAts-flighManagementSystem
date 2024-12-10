import json
import boto3

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('flight_bookings')

def lambda_handler(event, context):
    try:
        # Parse request body
        body = json.loads(event['body'])
        booking_id = body.get('booking_id')

        if not booking_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'booking_id is required'})
            }

        # Update the booking status to "canceled"
        response = table.update_item(
            Key={'booking_id': booking_id},
            UpdateExpression="SET #status = :status",
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':status': 'canceled'},
            ReturnValues="UPDATED_NEW"
        )

        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Booking canceled successfully',
                'updated_attributes': response['Attributes']
            })
        }
    except Exception as e:
        # Handle errors
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
