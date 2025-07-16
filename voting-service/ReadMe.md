# Requirements

## Functional Requirements

1. Voter registration with identity verification
2. Voter authentication
3. One Voter, One Vote
4. Generate Voting Card, available candidates, current election
5. Vote selection and casting vote
6. Election Setup
7. Election Start Stop

### Voter Registration:

The system shall allow authorized administrators to register new voters, capturing unique identification information (e.g., voter ID, biometrics, pre-assigned secure token).
Low-Level Considerations: Data structures for voter records, secure storage mechanisms (encryption at rest), efficient lookup algorithms. Potential for hardware-level interaction if using biometric scanners or smart card readers.

### Voter Authentication:

The system shall securely authenticate a voter before allowing them to cast a ballot. This may involve verifying their unique ID against registered records, biometric verification, or a secure token.
Low-Level Considerations: Secure hash functions for password/PIN storage, efficient cryptographic operations for token validation, potentially direct interaction with biometric hardware (e.g., fingerprint sensor drivers). Real-time comparison algorithms.

### One Voter, One Vote Enforcement:

The system shall prevent a voter from casting more than one ballot in a given election.
Low-Level Considerations: Atomic operations for marking a voter as "voted," secure flags/bitmaps in memory or persistent storage. Concurrency control if multiple voting stations are in use.

### Ballot Presentation and Casting:

#### Ballot Generation:

The system shall dynamically generate and display the correct ballot for the current election, including candidates/options and relevant instructions.
Low-Level Considerations: Efficient memory management for ballot data, rendering graphics/text on a display (potentially custom display drivers), parsing election configuration data.

#### Vote Selection:
The system shall allow voters to make their selections clearly and unambiguously (e.g., touch screen input, button presses).
Low-Level Considerations: Input device drivers (touchscreen, keypad), debouncing logic for physical buttons, interrupt handling.

#### Vote Review and Confirmation:
The system shall provide a mechanism for voters to review their selections before final submission and confirm their vote.
Low-Level Considerations: Temporary storage for selections, efficient display refresh.

#### Vote Casting (Secure Submission):
Upon confirmation, the system shall securely record the voter's selections as a cast ballot.
Low-Level Considerations: Atomic write operations to non-volatile memory (e.g., flash memory, secure SD card), encryption of ballot data before storage, secure journaling/logging of cast votes. Data integrity checks (checksums, CRCs).

### Ballot Storage and Auditing:

#### Secure Ballot Storage:

The system shall store cast ballots in a highly secure, immutable, and auditable manner, preventing alteration or deletion.
Low-Level Considerations: Write-once memory segments, cryptographic chaining of ballots (blockchain-like structure for integrity), tamper-detection mechanisms (physical and logical).

#### Audit Trail Generation:

The system shall generate a comprehensive and unalterable audit trail of all significant events (e.g., voter login, ballot cast, system errors, administrative actions).
Low-Level Considerations: Secure logging to dedicated flash memory, time-stamping mechanisms (real-time clock interaction), cryptographic signing of log entries.

#### Ballot Verification (Optional but Recommended):

The system shall provide a mechanism for voters to verify that their vote was accurately recorded without revealing their identity or the content of their vote to others. (e.g., a verifiable receipt with a unique, anonymous ID).
Low-Level Considerations: Secure one-way hash functions for receipt generation, robust random number generation for anonymous IDs, potentially secure multiparty computation techniques.

### Election Management and Configuration:

#### Election Setup:

Authorized administrators shall be able to configure election parameters (e.g., election name, dates, candidate list, ballot questions).
Low-Level Considerations: Secure parsing of configuration files (e.g., XML, JSON), data validation routines, secure storage of election configuration.

#### Election Start/Stop:

The system shall allow administrators to securely start and stop the voting process.
Low-Level Considerations: Secure state machine management, access control mechanisms.

#### Election Data Export:

The system shall allow authorized personnel to securely export encrypted ballot data and audit trails for tabulation and analysis.
Low-Level Considerations: Secure data transfer protocols (e.g., encrypted USB, secure network connection), efficient data serialization, key management for decryption.


## Non Functional

1. Audit Trails (voter login, ballot cast, system errors, administrative actions)
2. Data encryption (At transit and at rest)

### Data Encryption (In Transit and At Rest):

All sensitive data (voter information, ballot data, audit logs) shall be encrypted both when stored and when transmitted.
Low-Level Considerations: Selection and implementation of strong encryption algorithms (e.g., AES-256), secure key management, hardware security modules (HSMs) if available.

#### Tamper Detection and Resistance:

The system shall detect and respond to attempts at physical or logical tampering.
Low-Level Considerations: Checksum/CRC verification for code and data integrity, watchdog timers, hardware tamper switches, secure boot processes, memory protection units (MPU/MMU).

#### Fault Tolerance/Recovery:

The system shall be resilient to power failures or other unexpected interruptions and recover gracefully without data loss.
Low-Level Considerations: Non-volatile memory for critical state, battery backup, robust error handling, journaling file systems or custom data structures for atomic writes.

#### Access Control:

The system shall enforce strict role-based access control for all administrative functions.
Low-Level Considerations: User authentication modules, privilege escalation prevention, secure memory segregation.


## Future Work

### User Interface (UI) - Minimalist Focus for Low-Level:

#### Clear and Simple Display:

The system shall display information clearly and concisely, minimizing ambiguity for voters.
Low-Level Considerations: Efficient text/graphics rendering, handling different font sizes/resolutions, basic UI state management.

#### Intuitive Input:

The system shall provide an intuitive method for voters to interact (e.g., large buttons, clear touch zones).
Low-Level Considerations: Responsive input handling, visual feedback for interactions.

### Performance (Crucial for Low-Level):

#### Rapid Vote Casting:
The system shall allow a voter to complete the voting process within a specified timeframe (e.g., X seconds).
Low-Level Considerations: Optimized algorithms for data access and processing, minimizing I/O operations, efficient memory usage.

#### High Throughput (if applicable):
The system shall be capable of processing a large number of votes per hour/day.
Low-Level Considerations: Efficient use of CPU cycles, optimized data structures, potentially multi-threading/concurrency (if the underlying hardware supports it and it makes sense for a single machine).
