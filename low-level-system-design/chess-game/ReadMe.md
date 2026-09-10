## Functional Requirements

1. Board & Pieces: there should be a 8x8 board. There will be different pieces
    - King
    - Queen
    - Rook
    - Knight
    - Bishop
    - Pawn
2. Turn Management: Alternate turns between White and Black players; White moves first.
3. Move Validation: Validate piece movement vectors, paths, and legal destination squares (prevent friendly fire and path blockage).
4. Game State: Track board states such as ACTIVE, WHITE_WIN, BLACK_WIN, and DRAW.

## Non Functional Requirements

- Extensibility: Easily add new piece movement capabilities without modifying existing logic (Open/Closed Principle).
- State Encapsulation: Maintain clean decoupling between the game engine logic and data persistence layers.

## Entities & Services

- Enums
    - Color
    - GameStatus
- Model
    - Position
    - Piece
    - Board
    - Move
- Controller & Service
    - GameController
- Repository
    - DatabaseRepository

## Design Patterns Used

- **Strategy Pattern**: Implemented inside concrete Piece subclasses to isolate distinct movement rules for each piece type.

- **Factory Pattern**: Used to dynamically instantiate Piece objects based on type, color, and initial board coordinate mappings.

- **Repository Pattern**: Separates domain entities (GameController, Board) from persistence logic (DatabaseRepository), preventing SQL queries from leaking into game rules.

- **Command Pattern (Implicit)**: Encapsulated inside the Move class to keep an audit trail of executed moves.
