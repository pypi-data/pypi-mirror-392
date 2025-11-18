from typing import Tuple, Optional
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken
from django.conf import settings


User = get_user_model()

def issue_user_tokens(user_id: str, username: Optional[str] = None) -> Tuple[str, str, int, int]:
    """
    Issue access and refresh tokens using Simple JWT (standard way).
    Returns: access_token, refresh_token, access_expires_in, refresh_expires_in
    """

    user = User.objects.get(id=user_id)


    # Create refresh token linked to the user
    refresh = RefreshToken.for_user(user)

    access = AccessToken()
    access["username"] = user.username
    access["user_id"] = user.id

    # Return values
    return (
        str(access),
        str(refresh),
        int(access.lifetime.total_seconds()),
        int(refresh.lifetime.total_seconds()),
    )
