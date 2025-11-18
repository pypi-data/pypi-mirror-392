"""
Core energy management logic
"""
from .calculator import EnergyAccount


class EnergyManager:
    """Core energy management system"""

    def __init__(self, buyback_rate=0.15, loan_interest=0.0):
        """
        Initialize EnergyManager

        Args:
            buyback_rate: Rate for converting kWh to credits (default: 0.15 credits per kWh)
            loan_interest: Interest rate for loans (default: 0.0)
        """
        self.buyback_rate = buyback_rate
        self.loan_interest = loan_interest

    def process_buyback(self, account, kwh_amount):
        """
        Process energy buyback - convert surplus energy to credits

        Args:
            account: EnergyAccount object
            kwh_amount: Amount of kWh to sell back

        Returns:
            tuple: (success: bool, message: str, credits_earned: float)
        """
        surplus = account.calculate_surplus()

        if kwh_amount > surplus:
            return False, "Insufficient surplus energy", 0.0

        if kwh_amount <= 0:
            return False, "Invalid amount", 0.0

        credits_earned = kwh_amount * self.buyback_rate
        account.credits += credits_earned

        message = "Buyback successful: {0} kWh sold for {1:.2f} credits".format(
            kwh_amount, credits_earned)
        return True, message, credits_earned

    def process_loan(self, from_account, to_account, credit_amount):
        """
        Process energy credit loan from one user to another

        Args:
            from_account: Lender's EnergyAccount
            to_account: Borrower's EnergyAccount
            credit_amount: Amount of credits to loan

        Returns:
            tuple: (success: bool, message: str)
        """
        if credit_amount <= 0:
            return False, "Invalid loan amount"

        if from_account.credits < credit_amount:
            return False, "Insufficient credits to loan"

        from_account.credits -= credit_amount
        to_account.credits += credit_amount

        message = "Loan successful: {0:.2f} credits transferred".format(
            credit_amount)
        return True, message

    def process_donation(self, from_account, to_account, credit_amount):
        """
        Process energy credit donation

        Args:
            from_account: Donor's EnergyAccount
            to_account: Recipient's EnergyAccount
            credit_amount: Amount of credits to donate

        Returns:
            tuple: (success: bool, message: str)
        """
        if credit_amount <= 0:
            return False, "Invalid donation amount"

        if from_account.credits < credit_amount:
            return False, "Insufficient credits to donate"

        from_account.credits -= credit_amount
        to_account.credits += credit_amount

        message = "Donation successful: {0:.2f} credits donated".format(
            credit_amount)
        return True, message

    def calculate_energy_efficiency(self, account):
        """
        Calculate energy efficiency ratio

        Args:
            account: EnergyAccount object

        Returns:
            float: Efficiency ratio (generated/consumed)
        """
        if account.consumed == 0:
            return float('inf') if account.generated > 0 else 0.0

        return account.generated / account.consumed

    def calculate_potential_earnings(self, surplus_kwh):
        """
        Calculate potential earnings from surplus

        Args:
            surplus_kwh: Amount of surplus energy in kWh

        Returns:
            float: Potential credits to earn
        """
        return surplus_kwh * self.buyback_rate

    def generate_summary(self, account):
        """
        Generate account summary

        Args:
            account: EnergyAccount object

        Returns:
            dict: Summary information
        """
        efficiency = self.calculate_energy_efficiency(account)
        surplus = account.calculate_surplus()

        return {
            'user_id': account.user_id,
            'generated': round(account.generated, 2),
            'consumed': round(account.consumed, 2),
            'surplus': round(surplus, 2),
            'deficit': round(account.calculate_deficit(), 2),
            'credits': round(account.credits, 2),
            'status': account.get_status(),
            'efficiency': round(efficiency, 2) if efficiency != float('inf') else 'N/A',
            'potential_earnings': round(self.calculate_potential_earnings(surplus), 2)
        }

    def validate_transfer(self, from_account, amount, transfer_type='loan'):
        """
        Validate if a transfer can be made

        Args:
            from_account: EnergyAccount object
            amount: Amount to transfer
            transfer_type: Type of transfer

        Returns:
            tuple: (valid: bool, message: str)
        """
        if amount <= 0:
            return False, "Amount must be positive"

        if from_account.credits < amount:
            message = "Insufficient credits. Available: {0:.2f}".format(
                from_account.credits)
            return False, message

        return True, "Transfer valid"
