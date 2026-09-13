# Movie Ticket Booking System

## Check
- FR -> each show belongs to exactly one auditorium

## Running Locally

Start Postgres

```bash
CREATE SCHEMA <schema_name>;

GRANT ALL PRIVILEGES ON SCHEMA {schema_name} TO {user_name};
```

Run Alembic: Look at alembic read my

Then run the app

```
python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Docs

```
http://127.0.0.1:8000/docs
```

## Functional Requirements

The system should support:
- Create movies.
- Create theaters.
    - Add auditoriums/screens to theaters.
        - Configure physical seats inside an auditorium.
        - Generate sellable seat inventory for that show.
    - Schedule a movie show.
- Search/list shows.
- View seat availability for a show.
- Temporarily hold one or more seats.
- Confirm a booking after payment succeeds.
- Cancel a held booking.
- Retrieve booking details.
- Prevent two users from booking the same seat.

## Non Functional Requirements
- Make booking creation idempotent.
- Make payment confirmation idempotent.

Separations
```
HTTP/API
   ↓
Application services
   ↓
Repositories
   ↓
Domain models
   ↓
PostgreSQL
```

Extensibility:
- Should be able to add cancellation policies
- Dynamic Pricing
- coupons
- sear categories
- notifications

Testability:
- services should depend on repositories rather than hard coded database calls

Consistency:
- Either the Seat is selected or not. Clear selection

Transactional:
```mermaid

flowchart TD
    A[Check Seats] -->|if available| B(Lock Seats)
    B --> C(Create Booking)
    C --> D[Mark Seat as HELD]

```

Concurrency Solution:
TODO: 

## Assumptions

For this implementation:
- currency is fixed to INR
- payment processing itself is external
- payment_reference represents successful payment
- authentication is outside scope
- seats can be held for five minutes
- after five minutes, an unconfirmed hold becomes reclaimable
- seats cannot change after the show inventory has been generated
- movie/show administration is assumed trusted

### In Scope
```
Movies
Theaters
Auditoriums
Physical seats
Shows
Show-specific seat inventory
Seat availability
Seat holds
Booking confirmation
Cancellation
Concurrency protection
Idempotency
PostgreSQL persistence
REST API
Alembic
Unit tests
Integration tests
```

### Out of Scope
```
Authentication
Authorization
Real payment gateway
Refund processing
Email/SMS
Coupons
Food ordering
Recommendation engine
Distributed locking
Kafka/event streaming
Multi-region architecture
```

## Entities

```mermaid
erDiagram
   Movie {
      UUID id
      string title
      integer duration_minutes
      string language
   }

   Theater {
      UUID id PK
      string name
      string city "indexed"
   }
   Auditorium {
      UUID id UK
      UUID theater_id UK
      string name
   }
   Seat {
      UUID id
      UUID auditorium_id UK
      string row_label UK
      integer seat_number
      string category
   }
   Show {
      UUID id PK
      UUID movie_id "indexed"
      UUID auditorium_id "indexed"
      datetime starts_at "indexed"
      datetime ends_at 
      Decimal base_price 
      ShowStatus status 
   }
   ShowSeat {
      UUID id PK
      UUID show_id UK "indexed"
      UUID seat_id UK "indexed"
      float price
      string status
      UUID hold_booking_id
      datetime hold_expires_at "indexed"
      method is_available(now)
      method hold()
      method release()
      method mark_booked(booking_id)
   }
   Booking {
      UUID id PK
      UUID show_id
      BookingStatus status
      float total_amount
      datetime expires_at
      UUID payment_reference UK
      string idempotency_key UK
      string request_fingerprint
      datetime created_at
      datetime updated_at
      method confirm()
      method cancel()
      method expire()
   }
   BookingSeat {
      UUID booking_id PK
      UUID show_seat_id PK
      float price
   }

   Theater ||--o{ Auditorium : contains
   Auditorium ||--|{ Seat : contains
   Movie ||--o{ Show : places
   Auditorium ||--|{ Show : contains
   Show ||--|{ ShowSeat : contains
   Seat ||--|{ ShowSeat : contains
   Show ||--|{ Booking : contains
   Booking ||--|{ BookingSeat : contains
   ShowSeat ||--|{ BookingSeat : contains
```

## Critical Booking Workflow

```mermaid
flowchart TD
    A[Booking Service.create_hold] --> B(Check Idempotence Key)
    B --> C(Fetch Show)
    C --> D[SELECT ShowSeat FOR UPDATE]
    D --> E[check availability]
    E --> F[Create Booking]
    F --> G[Mark seats as HELD]
    G --> H[Create BookingSeat]
    H --> I[Commit]
```

### Why select ShowSeat FOR UPDATE Matters

Suppose:
```
Transaction A wants A1
Transaction B wants A1
```
Both querying:
```sql
SELECT ...
FOR UPDATE
```
causes:
```
A obtains lock
B blocks
```
A changes:
```
AVAILABLE -> HELD
```
and commits.

B wakes up and sees:
```
HELD
```
and returns:
```
409 Conflict
```
Without locking:
```
A reads AVAILABLE
B reads AVAILABLE
A writes HELD
B writes HELD
```
The system could sell the same logical seat twice.

### State Machines
Show Seat
```mermaid
flowchart TD
   A[AVAILABLE] --> |Create Hold|B{HELD}
   B --> |timeout cancel|A
   B --> |Payment Success|C[Booked]
```
Booking
```mermaid
flowchart TD
   B{HELD} --> |cancel|C[Cancelled]
   B --> |confirm|D[Booked]
   B --> |expire|E[EXPIRED]
```

## Challenges

“Why not reserve directly in BookingSeat?”

> Because I need a single mutable per-show inventory row that can be atomically locked.

“What happens when two users buy the same seat?”
```
Both transactions issue:

SELECT FOR UPDATE

One acquires the row first.

The other waits and then observes the changed state.
```
“What if the client retries?”

> Idempotency-Key.

“What if payment callback is repeated?”
```
Confirmation is idempotent when the same:

payment_reference

is supplied.
```
“What if two requests use the same payment reference?”
```
Database:

UNIQUE(payment_reference)

provides the final guarantee.
```
“What if the application crashes after payment but before confirmation?”
```
That's a distributed transaction between the payment provider and our database.

A production extension would introduce:

payment records
payment webhook reconciliation
idempotent callbacks
outbox/event processing
```
The local DB transaction alone cannot solves that problem.