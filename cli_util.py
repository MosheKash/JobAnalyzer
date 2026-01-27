def input_int(prompt, constraint=None, error_msg=None, empty_allowed=False): 
    while True:
        user_input = input(prompt)
        try:
            if empty_allowed and user_input.strip() == "":
                return None
            value = int(user_input)

            if constraint is not None and not constraint(value):
                print(error_msg or "Input does not satisfy the required constraint.")
                continue

            return value

        except (ValueError, TypeError):
            print(error_msg or "Invalid input. Please enter a valid integer.")

def input_str(prompt, constraint=None, error_msg=None):
    while True:
        user_input = input(prompt).strip()

        if constraint is not None and not constraint(user_input):
            print(error_msg or "Input does not satisfy the required constraint.")
            continue

        return user_input

def input_choice(prompt, choices: dict, error_msg=None):
    while True:
        print(prompt+"\n")
        for choice in choices:
            print(f"{choice}: {choices[choice]['desc']}")

        user_input = input("\nSelection: ").strip()

        if user_input not in choices.keys():
            print(error_msg or f"Invalid choice. Please choose from: {', '.join(choices)}")
            continue
        
        desired_func = choices[user_input]["func"]
        args = choices[user_input].get("args", [])
        kwargs = choices[user_input].get("kwargs", {})
        print("\n")
        return desired_func(*args, **kwargs)

def input_yes_no(prompt, yes_func, no_func, error_msg=None):
    while True:
        user_input = input(prompt + " (y/n): ").strip().lower()

        if user_input not in {'y', 'n'}:
            print(error_msg or "Invalid input. Please enter 'y' for yes or 'n' for no.")
            continue

        if user_input == 'y':
            return yes_func() if yes_func else True
        else:
            return no_func() if no_func else False

def return_self_dummy(*args, **kwargs):
    return args if args else None

class CommonConstraints:
    @staticmethod
    def non_empty_string(s: str) -> bool:
        return bool(s and s.strip())

    @staticmethod
    def positive_integer(n: int) -> bool:
        return n > 0

    @staticmethod
    def non_negative_integer(n: int) -> bool:
        return n >= 0
    
    @staticmethod
    def within_range(min_value: int, max_value: int):
        def constraint(n: int) -> bool:
            return min_value <= n <= max_value
        return constraint
    
    @staticmethod
    def matches_regex(pattern: str):
        import re
        def constraint(s: str) -> bool:
            return bool(re.match(pattern, s))
        return constraint
    
    @staticmethod
    def is_in_set(valid_set: set):
        def constraint(s: str) -> bool:
            return s in valid_set
        return constraint