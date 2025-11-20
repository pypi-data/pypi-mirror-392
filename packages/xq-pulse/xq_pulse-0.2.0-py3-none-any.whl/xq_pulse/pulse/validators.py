from __future__ import annotations

import pint

from xq_pulse.pulse.expression import (
    AnyExpression,
    Expression,
    Parameterized,
    eval_expression,
    is_bound,
)
from xq_pulse.util import Quantity, Unit


class ExpressionOrQuantityValidator:
    """
    A validator for attrs that validates both Expression and Quantity values.

    This validator:
    - Checks unit compatibility for both Expression and Quantity values
    - Validates min/max constraints for Quantity values (or bound Expressions)
    - Allows unbound Expressions (validation happens later when bound)
    - Provides clear error messages with class name, field name, and formatted values
    """

    def __init__(
        self,
        expected_unit: Unit,
        *,
        min_value: Quantity | None = None,
        max_value: Quantity | None = None,
        min_inclusive: bool = True,  # True for ge, False for gt
        max_inclusive: bool = True,  # True for le, False for lt
    ):
        self.expected_unit = expected_unit
        self.min_value = min_value
        self.max_value = max_value
        self.min_inclusive = min_inclusive
        self.max_inclusive = max_inclusive

    def __call__(self, instance, attribute, value):
        # Get context for error messages
        class_name = instance.__class__.__name__
        field_name = attribute.name

        # Handle Expression (bound or unbound)
        if isinstance(value, (AnyExpression, Parameterized)):
            # Check unit compatibility
            if not value.units.is_compatible_with(self.expected_unit):
                raise ValueError(
                    f"{class_name}.{field_name}: Unit mismatch - expected {self.expected_unit}, but got {value.units}"
                )

            # If bound, evaluate and validate as Quantity
            if is_bound(value):
                value = eval_expression(value)
            else:
                # Unbound expression - allow it, validation happens later
                return

        # Handle Quantity (Literal)
        if isinstance(value, pint.Quantity):
            # Check unit compatibility
            if not value.is_compatible_with(self.expected_unit):
                raise ValueError(
                    f"{class_name}.{field_name}: Unit mismatch - expected {self.expected_unit}, but got {value.units}"
                )

            # Check min constraint
            if self.min_value is not None:
                if self.min_inclusive:
                    if value < self.min_value:
                        raise ValueError(
                            f"{class_name}.{field_name}: Value too small - "
                            f"must be >= {self.min_value:~#g}, "
                            f"but got {value:~#g}"
                        )
                else:
                    if value <= self.min_value:
                        raise ValueError(
                            f"{class_name}.{field_name}: Value too small - "
                            f"must be > {self.min_value:~#g}, "
                            f"but got {value:~#g}"
                        )

            # Check max constraint
            if self.max_value is not None:
                if self.max_inclusive:
                    if value > self.max_value:
                        raise ValueError(
                            f"{class_name}.{field_name}: Value too large - "
                            f"must be <= {self.max_value:~#g}, "
                            f"but got {value:~#g}"
                        )
                else:
                    if value >= self.max_value:
                        raise ValueError(
                            f"{class_name}.{field_name}: Value too large - "
                            f"must be < {self.max_value:~#g}, "
                            f"but got {value:~#g}"
                        )

            # Validation passed
            return

        # If we get here and it's not a Quantity or Expression, that's an error
        if not isinstance(value, (pint.Quantity, Expression, Parameterized)):
            raise ValueError(
                f"{class_name}.{field_name}: Expected Expression or Quantity, but got {type(value).__name__}: {value}"
            )
