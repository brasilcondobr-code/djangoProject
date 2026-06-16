class ParametersValidator:
    @staticmethod
    def validate_types_condominium(data):
        if 'name' not in data or not data['name']:
            raise ValueError("Name is required")
        
    @staticmethod
    def validate_struction_condominium(data):
        if 'name' not in data or not data['name']:
            raise ValueError("Name is required")

    @staticmethod
    def validate_state(data):
        if 'name' not in data or not data['name']:
            raise ValueError("Name is required")
        if 'abbreviation' not in data or not data['abbreviation']:
            raise ValueError("Abbreviation is required")

    @staticmethod
    def validate_address(data):
        if 'zip_code' not in data or not data['zip_code']:
            raise ValueError("Zip code is required")
        if 'street' not in data or not data['street']:
            raise ValueError("Street is required")
        if 'number' not in data or not data['number']:
            raise ValueError("Number is required")
        if 'city' not in data or not data['city']:
            raise ValueError("City is required")
        if 'state' not in data or not data['state']:
            raise ValueError("State is required")

    @staticmethod
    def validate_types_visitor_restriction(data):
        if 'description' not in data or not data['description']:
            raise ValueError("Description is required")

    @staticmethod
    def validate_resident_type(data):
        if 'description' not in data or not data['description']:
            raise ValueError("Description is required")
