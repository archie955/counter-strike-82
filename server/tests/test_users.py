import pytest


@pytest.mark.asyncio
async def test_registration(client, helpers):
    response = await helpers.register_user(client)

    assert response["email"] == "authuser@example.com"
    assert response["username"] == "authusername"


@pytest.mark.asyncio
async def test_duplicate_email_registration(client, helpers):
    user = await helpers.register_user(client)

    user["username"] = "newusername"
    response = await client.post("/users", json=user)

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_duplicate_username_registration(client, helpers):
    user = await helpers.register_user(client)

    user["email"] = "newusername@example.com"
    response = await client.post("/users", json=user)

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_duplicate_password_ok(client, helpers):
    user = await helpers.register_user(client)

    user["email"] = "newusername@example.com"
    user["username"] = "newusername"

    response = await client.post("/users", json=user)

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_missing_username_registration(client):
    user = {"email": "missingdata@example.com", "password": "missingdata"}

    response = await client.post("/users", json=user)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_missing_email_registration(client):
    user = {"username": "missingdatauser", "password": "missingdata"}

    response = await client.post("/users", json=user)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_missing_password_registration(client):
    user = {"email": "missingdata@example.com", "username": "missingdata"}

    response = await client.post("/users", json=user)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_incorrect_email_type(client):
    user = {
        "email": "incorrectgmail.com",
        "username": "incorrect",
        "password": "password",
    }

    response = await client.post("/users", json=user)

    assert response.status_code == 422


# Login endpoint testing


@pytest.mark.asyncio
async def test_login_email(client, helpers):
    user = await helpers.register_user(client)

    response = await client.post(
        "/users/login",
        data={"username": user["email"], "password": user["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == user["email"]
    assert data["user"]["username"] == user["username"]


@pytest.mark.asyncio
async def test_login_username(client, helpers):
    user = await helpers.register_user(client)

    response = await client.post(
        "/users/login",
        data={"username": user["username"], "password": user["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == user["email"]
    assert data["user"]["username"] == user["username"]


@pytest.mark.asyncio
async def test_incorrect_password(client, helpers):
    user = await helpers.register_user(client)

    response = await client.post(
        "/users/login",
        data={"username": user["email"], "password": "incorrectpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_incorrect_email(client, helpers):
    user = await helpers.register_user(client)

    response = await client.post(
        "/users/login",
        data={"username": "notroot", "password": user["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 401


# test update endpoint


@pytest.mark.asyncio
async def test_update_email(client, helpers):
    user = await helpers.full_login(client)

    updated_payload = {
        "updated_user": {
            "email": "newemail@example.com",
            "username": user["username"],
            "password": user["password"],
        },
        "password": user["password"],
    }
    response = await helpers.update_user(client, updated_payload, user)

    assert response["email"] == "newemail@example.com"
    assert response["username"] == user["username"]


@pytest.mark.asyncio
async def test_update_username(client, helpers):
    user = await helpers.full_login(client)
    updated_payload = {
        "updated_user": {
            "email": user["email"],
            "username": "newusername",
            "password": user["password"],
        },
        "password": user["password"],
    }
    response = await helpers.update_user(client, updated_payload, user)

    assert response["email"] == user["email"]
    assert response["username"] == "newusername"


@pytest.mark.asyncio
async def test_update_password(client, helpers):
    user = await helpers.full_login(client)

    updated_payload = {
        "updated_user": {
            "email": user["email"],
            "username": user["username"],
            "password": "newpassword",
        },
        "password": user["password"],
    }

    response = await helpers.update_user(client, updated_payload, user)

    assert response["email"] == user["email"]
    assert response["username"] == user["username"]


@pytest.mark.asyncio
async def test_update_incorrect_password(client, helpers):
    user = await helpers.full_login(client)

    updated_payload = {
        "updated_user": {
            "email": "newemail@example.com",
            "username": user["username"],
            "password": user["password"],
        },
        "password": "incorrect",
    }
    response = await client.put(
        "/users", json=updated_payload, headers=helpers.auth_headers(user)
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_same_info(client, helpers):
    user = await helpers.full_login(client)

    updated_payload = {
        "updated_user": {
            "email": user["email"],
            "username": user["username"],
            "password": user["password"],
        },
        "password": user["password"],
    }
    response = await client.put(
        "/users", json=updated_payload, headers=helpers.auth_headers(user)
    )

    assert response.status_code == 400


# test delete endpoint


@pytest.mark.asyncio
async def test_delete(client, helpers):
    user = await helpers.full_login(client)

    response = await client.delete("/users", headers=helpers.auth_headers(user))

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_not_logged_in(client, helpers):
    await helpers.register_user(client)

    response = await client.delete("/users")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_logged_in_no_headers(client, helpers):
    response = await helpers.full_login(client)

    response = await client.delete("/users")

    assert response.status_code == 401
