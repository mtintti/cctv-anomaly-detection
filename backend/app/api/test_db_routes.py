import pytest
from pydantic import ValidationError


class TestClass_db_routes:
    @pytest.mark.asyncio
    async def test_db_routes_correct_user_found_signin(self, testclient):
        response = await testclient.post("/auth/signin", json={'email': 'test_user@g.cm', 'password':'111111'})
        response_json = response.json()
        print("test_db_routes_wrong_user", response_json)
        assert response_json[0] == 30
        assert response_json[2] == 'test_user@g.cm'


    @pytest.mark.asyncio
    async def test_db_routes_wrong_user_found_signin(self, testclient):
        response = await testclient.post("/auth/signin", json={'username':'username','email': 'test_ussser@g.cm', 'password': '11155'})
        response_json = response.json()
        print("")
        print("test_db_routes_wrong_user", response_json)
        assert response_json == None

    @pytest.mark.asyncio
    async def test_db_routes_wrong_user_signup(self, testclient):
        response = await testclient.post("/auth/signup",
                                         json={'username': 'username', 'email': 'test_user@g.cm', 'password': '11111'})
        response_json = response.json()
        print("")
        print("test_db_routes_wrong_user", response_json)
        assert response_json == None

    @pytest.mark.asyncio
    async def test_db_routes_user_length_wrong_signup(self, testclient):
        with pytest.raises(ValidationError) as val_err:
            response = await testclient.post("/auth/signup",
                                       json={'username': 'u', 'email': 'test_user@g.cm', 'password': '11111'})
            response_json = response
            print("")
            print("test_db_routes_user_length_wrong_signup", response_json)
        errors = val_err.value.errors()

        email_error = next(error for error in errors
                           if error["loc"] == ("username",))

        assert email_error["type"] == "string_too_short"
        assert "String should have at least 2 characters" in email_error["msg"]


    @pytest.mark.asyncio
    async def test_db_routes_not_valid_email_signin(self, testclient):
        with pytest.raises(ValidationError) as val_err:
            response = await testclient.post("/auth/signin", json={'email': 'testg.cm', 'password': '11111'})
            response_json = response
            print("test_db_routes_not_email_signin", response_json)
        errors = val_err.value.errors()

        email_error = next(error for error in errors
            if error["loc"] == ("email",))

        assert email_error["type"] == "value_error"
        assert "must have an @-sign" in email_error["msg"]

    @pytest.mark.asyncio
    async def test_db_routes_not_valid_email_signup(self, testclient):
        with pytest.raises(ValidationError) as val_err:
            response = await testclient.post("/auth/signup",
                                       json={'username': 'us', 'email': 'testg.cm', 'password': '11111'})
            response_json = response
            print("")
            print("test_db_routes_not_email_signup", response_json)
        errors = val_err.value.errors()

        email_error = next(error for error in errors
                           if error["loc"] == ("email",))

        assert email_error["type"] == "value_error"
        assert "must have an @-sign" in email_error["msg"]

    @pytest.mark.asyncio
    async def test_db_routes_short_password_signup(self, testclient):
        with pytest.raises(ValidationError) as val_err:
            response = await testclient.post("/auth/signup",
                                             json={'username': 'us', 'email': 'testg.cm', 'password': '111'})
            response_json = response
            print("")
            print("test_db_routes_not_email_signup", response_json)
        errors = val_err.value.errors()

        email_error = next(error for error in errors
                           if error["loc"] == ("password",))

        assert email_error["type"] == "string_too_short"
        assert "String should have at least 5 characters" in email_error["msg"]

    @pytest.mark.asyncio
    async def test_db_routes_short_password_signin(self, testclient):
        with pytest.raises(ValidationError) as val_err:
            response = await testclient.post("/auth/signin",
                                             json={'username': 'us', 'email': 'testg.cm', 'password': '111'})
            response_json = response
            print("")
            print("test_db_routes_not_email_signup", response_json)
        errors = val_err.value.errors()

        email_error = next(error for error in errors
                           if error["loc"] == ("password",))

        assert email_error["type"] == "string_too_short"
        assert "String should have at least 5 characters" in email_error["msg"]
