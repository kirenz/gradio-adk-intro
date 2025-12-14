from datetime import datetime

def get_current_time() -> dict:
    """
    Retrieves the current system time in 24-hour format.
    
    Use this tool when the user asks for the current time 
    or wants to know what time it is now.
    
    Returns:
        dict: A dictionary containing the current time (e.g., {'current_time': '14:30'})
    """
    # 1. Get current time
    now = datetime.now()
    
    # 2. Format the time 
    # %H = hour (00-23), %M = minute (00-59)
    time_str = now.strftime("%H:%M")
    
    # 3. Return as dictionary
    # The agent receives this structured data to formulate its natural language response
    return {
        "current_time": time_str
    }