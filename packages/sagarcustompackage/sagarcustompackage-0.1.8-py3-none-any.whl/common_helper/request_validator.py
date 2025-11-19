from functools import wraps
from flask import request, jsonify


def validate_request(schema=None, strict=False):
    """
    A decorator to validate incoming Flask request data.

    Features:
    ✔ Required fields
    ✔ Type checking
    ✔ Custom validation functions
    ✔ Strict mode (disallow extra keys)
    ✔ JSON + Form support
    ✔ Auto error response (422)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            # Extract request data
            if request.is_json:
                data = request.get_json(silent=True) or {}
            else:
                data = request.form.to_dict() or {}

            errors = {}

            # Apply schema validation
            if schema:
                for field, rules in schema.items():

                    # Required field check
                    if rules.get("required") and field not in data:
                        errors[field] = "Missing required field"
                        continue

                    if field not in data:
                        continue

                    val = data[field]

                    # Type validation
                    expected = rules.get("type")
                    if expected and not isinstance(val, expected):
                        try:
                            data[field] = expected(val)
                        except Exception:
                            errors[field] = f"Expected type {expected.__name__}"
                            continue

                    # Custom validator
                    custom = rules.get("custom")
                    if custom:
                        try:
                            if not custom(data[field]):
                                errors[field] = "Custom validation failed"
                        except Exception:
                            errors[field] = "Invalid custom validation function"

            # Strict mode: Disallow extra fields
            if strict and schema:
                extra = set(data.keys()) - set(schema.keys())
                if extra:
                    errors["extra_fields"] = list(extra)

            # Return standardized error
            if errors:
                return jsonify({
                    "status": "failed",
                    "error": "Invalid request data. Please review and try again.",
                    "details": errors,
                    "code": 422
                }), 422

            # Successful validation
            return func(data=data, *args, **kwargs)

        return wrapper

    return decorator
