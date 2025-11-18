"""
Energy calculation classes
"""


class EnergyAccount:
    """Represents a user's energy account"""

    def __init__(self, user_id, generated=0.0, consumed=0.0, credits=0.0):
        self.user_id = user_id
        self.generated = float(generated)  # kWh generated
        self.consumed = float(consumed)    # kWh consumed
        self.credits = float(credits)      # Energy credits balance

    def calculate_surplus(self):
        """Calculate surplus energy (kWh)"""
        return max(0, self.generated - self.consumed)

    def calculate_deficit(self):
        """Calculate energy deficit (kWh)"""
        return max(0, self.consumed - self.generated)

    def get_status(self):
        """Get current account status"""
        surplus = self.calculate_surplus()
        deficit = self.calculate_deficit()

        if surplus > 0:
            return "surplus"
        elif deficit > 0:
            return "deficit"
        else:
            return "balanced"

    def get_net_energy(self):
        """Get net energy (positive for surplus, negative for deficit)"""
        return self.generated - self.consumed


class Transaction:
    """Represents an energy transaction"""

    BUYBACK = 'buyback'
    LOAN = 'loan'
    DONATION = 'donation'
    REPAYMENT = 'repayment'

    TYPES = [BUYBACK, LOAN, DONATION, REPAYMENT]

    def __init__(self, transaction_id, from_user, to_user,
                 amount, transaction_type, timestamp, description=''):
        self.transaction_id = transaction_id
        self.from_user = from_user
        self.to_user = to_user
        self.amount = float(amount)
        self.transaction_type = transaction_type
        self.timestamp = timestamp
        self.description = description

    def validate(self):
        """Validate transaction"""
        if self.transaction_type not in self.TYPES:
            return False, "Invalid transaction type"
        if self.amount <= 0:
            return False, "Amount must be positive"
        if not self.from_user:
            return False, "From user is required"
        return True, "Valid"

    def get_type_display(self):
        """Get readable transaction type"""
        type_map = {
            self.BUYBACK: 'Energy Buyback',
            self.LOAN: 'Energy Loan',
            self.DONATION: 'Energy Donation',
            self.REPAYMENT: 'Loan Repayment'
        }
        return type_map.get(self.transaction_type, 'Unknown')
