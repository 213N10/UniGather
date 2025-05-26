from typing import List, Optional

from sqlalchemy import Column, DateTime, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key')
    )

    id = mapped_column(Integer)
    name = mapped_column(String(100), nullable=False)
    email = mapped_column(String(100), nullable=False)
    password_hash = mapped_column(String(255), nullable=False)
    role = mapped_column(String(20), server_default=text("'student'::character varying"))
    created_at = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    events: Mapped[List['Events']] = relationship('Events', uselist=True, back_populates='users')
    friends: Mapped[List['Friends']] = relationship('Friends', uselist=True, foreign_keys='[Friends.friend_id]', back_populates='friend')
    friends_: Mapped[List['Friends']] = relationship('Friends', uselist=True, foreign_keys='[Friends.user_id]', back_populates='user')
    attendance: Mapped[List['Attendance']] = relationship('Attendance', uselist=True, back_populates='user')
    comments: Mapped[List['Comments']] = relationship('Comments', uselist=True, back_populates='user')


class Events(Base):
    __tablename__ = 'events'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE', name='events_created_by_fkey'),
        PrimaryKeyConstraint('id', name='events_pkey')
    )

    id = mapped_column(Integer)
    title = mapped_column(String(255), nullable=False)
    datetime = mapped_column(DateTime, nullable=False)
    description = mapped_column(Text)
    location = mapped_column(String(255))
    visibility = mapped_column(String(20), server_default=text("'public'::character varying"))
    created_by = mapped_column(Integer)
    created_at = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    users: Mapped[Optional['Users']] = relationship('Users', back_populates='events')
    attendance: Mapped[List['Attendance']] = relationship('Attendance', uselist=True, back_populates='event')
    comments: Mapped[List['Comments']] = relationship('Comments', uselist=True, back_populates='event')
    media: Mapped[List['Media']] = relationship('Media', uselist=True, back_populates='event')


class Friends(Base):
    __tablename__ = 'friends'
    __table_args__ = (
        ForeignKeyConstraint(['friend_id'], ['users.id'], ondelete='CASCADE', name='friends_friend_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='friends_user_id_fkey'),
        PrimaryKeyConstraint('user_id', 'friend_id', name='friends_pkey')
    )

    user_id = mapped_column(Integer, nullable=False)
    friend_id = mapped_column(Integer, nullable=False)
    status = mapped_column(String(20), server_default=text("'pending'::character varying"))
    created_at = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    friend: Mapped['Users'] = relationship('Users', foreign_keys=[friend_id], back_populates='friends')
    user: Mapped['Users'] = relationship('Users', foreign_keys=[user_id], back_populates='friends_')


class Attendance(Base):
    __tablename__ = 'attendance'
    __table_args__ = (
        ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE', name='attendance_event_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='attendance_user_id_fkey'),
        PrimaryKeyConstraint('user_id', 'event_id', name='attendance_pkey')
    )

    user_id = mapped_column(Integer, nullable=False)
    event_id = mapped_column(Integer, nullable=False)
    status = mapped_column(String(20), server_default=text("'interested'::character varying"))
    timestamp = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    event: Mapped['Events'] = relationship('Events', back_populates='attendance')
    user: Mapped['Users'] = relationship('Users', back_populates='attendance')


class Comments(Base):
    __tablename__ = 'comments'
    __table_args__ = (
        ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE', name='comments_event_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='comments_user_id_fkey'),
        PrimaryKeyConstraint('id', name='comments_pkey')
    )

    id = mapped_column(Integer)
    content = mapped_column(Text, nullable=False)
    event_id = mapped_column(Integer)
    user_id = mapped_column(Integer)
    created_at = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    event: Mapped[Optional['Events']] = relationship('Events', back_populates='comments')
    user: Mapped[Optional['Users']] = relationship('Users', back_populates='comments')


class Media(Base):
    __tablename__ = 'media'
    __table_args__ = (
        ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        PrimaryKeyConstraint('id', name='media_pkey'),
    )

    id = mapped_column(Integer)
    event_id = mapped_column(Integer, nullable=True)
    user_id = mapped_column(Integer, nullable=True)
    url = mapped_column(String(255), nullable=False)
    type = mapped_column(String(20))
    uploaded_at = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    event: Mapped[Optional['Events']] = relationship('Events', back_populates='media')
    user: Mapped[Optional['Users']] = relationship('Users', backref='media_files')



class Likes(Base):
    __tablename__ = 'likes'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        PrimaryKeyConstraint('user_id', 'event_id', name='likes_pkey')
    )

    user_id = mapped_column(Integer, nullable=False)
    event_id = mapped_column(Integer, nullable=False)
    created_at = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped['Users'] = relationship('Users', backref='liked_events')
    event: Mapped['Events'] = relationship('Events', backref='liked_by')
