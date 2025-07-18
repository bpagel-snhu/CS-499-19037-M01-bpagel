"""
Custom exceptions for the batch_renamer package.
"""

class BatchRenamerError(Exception):
    """Base exception for all batch_renamer errors."""
    pass

class FileOperationError(BatchRenamerError):
    """Raised when a file operation fails."""
    pass

class ValidationError(BatchRenamerError):
    """Raised when input validation fails."""
    pass

class BackupError(BatchRenamerError):
    """Raised when backup operations fail."""
    def __init__(self, message, original_error=None):
        super().__init__(message)
        self.original_error = original_error

class ParseError(BatchRenamerError):
    """Raised when parsing operations fail."""
    def __init__(self, message, filename=None, position=None):
        super().__init__(message)
        self.filename = filename
        self.position = position
        
    def __str__(self):
        details = []
        if self.filename:
            details.append(f"filename: {self.filename}")
        if self.position:
            details.append(f"position: {self.position}")
        if details:
            return f"{super().__str__()} ({', '.join(details)})"
        return super().__str__()

class MonthNormalizeError(BatchRenamerError):
    """Raised when month normalization fails."""
    pass

class PDFOperationError(BatchRenamerError):
    """Raised when PDF operations fail."""
    def __init__(self, message, filename=None, requires_password=False):
        super().__init__(message)
        self.filename = filename
        self.requires_password = requires_password 