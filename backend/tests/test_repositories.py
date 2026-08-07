from app.repositories.users import UserRepository

def test_user_repository_create(db_session):
    repo = UserRepository(db_session)
    user = repo.create("new@example.com", "hashed_pw", is_admin=False)
    
    assert user.id is not None
    assert user.email == "new@example.com"
    assert user.password_hash == "hashed_pw"
    assert user.is_admin is False

def test_user_repository_get_by_id(db_session, test_user):
    repo = UserRepository(db_session)
    fetched = repo.get_by_id(test_user.id)
    assert fetched is not None
    assert fetched.id == test_user.id
    assert fetched.email == test_user.email

    not_found = repo.get_by_id(999)
    assert not_found is None

def test_user_repository_get_by_email(db_session, test_user):
    repo = UserRepository(db_session)
    fetched = repo.get_by_email(test_user.email)
    assert fetched is not None
    assert fetched.id == test_user.id
    assert fetched.email == test_user.email

    not_found = repo.get_by_email("nonexistent@example.com")
    assert not_found is None
