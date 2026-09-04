from app.core.security import hash_password, hash_token, new_token, verify_password


def test_password_uses_slow_hash_and_verifies() -> None:
    encoded = hash_password('correct horse battery staple')
    assert encoded.startswith('$argon2')
    assert verify_password('correct horse battery staple', encoded)
    assert not verify_password('wrong password', encoded)


def test_session_tokens_are_random_and_only_digest_is_persisted() -> None:
    first = new_token()
    second = new_token()
    assert first != second
    assert len(first) >= 43
    assert hash_token(first) == hash_token(first)
    assert hash_token(first) != hash_token(second)
    assert first not in hash_token(first)
