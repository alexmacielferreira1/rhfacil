from app.core.security import signed_token


def test_signed_token_is_reproducible_scoped_and_does_not_expose_secret() -> None:
    secret = 'a-production-secret-with-at-least-32-characters'
    token = signed_token(purpose='invitation', subject='tenant.invitation', secret=secret)

    assert token == signed_token(
        purpose='invitation', subject='tenant.invitation', secret=secret
    )
    other = signed_token(
        purpose='password-reset', subject='tenant.invitation', secret=secret
    )
    assert token != other
    assert secret not in token
    assert token.startswith('tenant.invitation.')
