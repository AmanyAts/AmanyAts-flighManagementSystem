# Flight Management System

The **Flight Management System** is a serverless application that manages flight bookings, cancellations, updates, and searches. Built using AWS Lambda and DynamoDB, this system provides an efficient and scalable solution for flight management.

---

## Features

- **Booking Flights:** Allows users to book flights, verifying seat availability and managing booking details.
- **Canceling Bookings:** Enables users to cancel their bookings, updating the booking status in the system.
- **Updating Bookings:** Provides functionality to update booking details such as the number of seats or departure date.
- **Searching Flights:** Allows users to search for available flights based on departure and destination cities and departure dates.

---

## Architecture

The system leverages the following AWS services:

- **AWS Lambda:** For handling the booking, cancellation, update, and search operations.
- **Amazon DynamoDB:** As the primary database for storing flight and booking details.

Each handler is implemented as a standalone Lambda function, ensuring modularity and scalability.

---

## Handlers

### 1. **Booking Handler** (`booking-handler.py`)
- **Functionality:** 
  - Validates flight availability and user input.
  - Updates seat availability in the Flights table.
  - Adds a new booking record in the Bookings table.
- **Dependencies:** 
  - DynamoDB tables: `Flights` and `Bookings`.

### 2. **Cancel Handler** (`cancel-handler.py`)
- **Functionality:** 
  - Cancels a booking by updating the status of the booking in the `Bookings` table to `canceled`.
- **Dependencies:**
  - DynamoDB table: `Bookings`.

### 3. **Update Handler** (`update-handler.py`)
- **Functionality:** 
  - Updates booking details, such as the number of seats or the departure date.
- **Dependencies:**
  - DynamoDB table: `Bookings`.

### 4. **Search Handler** (`search-handler.py`)
- **Functionality:** 
  - Searches for flights based on departure city, destination city, and departure date.
- **Dependencies:**
  - DynamoDB table: `Flights`.

---

## Setup and Deployment

1. **Prerequisites:**
   - AWS account with necessary permissions for Lambda and DynamoDB.
   - AWS CLI installed and configured.
   - Python 3.x installed locally.

2. **DynamoDB Tables:**
   - Create two DynamoDB tables:
     - **Flights** (Primary Key: `flightId`, Sort Key: `departureDate`)
     - **Bookings** (Primary Key: `bookingId`)

3. **Deployment:**
   - Package each handler as a zip file.
   - Deploy the Lambda functions using AWS Management Console or AWS CLI.

4. **Environment Variables:**
   - Specify the table names (`Flights` and `Bookings`) as environment variables for the Lambda functions.

---

## Usage

### Booking Flights
Send a POST request to the booking endpoint with the following JSON body:
```json
{
  "userId": "12345",
  "flightId": "FL123",
  "seats": 2,
  "departureDate": "2024-12-20"
}
