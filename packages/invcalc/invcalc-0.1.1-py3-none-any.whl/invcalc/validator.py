class ComponentValidator:
    """Validate electronic component specifications"""

    @staticmethod
    def validate_resistance(value, unit='Ω'):
        """Validate resistor values"""
        try:
            value = float(value)
            if value <= 0:
                return False, "Resistance must be positive"
            return True, "Valid resistance"
        except ValueError:
            return False, "Invalid resistance value"

    @staticmethod
    def validate_capacitance(value, unit='F'):
        """Validate capacitor values"""
        try:
            value = float(value)
            if value <= 0:
                return False, "Capacitance must be positive"
            return True, "Valid capacitance"
        except ValueError:
            return False, "Invalid capacitance value"

    @staticmethod
    def validate_voltage_rating(voltage):
        """Validate voltage ratings"""
        try:
            voltage = float(voltage)
            if voltage <= 0:
                return False, "Voltage rating must be positive"
            return True, "Valid voltage rating"
        except ValueError:
            return False, "Invalid voltage rating"
