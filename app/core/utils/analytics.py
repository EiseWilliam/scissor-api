from fastapi import Request


def extract_from_request(request: Request) -> tuple[str, str, str]:
    """
    Extracts referer, user agent string, and IP address from the given request.

    Args:
        request (Request): The request object.

    Returns:
        tuple[str | None, str | None, str | None]: A tuple containing the referer, user agent string, and IP address.
    """
    referer = request.headers.get("Referer", "")
    user_agent_string = request.headers.get("User-Agent", "")
    ip_address = request.client.host if request.client else ""
    
    return referer, user_agent_string, ip_address

    