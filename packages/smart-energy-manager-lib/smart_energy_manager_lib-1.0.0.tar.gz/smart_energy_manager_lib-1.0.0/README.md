# Energy Manager

A Python library for managing solar energy generation, consumption, storage, and trading in smart energy systems.

## Features

- **Energy Account Management**: Track energy generation and consumption
- **Surplus/Deficit Calculations**: Automatically calculate energy surplus or deficit
- **Buyback Processing**: Convert surplus energy to credits
- **Energy Loans**: Transfer energy credits between users
- **Energy Donations**: Support community energy sharing
- **Efficiency Calculations**: Measure energy efficiency metrics

## Installation
```bash
pip install energy-manager
```

## Quick Start
```python
from energy_manager import EnergyManager, EnergyAccount

# Initialize the energy manager
manager = EnergyManager(buyback_rate=0.15)

# Create an energy account
account = EnergyAccount(
    user_id=1,
    generated=150.0,  # kWh generated
    consumed=100.0,   # kWh consumed
    credits=10.0      # Current credits
)

# Calculate surplus
surplus = account.calculate_surplus()
print(f"Surplus: {surplus} kWh")

# Process buyback
success, message, credits_earned = manager.process_buyback(account, 50.0)
if success:
    print(f"Buyback successful! Earned {credits_earned} credits")

# Get account summary
summary = manager.generate_summary(account)
print(summary)
```

## Core Components

### EnergyAccount

Represents a user's energy account with generation, consumption, and credit tracking.
```python
account = EnergyAccount(
    user_id=1,
    generated=200.0,
    consumed=150.0,
    credits=25.0
)

# Get account status
status = account.get_status()  # Returns: 'surplus', 'deficit', or 'balanced'

# Calculate metrics
surplus = account.calculate_surplus()
deficit = account.calculate_deficit()
```

### EnergyManager

Core manager for energy operations and calculations.
```python
manager = EnergyManager(buyback_rate=0.15)

# Process buyback
success, message, credits = manager.process_buyback(account, kwh_amount)

# Process loan
success, message = manager.process_loan(from_account, to_account, credit_amount)

# Process donation
success, message = manager.process_donation(from_account, to_account, credit_amount)

# Calculate efficiency
efficiency = manager.calculate_energy_efficiency(account)

# Get comprehensive summary
summary = manager.generate_summary(account)
```

### Transaction

Represents an energy transaction with validation.
```python
from energy_manager import Transaction

transaction = Transaction(
    transaction_id="TXN-001",
    from_user="user1",
    to_user="user2",
    amount=10.0,
    transaction_type="loan",
    timestamp=datetime.now()
)

# Validate transaction
is_valid, message = transaction.validate()
```

## Use Cases

### Smart Energy Communities

Perfect for residential solar communities where households:
- Generate solar energy
- Track consumption
- Share excess energy with neighbors
- Trade energy credits

### Energy Trading Platforms

Build platforms that enable:
- Peer-to-peer energy trading
- Community energy banks
- Microgrid management
- Energy credit systems

### Sustainability Applications

Develop applications for:
- Carbon footprint tracking
- Renewable energy adoption
- Energy independence measurement
- Community sustainability goals

## API Reference

### EnergyAccount

**Methods:**
- `calculate_surplus()` - Returns surplus energy in kWh
- `calculate_deficit()` - Returns energy deficit in kWh
- `get_status()` - Returns account status ('surplus', 'deficit', 'balanced')
- `get_net_energy()` - Returns net energy (positive for surplus, negative for deficit)

### EnergyManager

**Methods:**
- `process_buyback(account, kwh_amount)` - Process energy buyback transaction
- `process_loan(from_account, to_account, credit_amount)` - Transfer credits as loan
- `process_donation(from_account, to_account, credit_amount)` - Donate credits
- `calculate_energy_efficiency(account)` - Calculate efficiency ratio
- `calculate_potential_earnings(surplus_kwh)` - Calculate potential credit earnings
- `generate_summary(account)` - Generate comprehensive account summary
- `validate_transfer(from_account, amount, transfer_type)` - Validate transfer eligibility

### Transaction

**Attributes:**
- `transaction_id` - Unique transaction identifier
- `from_user` - Source user
- `to_user` - Destination user
- `amount` - Transaction amount
- `transaction_type` - Type of transaction ('buyback', 'loan', 'donation', 'repayment')
- `timestamp` - Transaction timestamp

**Methods:**
- `validate()` - Validate transaction data
- `get_type_display()` - Get human-readable transaction type

## Configuration

### Buyback Rate

Configure the rate for converting kWh to credits:
```python
# Default rate: 0.15 credits per kWh
manager = EnergyManager(buyback_rate=0.15)

# Custom rate
manager = EnergyManager(buyback_rate=0.20)
```

### Loan Interest

Configure interest rate for loans (future feature):
```python
manager = EnergyManager(buyback_rate=0.15, loan_interest=0.05)
```

## Examples

### Complete Workflow
```python
from energy_manager import EnergyManager, EnergyAccount

# Initialize
manager = EnergyManager(buyback_rate=0.15)

# Create accounts for two users
alice = EnergyAccount(user_id=1, generated=200, consumed=100, credits=5)
bob = EnergyAccount(user_id=2, generated=50, consumed=120, credits=2)

# Alice has surplus, sells 50 kWh
success, msg, earned = manager.process_buyback(alice, 50)
print(f"Alice: {msg}, earned {earned} credits")

# Alice loans 5 credits to Bob
success, msg = manager.process_loan(alice, bob, 5)
print(f"Loan: {msg}")

# Check final status
alice_summary = manager.generate_summary(alice)
bob_summary = manager.generate_summary(bob)

print(f"Alice status: {alice_summary['status']}, credits: {alice_summary['credits']}")
print(f"Bob status: {bob_summary['status']}, credits: {bob_summary['credits']}")
```

## Testing

Run tests with pytest:
```bash
# Install dev dependencies
pip install energy-manager[dev]

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=energy_manager --cov-report=html
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Created as part of the Smart Energy Platform project at National College of Ireland.

## Changelog

### Version 1.0.0 (2025-01-01)
- Initial release
- Core energy management functionality
- Buyback, loan, and donation features
- Account status tracking
- Efficiency calculations