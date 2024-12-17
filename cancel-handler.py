import json
import boto3
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
bookings_table = dynamodb.Table('Bookings')  # Bookings table
flights_table = dynamodb.Table('Flights')    # Flights table

# Helper function to convert Decimal to native Python types
def decimal_to_native(obj):
    if isinstance(obj, list):
        return [decimal_to_native(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj) if obj % 1 != 0 else int(obj)  # Convert Decimal to int or float
    return obj

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

        # Retrieve the booking
        response = bookings_table.get_item(Key={'bookingId': booking_id})
        booking = response.get('Item')

        if not booking:
            print(f"Error: Booking with bookingId {booking_id} not found")  # Debugging
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Booking not found'})
            }

        # Check if the booking is already canceled
        if booking.get('status') == 'canceled':
            print(f"Error: Booking with bookingId {booking_id} is already canceled")  # Debugging
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Booking has already been canceled'})
            }

        # Retrieve the associated flight details
        flight_id = booking['flightId']
        departure_date = booking['departureDate']
        seats = booking['seats']

        flight_response = flights_table.get_item(
            Key={'flightId': flight_id, 'departureDate': departure_date}
        )
        flight = flight_response.get('Item')

        if not flight:
            print(f"Error: Flight with flightId {flight_id} and departureDate {departure_date} not found")  # Debugging
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Flight not found'})
            }

        # Update seat availability (add the seats back)
        available_seats = flight.get('seatAvailability', 0)
        print(f"Available seats before cancellation for flightId {flight_id}: {available_seats}")  # Debugging

        # Add the seats back to the flight
        updated_seats = available_seats + seats
        flights_table.update_item(
            Key={'flightId': flight_id, 'departureDate': departure_date},
            UpdateExpression="SET seatAvailability = :seatAvailability",
            ExpressionAttributeValues={':seatAvailability': updated_seats}
        )
        print(f"Seat availability updated after cancellation for flightId {flight_id}, new available seats: {updated_seats}")  # Debugging

        # Mark the booking as canceled
        bookings_table.update_item(
            Key={'bookingId': booking_id},
            UpdateExpression="SET #status = :status",
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':status': 'canceled'},
            ReturnValues="UPDATED_NEW"
        )

        # Convert the response to a serializable format (handle Decimals)
        response_body = {
            'message': 'Booking canceled successfully',
            'bookingId': booking_id
        }
        response_body = decimal_to_native(response_body)  # Convert Decimal to native types

        print(f"Booking canceled successfully: {json.dumps(response_body, indent=4)}")  # Debugging
        return {
            'statusCode': 200,
            'body': json.dumps(response_body)
        }

    except Exception as e:
        print(f"Error canceling booking: {str(e)}")  # Debugging
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }
