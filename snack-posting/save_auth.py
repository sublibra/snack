def on_response(response, posting) -> None:
    """
    Parses the JSON response body from a successful login,
    extracts the access_token, and saves it as a variable.
    """
    try:
        # 1. Parse the JSON body of the response into a Python dictionary.
        data = response.json()

        # 2. Get the value of the 'access_token' key.
        access_token = data["access_token"]

        # 3. Set the variable in `posting` for other requests to use.
        posting.set_variable("access_token", access_token)
        
        print(f"✅ Successfully captured and set access_token.")

    except Exception as e:
        # This will run if login fails or the response isn't as expected.
        print(f"❌ Error capturing access_token: {e}")
