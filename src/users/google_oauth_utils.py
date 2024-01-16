from typing import Any, Dict

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from retrying import retry


@retry(stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS, wait_fixed=settings.RETRY_WAIT_FIXED)
def google_get_access_token(*, code: str, redirect_uri: str) -> str:
    """
    Retrieves an access token from Google by exchanging an authorization code.

    Args:
        code (str): The authorization code obtained from the user.
        redirect_uri (str): The redirect URI that was used in the authorization request.

    Returns:
        str: The access token obtained from Google.

    Raises:
        ValidationError: If the request to obtain the access token fails.
    """
    data = {
        'code': code,
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
    }
    response = requests.post(settings.GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data, timeout=settings.REQUEST_TIMEOUT)

    if not response.ok:
        raise ValidationError('Failed to obtain access token from Google.')

    access_token = response.json()['access_token']

    return access_token


@retry(stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS, wait_fixed=settings.RETRY_WAIT_FIXED)
def google_get_user_info(*, access_token: str) -> Dict[str, Any]:
    """
    Calls the Google user info API to obtain the user's information.

    Args:
        access_token (str): The access token used to authenticate the request.

    Returns:
        Dict[str, Any]: A dictionary containing the user's information.

    Raises:
        ValidationError: If the request to the Google API fails.

    """
    url = settings.GOOGLE_USER_INFO_URL
    response = requests.get(url, params={'access_token': access_token}, timeout=settings.REQUEST_TIMEOUT)
    if not response.ok:
        raise ValidationError("Failed to obtain user's info from Google.")

    return response.json()
