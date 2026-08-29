from flask import jsonify


def standard_response(data=None, error=None, status_code=200):
    """Utility helper for consistent JSON responses."""
    if error:
        return jsonify({"error": error}), status_code
    return jsonify(data), status_code
