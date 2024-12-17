import json
import boto3
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Bookings')  # Align table name with booking-handler.py
flights_table = dynamodb.Table('Flights')  # Flights table

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
        updated_seats = body.get('seats')
        updated_date = body.get('departureDate')

        if not booking_id:
            print("Error: bookingId is required")  # Debugging
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'bookingId is required'})
            }

        print(f"Updating booking with bookingId: {booking_id}")  # Debugging

        # Retrieve the booking
        response = table.get_item(Key={'bookingId': booking_id})
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
        flight_response = flights_table.get_item(
            Key={'flightId': flight_id, 'departureDate': updated_date}
        )
        flight = flight_response.get('Item')

        if not flight:
            print(f"Error: Flight with flightId {flight_id} and departureDate {updated_date} not found")  # Debugging
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Flight not found'})
            }

        # Get current seat availability
        available_seats = flight.get('seatAvailability', 0)
        print(f"Available seats for flightId {flight_id}: {available_seats}")  # Debugging

        if updated_seats:
            # Handle the seat subtraction for updates
            original_seats = booking.get('seats', 0)
            seats_diff = updated_seats - original_seats
            # Subtract seats from available seats
            available_seats -= seats_diff
            flights_table.update_item(
                Key={'flightId': flight_id, 'departureDate': updated_date},
                UpdateExpression="SET seatAvailability = :seatAvailability",
                ExpressionAttributeValues={':seatAvailability': available_seats}
            )
            print(f"Seat availability updated for flightId {flight_id}, new available seats: {available_seats}")  # Debugging

        # Prepare update expression for booking
        update_expression = []
        expression_attribute_values = {}

        if updated_seats:
            update_expression.append("seats = :seats")
            expression_attribute_values[":seats"] = Decimal(updated_seats)

        if not update_expression:
            print("Error: No fields to update")  # Debugging
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No fields to update'})
            }

        # Execute booking update
        response = table.update_item(
            Key={'bookingId': booking_id},
            UpdateExpression="SET " + ", ".join(update_expression),
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW"
        )

        # Convert response attributes to native types
        updated_attributes = decimal_to_native(response.get('Attributes', {}))

        print(f"Booking updated successfully: {json.dumps(updated_attributes, indent=4)}")  # Debugging
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Booking updated successfully',
                'updatedAttributes': updated_attributes
            })
        }

    except Exception as e:
        print(f"Error updating booking: {str(e)}")  # Debugging
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }
