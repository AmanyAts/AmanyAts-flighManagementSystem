import boto3
import json
import uuid
from datetime import datetime

def bookFlight(event, context):
    print("Received event:", json.dumps(event, indent=4))  # Debugging: Log the incoming event

    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb')
    bookings_table = dynamodb.Table('Bookings')  # Bookings table
    flights_table = dynamodb.Table('Flights')    # Flights table

    try:
        # Parse request body
        body = json.loads(event.get("body", "{}"))
        print("Request body parsed:", json.dumps(body, indent=4))  # Debugging: Log request body

        user_id = body.get("userId")
        flight_id = body.get("flightId")
        seats = body.get("seats")
        departure_date = body.get("departureDate")

        # Validate input and log missing fields
        missing_fields = []
        if not user_id:
            missing_fields.append("userId")
        if not flight_id:
            missing_fields.append("flightId")
        if not seats:
            missing_fields.append("seats")
        if not departure_date:
            missing_fields.append("departureDate")

        if missing_fields:
            print(f"Validation Error: Missing required fields - {', '.join(missing_fields)}")  # Debugging: Log missing fields
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Missing required fields: {', '.join(missing_fields)}"})
            }

        print(f"Validating flightId: {flight_id}, departureDate: {departure_date} in Flights table...")  # Debugging
        flight = flights_table.get_item(
            Key={
                "flightId": flight_id,
                "departureDate": departure_date
            }
        ).get("Item")

        if not flight:
            print(f"Flight not found for flightId: {flight_id} and departureDate: {departure_date}")  # Debugging
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Flight not found"})
            }

        print(f"Flight found: {json.dumps(flight, indent=4)}")  # Debugging: Log flight details

        available_seats = flight.get("seatAvailability", 0)
        print(f"Available seats for flightId {flight_id}: {available_seats}")  # Debugging

        if seats > available_seats:
            print(f"Error: Requested seats ({seats}) exceed available seats ({available_seats})")  # Debugging
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Not enough seats available"})
            }

        # Generate booking ID and record booking date
        booking_id = str(uuid.uuid4())
        booking_date = datetime.utcnow().isoformat()
        print(f"Generated bookingId: {booking_id}, Booking Date: {booking_date}")  # Debugging

        # Update Flights table (decrease seat availability)
        print(f"Updating seat availability for flightId {flight_id}...")  # Debugging
        flights_table.update_item(
            Key={
                "flightId": flight_id,
                "departureDate": departure_date
            },
            UpdateExpression="SET seatAvailability = seatAvailability - :seats",
            ExpressionAttributeValues={":seats": seats}
        )
        print(f"Seat availability updated for flightId {flight_id}")  # Debugging

        # Insert booking into Bookings table
        print("Inserting booking into Bookings table...")  # Debugging
        bookings_table.put_item(
            Item={
                "bookingId": booking_id,
                "userId": user_id,
                "flightId": flight_id,
                "seats": seats,
                "bookingDate": booking_date
            }
        )
        print(f"Booking created successfully with bookingId: {booking_id}")  # Debugging

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Booking created successfully", "bookingId": booking_id})
        }

    except Exception as e:
        print(f"Error processing booking: {str(e)}")  # Debugging
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error"})
        }
