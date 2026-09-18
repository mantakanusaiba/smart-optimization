class GridWiseError(Exception):
    status_code = 500
    public_message = "Optimization service could not complete the request."


class DirectiveValidationError(GridWiseError):
    status_code = 422
    public_message = "An operator directive could not be safely interpreted."


class InterpretationError(GridWiseError):
    status_code = 500
    public_message = "Operator notes could not be interpreted."


class OptimizationError(GridWiseError):
    status_code = 500
    public_message = "A valid energy schedule could not be produced."


class ReplayValidationError(GridWiseError):
    status_code = 500
    public_message = "The optimized schedule failed independent validation."
