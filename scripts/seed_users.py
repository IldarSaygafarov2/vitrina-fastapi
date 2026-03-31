import asyncio

import random

from config.loader import load_config
from infrastructure.database.repo.user import UserRepo
from infrastructure.database.setup import create_engine, create_session_pool
from infrastructure.database.models.user import UserRole


config = load_config(".env")


async def seed_users(session):
    repo = UserRepo(session)

    print("Starting seed: 5 group_directors + 5 agents")

    group_directors = []
    for i in range(1, 6):
        first_name = f"GroupDirector{i}"
        lastname = "Seed"
        phone_number = f"+79990000{100 + i:02d}"
        tg_username = f"group_director_{i}"
        tg_chat_id = random.randint(10**6, 10**10)

        group_director = await repo.create_user(
            first_name=first_name,
            lastname=lastname,
            phone_number=phone_number,
            tg_username=tg_username,
            profile_image="",
            profile_image_hash="",
            role=UserRole.GROUP_DIRECTOR.value,
            added_by=None,
        )
        group_director = await repo.update_user(
            user_id=group_director.id,
            tg_chat_id=tg_chat_id,
        )
        group_directors.append(group_director)
        print(
            f"Created group director: id={group_director.id}, username={group_director.tg_username}"
        )

    for i, group_director in enumerate(group_directors, start=1):
        first_name = f"Agent{i}"
        lastname = "Seed"
        phone_number = f"+79991000{100 + i:02d}"
        tg_username = f"agent_{i}"
        tg_chat_id = random.randint(10**12, 10**18)
        director = await repo.get_user_by_chat_id(group_director.tg_chat_id)

        user = await repo.create_user(
            first_name=first_name,
            lastname=lastname,
            phone_number=phone_number,
            tg_username=tg_username,
            profile_image="",
            profile_image_hash="",
            role=UserRole.REALTOR.value,
            added_by=group_director.tg_chat_id,
        )
        user = await repo.update_user(
            user_id=user.id,
            tg_chat_id=tg_chat_id,
        )
        print(
            f"Created agent: id={user.id}, username={user.tg_username}, added_by_group_director_id={director.id}"
        )

    print("Seeding complete.")


async def main():
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine)

    async with session_pool() as session:
        await seed_users(session)


if __name__ == "__main__":
    asyncio.run(main())
