def create_personalized_greeting(state: dict) -> str:
    name = state.get('name')
    age = state.get('age')
    weight = state.get('weight')
    height = state.get('height')
    phone_number = state.get('phone_number')
    return f"""
    Name: {name}
    Age: {age}
    Weight: {weight}
    Height: {height}
    Phone Number: {phone_number}
    """
