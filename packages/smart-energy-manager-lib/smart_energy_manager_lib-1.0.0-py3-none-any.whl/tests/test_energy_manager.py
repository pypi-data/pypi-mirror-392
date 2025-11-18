"""
Unit tests for Energy Manager library
"""

import pytest
from datetime import datetime
from energy_manager import EnergyManager, EnergyAccount, Transaction


class TestEnergyAccount:
    """Test EnergyAccount class"""

    def test_create_account(self):
        """Test creating an energy account"""
        account = EnergyAccount(
            user_id=1,
            generated=150.0,
            consumed=100.0,
            credits=10.0
        )

        assert account.user_id == 1
        assert account.generated == 150.0
        assert account.consumed == 100.0
        assert account.credits == 10.0

    def test_calculate_surplus(self):
        """Test surplus calculation"""
        account = EnergyAccount(user_id=1, generated=150, consumed=100)
        assert account.calculate_surplus() == 50.0

    def test_calculate_deficit(self):
        """Test deficit calculation"""
        account = EnergyAccount(user_id=1, generated=80, consumed=120)
        assert account.calculate_deficit() == 40.0

    def test_get_status_surplus(self):
        """Test status when user has surplus"""
        account = EnergyAccount(user_id=1, generated=150, consumed=100)
        assert account.get_status() == "surplus"

    def test_get_status_deficit(self):
        """Test status when user has deficit"""
        account = EnergyAccount(user_id=1, generated=80, consumed=120)
        assert account.get_status() == "deficit"

    def test_get_status_balanced(self):
        """Test status when balanced"""
        account = EnergyAccount(user_id=1, generated=100, consumed=100)
        assert account.get_status() == "balanced"

    def test_get_net_energy(self):
        """Test net energy calculation"""
        account = EnergyAccount(user_id=1, generated=150, consumed=100)
        assert account.get_net_energy() == 50.0


class TestTransaction:
    """Test Transaction class"""

    def test_create_transaction(self):
        """Test creating a transaction"""
        tx = Transaction(
            transaction_id="TXN-001",
            from_user="user1",
            to_user="user2",
            amount=10.0,
            transaction_type="loan",
            timestamp=datetime.now()
        )

        assert tx.transaction_id == "TXN-001"
        assert tx.amount == 10.0
        assert tx.transaction_type == "loan"

    def test_validate_valid_transaction(self):
        """Test validation of valid transaction"""
        tx = Transaction(
            transaction_id="TXN-001",
            from_user="user1",
            to_user="user2",
            amount=10.0,
            transaction_type="loan",
            timestamp=datetime.now()
        )

        valid, message = tx.validate()
        assert valid is True
        assert message == "Valid"

    def test_validate_invalid_type(self):
        """Test validation with invalid type"""
        tx = Transaction(
            transaction_id="TXN-001",
            from_user="user1",
            to_user="user2",
            amount=10.0,
            transaction_type="invalid",
            timestamp=datetime.now()
        )

        valid, message = tx.validate()
        assert valid is False
        assert "Invalid transaction type" in message

    def test_validate_negative_amount(self):
        """Test validation with negative amount"""
        tx = Transaction(
            transaction_id="TXN-001",
            from_user="user1",
            to_user="user2",
            amount=-10.0,
            transaction_type="loan",
            timestamp=datetime.now()
        )

        valid, message = tx.validate()
        assert valid is False
        assert "positive" in message.lower()


class TestEnergyManager:
    """Test EnergyManager class"""

    def test_create_manager(self):
        """Test creating energy manager"""
        manager = EnergyManager(buyback_rate=0.15)
        assert manager.buyback_rate == 0.15

    def test_process_buyback_success(self):
        """Test successful buyback"""
        manager = EnergyManager(buyback_rate=0.15)
        account = EnergyAccount(user_id=1, generated=150,
                                consumed=100, credits=10)

        success, message, credits_earned = manager.process_buyback(account, 50)

        assert success is True
        assert credits_earned == 7.5  # 50 * 0.15
        assert account.credits == 17.5  # 10 + 7.5

    def test_process_buyback_insufficient_surplus(self):
        """Test buyback with insufficient surplus"""
        manager = EnergyManager(buyback_rate=0.15)
        account = EnergyAccount(user_id=1, generated=150,
                                consumed=100, credits=10)

        success, message, credits_earned = manager.process_buyback(
            account, 100)

        assert success is False
        assert "Insufficient surplus" in message
        assert credits_earned == 0.0

    def test_process_loan_success(self):
        """Test successful loan"""
        manager = EnergyManager()
        from_account = EnergyAccount(
            user_id=1, generated=150, consumed=100, credits=20)
        to_account = EnergyAccount(
            user_id=2, generated=80, consumed=120, credits=5)

        success, message = manager.process_loan(from_account, to_account, 10)

        assert success is True
        assert from_account.credits == 10
        assert to_account.credits == 15

    def test_process_loan_insufficient_credits(self):
        """Test loan with insufficient credits"""
        manager = EnergyManager()
        from_account = EnergyAccount(
            user_id=1, generated=150, consumed=100, credits=5)
        to_account = EnergyAccount(
            user_id=2, generated=80, consumed=120, credits=5)

        success, message = manager.process_loan(from_account, to_account, 10)

        assert success is False
        assert "Insufficient credits" in message

    def test_process_donation_success(self):
        """Test successful donation"""
        manager = EnergyManager()
        from_account = EnergyAccount(
            user_id=1, generated=150, consumed=100, credits=20)
        to_account = EnergyAccount(
            user_id=2, generated=80, consumed=120, credits=5)

        success, message = manager.process_donation(
            from_account, to_account, 10)

        assert success is True
        assert from_account.credits == 10
        assert to_account.credits == 15

    def test_calculate_energy_efficiency(self):
        """Test energy efficiency calculation"""
        manager = EnergyManager()
        account = EnergyAccount(user_id=1, generated=150, consumed=100)

        efficiency = manager.calculate_energy_efficiency(account)
        assert efficiency == 1.5  # 150 / 100

    def test_calculate_potential_earnings(self):
        """Test potential earnings calculation"""
        manager = EnergyManager(buyback_rate=0.15)

        earnings = manager.calculate_potential_earnings(50)
        assert earnings == 7.5  # 50 * 0.15

    def test_generate_summary(self):
        """Test summary generation"""
        manager = EnergyManager(buyback_rate=0.15)
        account = EnergyAccount(user_id=1, generated=150,
                                consumed=100, credits=10)

        summary = manager.generate_summary(account)

        assert summary['user_id'] == 1
        assert summary['generated'] == 150
        assert summary['consumed'] == 100
        assert summary['surplus'] == 50
        assert summary['deficit'] == 0
        assert summary['credits'] == 10
        assert summary['status'] == 'surplus'
        assert summary['efficiency'] == 1.5
        assert summary['potential_earnings'] == 7.5

    def test_validate_transfer_valid(self):
        """Test transfer validation - valid"""
        manager = EnergyManager()
        account = EnergyAccount(user_id=1, generated=150,
                                consumed=100, credits=20)

        valid, message = manager.validate_transfer(account, 10, 'loan')
        assert valid is True

    def test_validate_transfer_insufficient(self):
        """Test transfer validation - insufficient"""
        manager = EnergyManager()
        account = EnergyAccount(user_id=1, generated=150,
                                consumed=100, credits=5)

        valid, message = manager.validate_transfer(account, 10, 'loan')
        assert valid is False
        assert "Insufficient credits" in message


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
