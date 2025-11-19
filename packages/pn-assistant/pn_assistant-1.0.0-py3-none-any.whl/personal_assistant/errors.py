class ValidationError(Exception):
    """Custom exception for validation errors in fields."""
    
    def __init__(self, message):
        self.message = f'\n{"-"*10} {message} {"-"*10}'
        super().__init__(self.message)
