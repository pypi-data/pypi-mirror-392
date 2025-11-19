from baltra_sdk.infra.aws.cognito_user_repository import CognitoUserRepository
from baltra_sdk.application.users.get_users_service import GetUsersService

def make_get_users_service() -> GetUsersService:
    repo = CognitoUserRepository()
    return GetUsersService(repo)
