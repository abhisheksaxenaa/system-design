## 1. Requirements

### Functional Requirements:

- Browse Shows: Users can view theaters, movies, and available shows.

- Seat Selection & Locking: Users select seats for a show. Seats are locked temporarily (e.g., 10 minutes) during payment to prevent double booking.

- Booking & Payment: Users can book locked seats and complete payment.

- Concurrency Handling: Multiple users trying to book the same seat simultaneously must be handled safely (ACID compliance via database locks).

### Non-Functional Requirements:

- **High Availability & Consistency**: Strong consistency for seat reservation (no double bookings).

- **Extensibility**: Easy to add new payment methods or seat types.

### Future Requirements:

- Have multiple cinemas and ability to select a cinema

- Need to show cinemas based on location

- Search shows by movie

## 2. Entities and Services

### Core Entities:

**User**: Customer details.

**Theater & Screen**: Physical venue and individual screens.

**Movie**: Movie metadata.

**Show**: A movie screening at a specific screen, time, and date.

**Seat**: Physical seats in a screen (e.g., VIP, Regular).

**ShowSeat**: The state of a specific seat for a given show (AVAILABLE, LOCKED, BOOKED).

**Booking**: Reservation record linked to a user, show, and booked seats.

**Payment**: Payment state (PENDING, SUCCESS, FAILED).

## 3. Design Patterns Used

**Strategy Pattern**: For multi-gateway payment processing (PaymentStrategy, UPIPayment, CreditCardPayment).

**State Pattern / Enum State Machine**: For managing ShowSeat status and BookingStatus.

**Repository/Service Pattern**: To decouple SQLAlchemy database persistence from business logic.