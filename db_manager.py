from sqlalchemy import Column, Integer, String, Date, Float, Boolean, ForeignKey, DateTime, create_engine
from sqlalchemy.orm import relationship, declarative_base,sessionmaker
from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:///databases/wellmind.db')  # Use your database URL
Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    gender = Column(String)
    birthday = Column(Date)

    keystroke_data = relationship("KeystrokeData", back_populates="user")
    facial_data = relationship("FacialExpressionData", back_populates="user")
    stress_events = relationship("StressEvent", back_populates="user")
    preferences = relationship("UserPreferenceMapping", back_populates="user")
    keystroke_overall = relationship("KeystrokeOverallData", back_populates="user")
    facial_overall = relationship("FacialExpressionOverall", back_populates="user")


class KeystrokeData(Base):
    __tablename__ = 'keystroke_data'

    keystroke_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    timestamp = Column(DateTime)
    key = Column(String)
    press_time = Column(Float)
    release_time = Column(Float)
    key_hold_time = Column(Float)
    flight_time = Column(Float)
    typing_speed = Column(Float)

    user = relationship("User", back_populates="keystroke_data")


class FacialExpressionData(Base):
    __tablename__ = 'facial_expression_data'

    facial_data_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    timestamp = Column(DateTime)
    # image_path = Column(String)  # Assuming you store the path to the image
    # emotion_label = Column(String)
    stress_percentage = Column(Float)
    user = relationship("User", back_populates="facial_data")


class StressEvent(Base):
    __tablename__ = 'stress_event'

    event_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    facial_expression_id = Column(Integer, ForeignKey('facial_expression_data.facial_data_id'))
    keystroke_id = Column(Integer, ForeignKey('keystroke_data.keystroke_id'))
    timestamp = Column(DateTime)

    user = relationship("User", back_populates="stress_events")
    facial_data = relationship("FacialExpressionData")
    keystroke_data = relationship("KeystrokeData")
    logs = relationship("RecommendationLog", back_populates="event")


class UserPreferenceMapping(Base):
    __tablename__ = 'user_preference_mapping'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    category_id = Column(Integer, ForeignKey('recommendation_categories.category_id'))

    user = relationship("User", back_populates="preferences")
    category = relationship("RecommendationCategory", back_populates="preferences")


class RecommendationCategory(Base):
    __tablename__ = 'recommendation_categories'

    category_id = Column(Integer, primary_key=True)

    recommendations = relationship("Recommendation", back_populates="category")
    preferences = relationship("UserPreferenceMapping", back_populates="category")


class Recommendation(Base):
    __tablename__ = 'recommendation'

    recommendation_id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('recommendation_categories.category_id'))
    message = Column(String)
    score = Column(Float)

    category = relationship("RecommendationCategory", back_populates="recommendations")
    logs = relationship("RecommendationLog", back_populates="recommendation")


class RecommendationLog(Base):
    __tablename__ = 'recommendation_log'

    log_id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('stress_event.event_id'))
    recommendation_id = Column(Integer, ForeignKey('recommendation.recommendation_id'))
    category = Column(String)
    is_react = Column(Boolean)

    event = relationship("StressEvent", back_populates="logs")
    recommendation = relationship("Recommendation", back_populates="logs")


class KeystrokeOverallData(Base):
    __tablename__ = 'keystroke_overall_data'

    facial_overall_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    timestamp = Column(DateTime)
    stress_value = Column(Float)

    user = relationship("User", back_populates="keystroke_overall")


class FacialExpressionOverall(Base):
    __tablename__ = 'facial_expression_overall'

    facial_overall_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    timestamp = Column(DateTime)
    stress_value = Column(Float)

    user = relationship("User", back_populates="facial_overall")


Base.metadata.create_all(engine)


def get_session():
    """Get a new session for database operations."""
    return Session()

def close_session(session):
    """Close the provided session."""
    session.close()


def create_user(first_name, last_name,gender,birthday):
    """Create a new user in the database."""
    session = get_session()
    user = User(
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        birthday=datetime.strptime(birthday, "%Y-%m-%d").date()
    )
    session.add(user)
    session.commit()
    close_session(session)


def get_user_by_id(user_id):
    """Retrieve a user by their ID."""
    session = get_session()
    user = session.query(User).filter(User.user_id == user_id).first()
    close_session(session)
    return user


def store_facial_expression_data(user_id,stress_percentage):
    """Store facial expression data in the database."""
    session = get_session()
    facial_data = FacialExpressionData(
        user_id=user_id,
        timestamp=datetime.now(),
        # image_path=image_path,
        # emotion_label=emotion_label,
        stress_percentage=stress_percentage 
    )
    session.add(facial_data)
    session.commit()
    close_session(session)


