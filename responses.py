def handle_response(message) -> str:
    message = message.lower()
    if message == "generate":
        return "working"
    