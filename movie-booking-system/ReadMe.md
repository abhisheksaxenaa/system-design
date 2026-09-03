## 1. Requirements

### Functional Requirements:

- Movie & Theater Management: Support multiple cinema halls, movies, screens, and scheduled showtimes.

- Seat Inventory: Track individual seat types (VIP, Premium, Standard) and real-time availability states (Available, Locked, Booked).

- Dynamic Pricing (Strategy Pattern): Calculate ticket prices dynamically using pluggable strategies based on factors like showtime (matinee vs. evening), seat tier, and demand/popularity.

- Booking & Seat Locking: Allow users to temporarily lock seats during checkout to prevent double-booking (concurrency safety), expiring after a timeout.

- Database Operations: Fully persist entities and manage state transitions using SQLModel ORM.

### Non-Functional Requirements:

- **Extensibility**: Easily add new pricing rules without modifying core booking code (Open/Closed Principle).

- **Data Integrity**: Ensure transactional isolation to handle race conditions on seat reservations.

### Future Requirements:

- Have multiple cinemas and ability to select a cinema

- Need to show cinemas based on location

- Search shows by movie

## 2. Entities and Services

### Core Entities:

- Entities (SQLModel Models): User, Movie, Theater, Screen, Seat, Showtime, Booking, ShowtimeSeat.

- Strategy Interface: PricingStrategy (defines calculate_price()).

- Concrete Strategies: StandardPricingStrategy, MatineeDiscountStrategy, PopularityDemandStrategy.

- Core Services:

    - PricingService: Context class that executes the active strategy.

    - BookingService: Handles seat locks, price calculation, and checkout persistence.

## 3. Design Patterns Used

**Strategy Pattern**: For multi-gateway payment processing (PaymentStrategy, UPIPayment, CreditCardPayment).

**State Pattern / Enum State Machine**: For managing ShowSeat status and BookingStatus.

**Repository/Service Pattern**: To decouple SQLModel database persistence from business logic.