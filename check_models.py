from models import Session, User, Audience, Reserve

session = Session()

user = User(userId=1, username="reook", firstName="Marie", lastName="Roberts", email="marie123@gmail.com", password=b'', phone=3298743);
user1 = User(userId=2, username="resjdnsook", firstName="Rob", lastName="Martens", email="robbejdks@gmail.com", password=b'', phone=202202020);

audience = Audience(audienceId=1, name="123a");
audience1 = Audience(audienceId=2, name="444b");
audience2 = Audience(audienceId=3, name="555");

reserve = Reserve(reserveId=1, begin="2021-03-04 10:20", end="2021-03-04 11:50", userId=1, audienceId=2)
reserve1 = Reserve(reserveId=2, begin="2021-05-04 10:40", end="2021-05-04 11:40", userId=1, audienceId=3)

session.add(user)
session.add(user1)

session.add(audience)
session.add(audience1)
session.add(audience2)

session.add(reserve)
session.add(reserve1)

# audience7 = Audience(audienceId=7, name="777");
# session.add(audience7)

session.commit()

print(session.query(User).all())
print(session.query(Audience).all())
print(session.query(Reserve).all())

session.close()

# alembic revision --autogenerate -m "First"
# alembic upgrade head