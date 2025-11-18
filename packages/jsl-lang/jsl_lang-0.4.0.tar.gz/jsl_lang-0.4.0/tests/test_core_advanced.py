"""
Advanced tests for JSL Core module.

Focuses on:
- Error handling and edge cases
- Env class methods (deepcopy, equality, content_hash)
- Closure class methods
- HostDispatcher functionality
- Boundary conditions
"""

import pytest
import hashlib
from jsl.core import (
    Env, Closure, Evaluator, HostDispatcher,
    JSLError, SymbolNotFoundError, JSLTypeError
)
from jsl.prelude import make_prelude


class TestEnvClass:
    """Test Env class methods and functionality."""

    def test_env_creation(self):
        """Test basic environment creation."""
        env = Env({"x": 10, "y": 20})
        assert "x" in env
        assert "y" in env
        assert env.get("x") == 10
        assert env.get("y") == 20

    def test_env_parent_chain(self):
        """Test environment parent chain lookups."""
        parent = Env({"x": 10})
        child = Env({"y": 20}, parent=parent)

        assert "x" in child  # Should find in parent
        assert "y" in child  # Should find in self
        assert child.get("x") == 10
        assert child.get("y") == 20

    def test_env_get_missing_symbol(self):
        """Test that getting missing symbol raises error."""
        env = Env({"x": 10})

        with pytest.raises(SymbolNotFoundError, match="Symbol 'z' not found"):
            env.get("z")

    def test_env_contains(self):
        """Test __contains__ method."""
        parent = Env({"x": 10})
        child = Env({"y": 20}, parent=parent)

        assert "x" in child
        assert "y" in child
        assert "z" not in child

    def test_env_extend(self):
        """Test environment extension."""
        base = Env({"x": 10})
        extended = base.extend({"y": 20})

        assert "x" in extended
        assert "y" in extended
        assert extended.get("x") == 10
        assert extended.get("y") == 20

        # Original should be unchanged
        assert "y" not in base

    def test_env_define(self):
        """Test defining new bindings."""
        env = Env({"x": 10})
        env.define("y", 20)

        assert "y" in env
        assert env.get("y") == 20

    def test_env_define_immutable_prelude(self):
        """Test that defining in prelude raises error."""
        prelude = make_prelude()

        with pytest.raises(JSLError, match="Cannot modify prelude"):
            prelude.define("new_var", 42)

    def test_env_to_dict(self):
        """Test environment to dict conversion."""
        parent = Env({"x": 10})
        child = Env({"y": 20}, parent=parent)

        d = child.to_dict()
        assert isinstance(d, dict)
        # Should include both child and parent bindings (except callables)
        assert "y" in d

    def test_env_get_with_chain(self):
        """Test environment get method with parent chain."""
        parent = Env({"x": 10})
        child = Env({"y": 20}, parent=parent)

        assert child.get("x") == 10
        assert child.get("y") == 20

        with pytest.raises(SymbolNotFoundError):
            child.get("z")


class TestEnvEquality:
    """Test Env equality comparisons."""

    def test_env_equality_same_bindings(self):
        """Test equality with same bindings."""
        env1 = Env({"x": 10, "y": 20})
        env2 = Env({"x": 10, "y": 20})

        assert env1 == env2

    def test_env_equality_different_bindings(self):
        """Test inequality with different bindings."""
        env1 = Env({"x": 10})
        env2 = Env({"x": 20})

        assert env1 != env2

    def test_env_equality_with_parent(self):
        """Test equality with parent chains."""
        parent1 = Env({"x": 10})
        parent2 = Env({"x": 10})
        child1 = Env({"y": 20}, parent=parent1)
        child2 = Env({"y": 20}, parent=parent2)

        # Should be equal if flattened bindings are the same
        assert child1 == child2

    def test_env_equality_prelude(self):
        """Test prelude environment equality."""
        prelude1 = make_prelude()
        prelude2 = make_prelude()

        # Preludes should be equal by ID
        assert prelude1 == prelude2

    def test_env_equality_with_closures(self):
        """Test equality with closure bindings."""
        closure1 = Closure(["x"], ["+", "x", 1], Env())
        closure2 = Closure(["x"], ["+", "x", 1], Env())

        env1 = Env({"f": closure1})
        env2 = Env({"f": closure2})

        # Should be equal if closures have same structure
        assert env1 == env2

    def test_env_inequality_wrong_type(self):
        """Test inequality with non-Env objects."""
        env = Env({"x": 10})

        assert env != {"x": 10}  # Dict
        assert env != None
        assert env != 42


class TestEnvDeepcopy:
    """Test Env deepcopy functionality."""

    def test_env_deepcopy_simple(self):
        """Test deepcopy of simple environment."""
        original = Env({"x": 10, "y": 20})
        copy = original.deepcopy()

        assert copy == original
        assert copy is not original
        assert copy.bindings is not original.bindings

    def test_env_deepcopy_with_parent(self):
        """Test deepcopy with parent chain."""
        parent = Env({"x": 10})
        child = Env({"y": 20}, parent=parent)

        copy = child.deepcopy()

        assert copy is not child
        assert copy.bindings is not child.bindings
        # Parent may be deeply copied or None depending on implementation
        if copy.parent is not None:
            assert copy.parent is not child.parent

    def test_env_deepcopy_with_closure(self):
        """Test deepcopy with closure bindings."""
        env = Env({"x": 10})
        closure = Closure(["y"], ["+", "x", "y"], env)
        env_with_closure = Env({"f": closure})

        copy = env_with_closure.deepcopy()

        assert copy is not env_with_closure
        assert "f" in copy
        assert isinstance(copy.get("f"), Closure)

    def test_env_deepcopy_preserves_prelude_id(self):
        """Test that deepcopy preserves prelude metadata."""
        prelude = make_prelude()
        copy = prelude.deepcopy()

        assert copy._is_prelude == prelude._is_prelude
        assert copy._prelude_id == prelude._prelude_id


class TestEnvContentHash:
    """Test Env content hashing."""

    def test_content_hash_deterministic(self):
        """Test that content hash is deterministic."""
        env = Env({"x": 10, "y": 20})

        hash1 = env.content_hash()
        hash2 = env.content_hash()

        assert hash1 == hash2
        assert isinstance(hash1, str)
        assert len(hash1) == 16  # 16 hex characters

    def test_content_hash_different_for_different_envs(self):
        """Test that different environments have different hashes."""
        env1 = Env({"x": 10})
        env2 = Env({"x": 20})

        assert env1.content_hash() != env2.content_hash()

    def test_content_hash_with_parent(self):
        """Test content hash with parent chain."""
        parent = Env({"x": 10})
        child1 = Env({"y": 20}, parent=parent)
        child2 = Env({"y": 20}, parent=parent)

        # Same structure should have same hash
        assert child1.content_hash() == child2.content_hash()

    def test_content_hash_cycle_detection(self):
        """Test that content hash handles cycles."""
        env = Env({"x": 10})
        closure = Closure(["y"], ["+", "x", "y"], env)
        env.define("f", closure)  # Creates cycle: env -> closure -> env

        # Should not infinite loop
        hash_val = env.content_hash()
        assert isinstance(hash_val, str)


class TestClosureClass:
    """Test Closure class methods."""

    def test_closure_creation(self):
        """Test basic closure creation."""
        env = Env({"x": 10})
        closure = Closure(["y"], ["+", "x", "y"], env)

        assert closure.params == ["y"]
        assert closure.body == ["+", "x", "y"]
        assert closure.env is env

    def test_closure_call(self):
        """Test calling a closure."""
        env = make_prelude()
        closure = Closure(["x"], ["*", "x", 2], env)
        evaluator = Evaluator()

        result = closure(evaluator, [5])
        assert result == 10

    def test_closure_call_wrong_arity(self):
        """Test calling closure with wrong number of arguments."""
        env = Env()
        closure = Closure(["x", "y"], ["+", "x", "y"], env)
        evaluator = Evaluator()

        with pytest.raises(JSLTypeError, match="expects 2 arguments, got 1"):
            closure(evaluator, [5])

    def test_closure_deepcopy(self):
        """Test closure deepcopy."""
        env = Env({"x": 10})
        original = Closure(["y"], ["+", "x", "y"], env)

        copy = original.deepcopy()

        assert copy is not original
        assert copy.params == original.params
        assert copy.body == original.body
        assert copy.env is not original.env  # Should be deep copied

    def test_closure_deepcopy_with_new_env(self):
        """Test closure deepcopy with provided environment."""
        old_env = Env({"x": 10})
        new_env = Env({"x": 20})
        original = Closure(["y"], ["+", "x", "y"], old_env)

        copy = original.deepcopy(env=new_env)

        assert copy.env is new_env


class TestHostDispatcher:
    """Test HostDispatcher functionality."""

    def test_host_dispatcher_creation(self):
        """Test creating a host dispatcher."""
        dispatcher = HostDispatcher()
        assert isinstance(dispatcher, HostDispatcher)
        assert hasattr(dispatcher, 'handlers')

    def test_host_dispatcher_register(self):
        """Test registering handlers."""
        dispatcher = HostDispatcher()

        def my_handler(x):
            return x * 2

        dispatcher.register("double", my_handler)
        assert "double" in dispatcher.handlers

    def test_host_dispatcher_dispatch(self):
        """Test dispatching to handlers."""
        dispatcher = HostDispatcher()

        def add_handler(a, b):
            return a + b

        dispatcher.register("add", add_handler)
        result = dispatcher.dispatch("add", [10, 20])
        assert result == 30

    def test_host_dispatcher_missing_handler(self):
        """Test dispatching to missing handler."""
        dispatcher = HostDispatcher()

        with pytest.raises(JSLError, match="Unknown host command"):
            dispatcher.dispatch("nonexistent", [])

    def test_host_dispatcher_handler_error(self):
        """Test handler that raises error."""
        dispatcher = HostDispatcher()

        def error_handler():
            raise ValueError("Test error")

        dispatcher.register("error", error_handler)

        with pytest.raises((JSLError, ValueError)):
            dispatcher.dispatch("error", [])


class TestEvaluatorErrorPaths:
    """Test error handling in evaluator."""

    def test_undefined_variable(self):
        """Test evaluation of undefined variable."""
        evaluator = Evaluator()
        env = make_prelude()

        with pytest.raises(SymbolNotFoundError, match="undefined_var"):
            evaluator.eval("undefined_var", env)

    def test_invalid_function_call_not_callable(self):
        """Test calling non-callable value."""
        evaluator = Evaluator()
        env = make_prelude().extend({"x": 42})

        with pytest.raises((JSLTypeError, JSLError)):
            evaluator.eval(["x", 1, 2], env)

    def test_lambda_missing_params(self):
        """Test lambda with missing parameters."""
        evaluator = Evaluator()
        env = make_prelude()

        # Lambda should have [params, body]
        with pytest.raises(JSLError):
            evaluator.eval(["lambda"], env)

    def test_let_invalid_bindings(self):
        """Test let with invalid bindings."""
        evaluator = Evaluator()
        env = make_prelude()

        # Let bindings should be a list of [name, value] pairs
        with pytest.raises(JSLError, match="binding must be"):
            evaluator.eval(["let", ["x"], ["x"]], env)

    def test_if_missing_branches(self):
        """Test if with missing branches."""
        evaluator = Evaluator()
        env = make_prelude()

        # If should have condition, then, else
        with pytest.raises(JSLError):
            evaluator.eval(["if", True], env)

    def test_def_invalid_arguments(self):
        """Test def with invalid arguments."""
        evaluator = Evaluator()
        env = make_prelude()

        # Def should have name and value
        with pytest.raises(JSLError):
            evaluator.eval(["def", "x"], env)

    def test_quote_missing_argument(self):
        """Test quote with missing argument."""
        evaluator = Evaluator()
        env = make_prelude()

        with pytest.raises(JSLError):
            evaluator.eval(["@"], env)

    def test_try_invalid_structure(self):
        """Test try with invalid structure."""
        evaluator = Evaluator()
        env = make_prelude()

        # Try should have body and handler
        with pytest.raises(JSLError):
            evaluator.eval(["try"], env)

    def test_do_with_one_expression(self):
        """Test do with single expression."""
        evaluator = Evaluator()
        env = make_prelude()

        # Do with one expression should return its value
        result = evaluator.eval(["do", 42], env)
        assert result == 42


class TestEvaluatorEdgeCases:
    """Test edge cases in evaluator."""

    def test_eval_nil(self):
        """Test evaluating None."""
        evaluator = Evaluator()
        env = make_prelude()

        result = evaluator.eval(None, env)
        assert result is None

    def test_eval_bool(self):
        """Test evaluating booleans."""
        evaluator = Evaluator()
        env = make_prelude()

        assert evaluator.eval(True, env) == True
        assert evaluator.eval(False, env) == False

    def test_eval_number(self):
        """Test evaluating numbers."""
        evaluator = Evaluator()
        env = make_prelude()

        assert evaluator.eval(42, env) == 42
        assert evaluator.eval(3.14, env) == 3.14
        assert evaluator.eval(-10, env) == -10

    def test_eval_empty_list(self):
        """Test evaluating empty list."""
        evaluator = Evaluator()
        env = make_prelude()

        result = evaluator.eval([], env)
        assert result == []

    def test_nested_let_shadowing(self):
        """Test nested let with variable shadowing."""
        evaluator = Evaluator()
        env = make_prelude()

        # Inner let shadows outer x
        expr = ["let", [["x", 10]],
                  ["let", [["x", 20]],
                    "x"]]

        result = evaluator.eval(expr, env)
        assert result == 20

    def test_closure_captures_environment(self):
        """Test that closures capture their defining environment."""
        evaluator = Evaluator()
        env = make_prelude()

        # Create closure in environment with x=10
        expr = [
            "let", [["x", 10]],
            ["lambda", ["y"], ["+", "x", "y"]]
        ]

        closure = evaluator.eval(expr, env)
        assert isinstance(closure, Closure)

        # Call closure - should use captured x=10
        result = closure(evaluator, [5])
        assert result == 15

    def test_recursive_closure(self):
        """Test recursive closure."""
        evaluator = Evaluator()
        # Create a mutable environment that allows def
        env = make_prelude().extend({})

        # Factorial function
        expr = [
            "do",
            ["def", "fact",
              ["lambda", ["n"],
                ["if", ["<=", "n", 1],
                  1,
                  ["*", "n", ["fact", ["-", "n", 1]]]]]],
            ["fact", 5]
        ]

        result = evaluator.eval(expr, env)
        assert result == 120  # 5! = 120

    def test_higher_order_function(self):
        """Test higher-order function (function returning function)."""
        evaluator = Evaluator()
        env = make_prelude()

        # Create adder factory: (lambda (x) (lambda (y) (+ x y)))
        expr = [
            "let", [["make_adder",
                      ["lambda", ["x"],
                        ["lambda", ["y"], ["+", "x", "y"]]]]],
            [["make_adder", 10], 5]
        ]

        result = evaluator.eval(expr, env)
        assert result == 15


class TestEvaluatorWithHost:
    """Test evaluator with host operations."""

    def test_host_operation_basic(self):
        """Test that host form is recognized."""
        # Create evaluator with a dispatcher
        dispatcher = HostDispatcher()
        results = []
        dispatcher.register("log", lambda msg: results.append(msg))

        evaluator = Evaluator(host_dispatcher=dispatcher)
        env = make_prelude()

        # Test that host form works
        expr = ["host", "@log", "@Hello"]
        evaluator.eval(expr, env)

        # Result should have been logged
        assert "Hello" in results


class TestResourceManagement:
    """Test resource management in evaluator."""

    def test_resource_budget_creation(self):
        """Test creating a resource budget."""
        from jsl.resources import ResourceBudget, ResourceLimits

        limits = ResourceLimits(max_gas=1000)
        budget = ResourceBudget(limits=limits)

        assert budget is not None
        assert budget.limits == limits

    def test_resource_limits(self):
        """Test resource limits configuration."""
        from jsl.resources import ResourceLimits

        limits = ResourceLimits(max_gas=1000, max_memory=1024, max_time_ms=5000)

        assert limits.max_gas == 1000
        assert limits.max_memory == 1024
        assert limits.max_time_ms == 5000
