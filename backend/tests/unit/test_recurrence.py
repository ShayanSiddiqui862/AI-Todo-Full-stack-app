import pytest
from datetime import datetime, timedelta
from backend.src.services.recurrence import calculate_next_occurrence, create_next_recurring_instance


class TestRecurrenceCalculation:
    """Unit tests for recurrence calculation logic."""

    def test_calculate_daily_recurrence(self):
        """Test daily recurrence calculation."""
        current_date = datetime(2026, 2, 8, 10, 0, 0)
        next_date = calculate_next_occurrence(current_date, "daily", 1)
        expected = datetime(2026, 2, 9, 10, 0, 0)
        assert next_date == expected

    def test_calculate_weekly_recurrence(self):
        """Test weekly recurrence calculation."""
        current_date = datetime(2026, 2, 8, 10, 0, 0)  # Sunday
        next_date = calculate_next_occurrence(current_date, "weekly", 1)
        expected = datetime(2026, 2, 15, 10, 0, 0)  # Next Sunday
        assert next_date == expected

    def test_calculate_monthly_recurrence_same_day(self):
        """Test monthly recurrence calculation with same day."""
        current_date = datetime(2026, 2, 8, 10, 0, 0)
        next_date = calculate_next_occurrence(current_date, "monthly", 1)
        expected = datetime(2026, 3, 8, 10, 0, 0)
        assert next_date == expected

    def test_calculate_monthly_recurrence_end_of_month(self):
        """Test monthly recurrence calculation handling end of month."""
        # January 31st to February (which doesn't have 31 days)
        current_date = datetime(2026, 1, 31, 10, 0, 0)
        next_date = calculate_next_occurrence(current_date, "monthly", 1)
        # Should go to February 28th (or 29th in leap years)
        expected = datetime(2026, 2, 28, 10, 0, 0)
        assert next_date == expected

    def test_calculate_monthly_recurrence_with_interval(self):
        """Test monthly recurrence calculation with interval > 1."""
        current_date = datetime(2026, 2, 8, 10, 0, 0)
        next_date = calculate_next_occurrence(current_date, "monthly", 3)  # Every 3 months
        expected = datetime(2026, 5, 8, 10, 0, 0)
        assert next_date == expected

    def test_calculate_invalid_recurrence_type(self):
        """Test invalid recurrence type returns original date."""
        current_date = datetime(2026, 2, 8, 10, 0, 0)
        next_date = calculate_next_occurrence(current_date, "invalid", 1)
        expected = current_date  # Should return original date for invalid type
        assert next_date == expected

    def test_create_next_recurring_instance_basic(self):
        """Test creating next recurring instance with basic data."""
        task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'completed': True,
            'user_id': 'user123',
            'priority': 'medium',
            'tags': ['test', 'recurring'],
            'due_date': datetime(2026, 2, 8, 10, 0, 0),
            'remind_at': datetime(2026, 2, 8, 9, 0, 0),
            'recurrence_type': 'daily',
            'recurrence_interval': 1,
            'created_at': datetime(2026, 2, 1, 10, 0, 0),
            'updated_at': datetime(2026, 2, 1, 10, 0, 0)
        }

        next_instance = create_next_recurring_instance(task_data)

        # Check that the new instance has the right properties
        assert next_instance['title'] == 'Test Task'
        assert next_instance['description'] == 'Test Description'
        assert next_instance['completed'] is False  # Should be reset to false
        assert next_instance['user_id'] == 'user123'
        assert next_instance['priority'] == 'medium'
        assert next_instance['tags'] == ['test', 'recurring']
        assert next_instance['due_date'] == datetime(2026, 2, 9, 10, 0, 0)  # Next day due to daily recurrence
        assert next_instance['remind_at'] == datetime(2026, 2, 9, 9, 0, 0)  # Should shift by same amount as due_date
        assert next_instance['recurrence_type'] == 'daily'
        assert next_instance['recurrence_interval'] == 1

        # Check that ID is not present (should be reset for new record)
        assert 'id' not in next_instance

        # Check that timestamps are updated
        assert 'created_at' in next_instance
        assert 'updated_at' in next_instance

    def test_create_next_recurring_instance_no_reminder(self):
        """Test creating next recurring instance without reminder."""
        task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'completed': True,
            'user_id': 'user123',
            'due_date': datetime(2026, 2, 8, 10, 0, 0),
            'recurrence_type': 'weekly',
            'recurrence_interval': 1,
            'created_at': datetime(2026, 2, 1, 10, 0, 0),
            'updated_at': datetime(2026, 2, 1, 10, 0, 0)
        }

        next_instance = create_next_recurring_instance(task_data)

        # Check that due date is updated correctly
        assert next_instance['due_date'] == datetime(2026, 2, 15, 10, 0, 0)  # Next week
        # Check that remind_at is not set if not in original
        assert 'remind_at' not in next_instance or next_instance.get('remind_at') is None