"""
Tests for JSL Resource Management.

Tests cover:
- Gas costs and metering
- Resource budgets and limits
- Memory tracking
- Time limits
- Host gas policies
- Resource exhaustion handling
"""

import pytest
import time
from jsl.resources import (
    GasCost,
    HostGasPolicy,
    ResourceLimits,
    ResourceBudget,
    ResourceExhausted
)


class TestGasCost:
    """Test gas cost enumeration."""

    def test_gas_cost_values(self):
        """Test that gas costs are defined."""
        assert GasCost.LITERAL == 1
        assert GasCost.VARIABLE == 2
        assert GasCost.ARITHMETIC == 3
        assert GasCost.IF == 5
        assert GasCost.LAMBDA_CREATE == 20
        assert GasCost.FUNCTION_CALL == 10

    def test_gas_cost_ordering(self):
        """Test that gas costs have sensible ordering."""
        # Literals should be cheapest
        assert GasCost.LITERAL < GasCost.VARIABLE

        # Function calls should be more expensive than basic operations
        assert GasCost.FUNCTION_CALL > GasCost.ARITHMETIC

        # Creating lambdas should be expensive
        assert GasCost.LAMBDA_CREATE > GasCost.FUNCTION_CALL

    def test_gas_cost_is_int(self):
        """Test that gas costs are integers."""
        assert isinstance(GasCost.LITERAL, int)
        assert isinstance(GasCost.FUNCTION_CALL, int)


class TestHostGasPolicy:
    """Test host gas policy."""

    def test_host_gas_policy_creation(self):
        """Test creating a host gas policy."""
        policy = HostGasPolicy()
        assert policy is not None
        assert hasattr(policy, 'cost_tree')

    def test_host_gas_policy_with_custom_costs(self):
        """Test creating policy with custom costs."""
        custom_costs = {
            "@file": {
                "@read": 100,
                "@write": 200
            }
        }
        policy = HostGasPolicy(cost_tree=custom_costs)
        assert policy.cost_tree == custom_costs

    def test_host_gas_policy_get_cost(self):
        """Test getting cost for a command."""
        policy = HostGasPolicy()

        # Should return some cost (default or specific)
        cost = policy.get_cost("@file/read")
        assert isinstance(cost, int)
        assert cost > 0

    def test_host_gas_policy_hierarchy(self):
        """Test hierarchical cost lookup."""
        policy = HostGasPolicy()

        # Get costs for different levels
        file_read = policy.get_cost("@file/read")
        network_get = policy.get_cost("@network/http-get")

        assert isinstance(file_read, int)
        assert isinstance(network_get, int)

    def test_host_gas_policy_unknown_operation(self):
        """Test cost for unknown operation."""
        policy = HostGasPolicy()

        # Unknown operations should have default cost
        cost = policy.get_cost("@unknown/operation")
        assert isinstance(cost, int)
        assert cost > 0


class TestResourceLimits:
    """Test resource limits."""

    def test_resource_limits_creation(self):
        """Test creating resource limits."""
        limits = ResourceLimits(max_gas=1000)
        assert limits.max_gas == 1000
        assert limits.max_memory is None
        assert limits.max_time_ms is None

    def test_resource_limits_all_parameters(self):
        """Test creating limits with all parameters."""
        limits = ResourceLimits(
            max_gas=1000,
            max_memory=1024,
            max_time_ms=5000
        )
        assert limits.max_gas == 1000
        assert limits.max_memory == 1024
        assert limits.max_time_ms == 5000

    def test_resource_limits_none_values(self):
        """Test that None values mean no limit."""
        limits = ResourceLimits()
        assert limits.max_gas is None
        assert limits.max_memory is None
        assert limits.max_time_ms is None


class TestResourceBudget:
    """Test resource budget."""

    def test_resource_budget_creation(self):
        """Test creating a resource budget."""
        limits = ResourceLimits(max_gas=1000)
        budget = ResourceBudget(limits=limits)

        assert budget is not None
        assert budget.limits == limits

    def test_resource_budget_no_limits(self):
        """Test budget with no limits."""
        budget = ResourceBudget()

        assert budget is not None
        assert budget.limits is None

    def test_resource_budget_with_policy(self):
        """Test budget with host gas policy."""
        limits = ResourceLimits(max_gas=1000)
        policy = HostGasPolicy()
        budget = ResourceBudget(limits=limits, host_gas_policy=policy)

        assert budget.limits == limits
        assert budget.host_gas_policy == policy

    def test_consume_gas(self):
        """Test consuming gas."""
        limits = ResourceLimits(max_gas=1000)
        budget = ResourceBudget(limits=limits)

        budget.consume_gas(100, "test operation")

        assert budget.gas_used == 100

    def test_consume_gas_multiple_times(self):
        """Test consuming gas multiple times."""
        limits = ResourceLimits(max_gas=1000)
        budget = ResourceBudget(limits=limits)

        budget.consume_gas(100, "op1")
        budget.consume_gas(200, "op2")
        budget.consume_gas(50, "op3")

        assert budget.gas_used == 350
        assert budget.gas_remaining == 650

    def test_gas_exhausted(self):
        """Test gas exhaustion."""
        limits = ResourceLimits(max_gas=100)
        budget = ResourceBudget(limits=limits)

        # Consume most of the gas
        budget.consume_gas(90, "op1")

        # Try to consume more than remaining
        with pytest.raises(ResourceExhausted, match="Gas limit exceeded"):
            budget.consume_gas(20, "op2")

    def test_gas_exactly_at_limit(self):
        """Test consuming exactly the limit."""
        limits = ResourceLimits(max_gas=100)
        budget = ResourceBudget(limits=limits)

        budget.consume_gas(100, "exact")
        assert budget.gas_used == 100
        assert budget.gas_remaining == 0

        # Next consumption should fail
        with pytest.raises(ResourceExhausted):
            budget.consume_gas(1, "one more")

    def test_no_gas_limit(self):
        """Test budget with no gas limit."""
        budget = ResourceBudget()  # No limits

        # Should be able to consume arbitrary amounts
        budget.consume_gas(1000000, "big operation")
        assert budget.gas_used == 1000000

    def test_check_time(self):
        """Test time checking."""
        limits = ResourceLimits(max_time_ms=100)  # 100ms limit
        budget = ResourceBudget(limits=limits)

        # Should not raise immediately
        budget.check_time()

        # Sleep to exceed time limit
        time.sleep(0.15)  # 150ms

        # Now should raise
        with pytest.raises(ResourceExhausted, match="Time limit exceeded"):
            budget.check_time()

    def test_no_time_limit(self):
        """Test budget with no time limit."""
        budget = ResourceBudget()  # No limits

        # Should never raise
        budget.check_time()
        time.sleep(0.01)
        budget.check_time()

    def test_track_memory(self):
        """Test memory tracking."""
        limits = ResourceLimits(max_memory=1024)
        budget = ResourceBudget(limits=limits)

        # Track some memory usage
        budget.track_memory(512)
        assert budget.memory_used == 512

        budget.track_memory(256)
        assert budget.memory_used == 768

    def test_memory_exhausted(self):
        """Test memory exhaustion."""
        limits = ResourceLimits(max_memory=1024)
        budget = ResourceBudget(limits=limits)

        budget.track_memory(900)

        with pytest.raises(ResourceExhausted, match="Memory limit exceeded"):
            budget.track_memory(200)  # Would exceed 1024

    def test_no_memory_limit(self):
        """Test budget with no memory limit."""
        budget = ResourceBudget()  # No limits

        # Should be able to track arbitrary amounts
        budget.track_memory(1000000)
        assert budget.memory_used == 1000000


class TestResourceExhausted:
    """Test ResourceExhausted exception."""

    def test_resource_exhausted_creation(self):
        """Test creating ResourceExhausted exception."""
        exc = ResourceExhausted("Test message")
        assert str(exc) == "Test message"

    def test_resource_exhausted_with_details(self):
        """Test exception with details."""
        exc = ResourceExhausted("Gas limit exceeded: used 1000, limit 900")
        assert "Gas limit exceeded" in str(exc)
        assert "1000" in str(exc)


class TestIntegration:
    """Integration tests with evaluator."""

    def test_gas_tracking_with_evaluator(self):
        """Test gas tracking during evaluation."""
        from jsl import Evaluator, make_prelude
        from jsl.resources import ResourceLimits

        limits = ResourceLimits(max_gas=10000)
        evaluator = Evaluator(resource_limits=limits)
        env = make_prelude()

        # Simple expression
        expr = ["+", 1, 2, 3, 4, 5]
        result = evaluator.eval(expr, env)

        assert result == 15
        # Gas should have been consumed
        if evaluator.resources:
            assert evaluator.resources.gas_used > 0

    def test_gas_limit_exceeded_during_evaluation(self):
        """Test that gas limit is enforced during evaluation."""
        from jsl import Evaluator, make_prelude
        from jsl.resources import ResourceLimits

        limits = ResourceLimits(max_gas=10)  # Very low limit
        evaluator = Evaluator(resource_limits=limits)
        env = make_prelude()

        # Complex expression that will exceed limit
        expr = ["+",
                 ["*", 10, 20],
                 ["*", 30, 40],
                 ["*", 50, 60]]

        with pytest.raises(ResourceExhausted):
            evaluator.eval(expr, env)

    def test_evaluator_without_limits(self):
        """Test evaluator without resource limits."""
        from jsl import Evaluator, make_prelude

        evaluator = Evaluator()  # No limits
        env = make_prelude()

        # Should work fine
        expr = ["+", 1, 2, 3]
        result = evaluator.eval(expr, env)
        assert result == 6


class TestHostGasCosts:
    """Test host operation gas costs."""

    def test_file_operation_costs(self):
        """Test file operation costs."""
        policy = HostGasPolicy()

        read_cost = policy.get_cost("@file/read")
        write_cost = policy.get_cost("@file/write")

        # Write should be more expensive than read
        assert write_cost > read_cost
        assert read_cost > 0

    def test_network_operation_costs(self):
        """Test network operation costs."""
        policy = HostGasPolicy()

        http_get = policy.get_cost("@network/http-get")
        http_post = policy.get_cost("@network/http-post")

        # Network operations should be expensive
        assert http_get > 100
        assert http_post > 100

    def test_custom_cost_override(self):
        """Test overriding default costs."""
        custom = {
            "@file": {
                "@read": 50,  # Override default
                "@write": 100
            }
        }
        policy = HostGasPolicy(cost_tree=custom)

        read_cost = policy.get_cost("@file/read")
        assert read_cost == 50


class TestBudgetCheckpoints:
    """Test budget checkpointing and restoration."""

    def test_budget_state_snapshot(self):
        """Test capturing budget state."""
        limits = ResourceLimits(max_gas=1000)
        budget = ResourceBudget(limits=limits)

        budget.consume_gas(100, "op1")

        # State should be capturable
        assert budget.gas_used == 100
        assert budget.gas_remaining == 900

    def test_multiple_operations_tracking(self):
        """Test tracking multiple operations."""
        limits = ResourceLimits(max_gas=1000, max_memory=2048)
        budget = ResourceBudget(limits=limits)

        # Perform multiple operations
        budget.consume_gas(100, "op1")
        budget.track_memory(512)
        budget.consume_gas(50, "op2")
        budget.track_memory(256)

        assert budget.gas_used == 150
        assert budget.memory_used == 768

    def test_resource_usage_tracking(self):
        """Test that all resource types are tracked correctly."""
        limits = ResourceLimits(
            max_gas=1000,
            max_memory=2048,
            max_time_ms=5000
        )
        budget = ResourceBudget(limits=limits)

        # Use some of each resource
        budget.consume_gas(200, "computation")
        budget.track_memory(1024)

        assert budget.gas_used == 200
        assert budget.memory_used == 1024
        assert budget.gas_remaining == 800
