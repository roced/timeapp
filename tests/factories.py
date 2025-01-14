from factory import Factory, Faker, SubFactory
from app.models import Event, User, Memo, EventLike, EventAttendance, EventWishlist
from datetime import datetime, timedelta

class UserFactory(Factory):
    class Meta:
        model = User
    
    username = Faker('user_name')
    email = Faker('email')
    role = 'viewer'
    is_admin = False
    created_at = Faker('date_time')
    updated_at = Faker('date_time')

class EventFactory(Factory):
    class Meta:
        model = Event
    
    title = Faker('sentence')
    description = Faker('paragraph')
    start_date = Faker('future_date')
    end_date = Faker('future_date')
    location = Faker('city')
    venue = Faker('company')
    is_public = True
    is_recurring = False
    info_link = Faker('url')
    tags = 'test;event'
    owner_id = SubFactory(UserFactory)
    created_at = Faker('date_time')
    updated_at = Faker('date_time')
    like_count = 0
    attendance_count = 0
    pending_promotion = False

class EventLikeFactory(Factory):
    class Meta:
        model = EventLike
    
    user = SubFactory(UserFactory)
    event = SubFactory(EventFactory)
    created_at = Faker('date_time')

class EventAttendanceFactory(Factory):
    class Meta:
        model = EventAttendance
    
    user = SubFactory(UserFactory)
    event = SubFactory(EventFactory)
    created_at = Faker('date_time')

class EventWishlistFactory(Factory):
    class Meta:
        model = EventWishlist
    
    user = SubFactory(UserFactory)
    event = SubFactory(EventFactory)
    created_at = Faker('date_time')

class MemoFactory(Factory):
    class Meta:
        model = Memo
    
    title = Faker('sentence')
    content = Faker('paragraph')
    due_date = Faker('future_date')
    priority = 'medium'
    status = 'pending'
    user_id = SubFactory(UserFactory)
    created_at = Faker('date_time')
    updated_at = Faker('date_time') 