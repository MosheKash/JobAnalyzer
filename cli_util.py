def input_int(prompt, constraint=None, error_msg=None): 
    while True:
        user_input = input(prompt)
        try:
            value = int(user_input)

            if constraint is not None and not constraint(value):
                print(error_msg or "Input does not satisfy the required constraint.")
                continue

            return value

        except ValueError:
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
            return yes_func()
        else:
            return no_func()