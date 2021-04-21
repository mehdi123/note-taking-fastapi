from . import database
from app.models.user import users, verifications
from app.schemas.user import User
from app.utils.hash import create_hash

class UserTableHandler:
    '''
        Users sqlalchemy table handler
    '''
    
    @staticmethod
    async def find_by_email(email: str):
        query = users.select().where(users.c.email == email)
        user = await database.fetch_one(query)
        return user
    
    @staticmethod
    async def find_by_id(user_id: int):
        query = users.select().where(users.c.id == user_id)
        user = await database.fetch_one(query)
        return user

    @staticmethod
    async def add(user: User):
        query = users.insert().values(fullname=user.fullname,
                                        email=user.email,
                                        password=create_hash(user.password),
                                        is_superuser=False,
                                        is_verified=False)
        user_id = await database.execute(query)
        verification_code = create_hash(f"{user.fullname}:{user.email}")
        query = verifications.insert().values(user_id=user_id, 
            code=verification_code
        )
        await database.execute(query)
        return user_id, verification_code
    
    @staticmethod
    async def verify_user(user_id, is_verified=True):
        query = users.update().values(is_verified=is_verified).where(users.c.id == user_id)
        result = await database.execute(query)
        query = verifications.delete().where(verifications.c.user_id == user_id)
        result = await database.execute(query)             

    @staticmethod
    async def update_password(user_id, new_password):
        query = users.update().values(password=create_hash(new_password)).where(users.c.id == user_id)
        await database.execute(query)