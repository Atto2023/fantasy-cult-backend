from sqlalchemy.future import select
from src.db.database import db
from sqlalchemy import (
    update, 
    delete
)

from src.db.models import (
    Notification, 
    UserDevice,
)
from sqlalchemy import func
import logging

class NotificationSchema():

    @classmethod
    async def get_notification(cls, user_id,limit,offset):
        notification = select(
            Notification.message,
            Notification.read,
            Notification.created_at
        ).where(
            Notification.user_id == user_id
        ).order_by(
            Notification.created_at.desc()
        ).limit(limit).offset(offset-1)

        notification = await db.execute(notification)
        return notification.all()

    @classmethod
    async def read_notification(cls, user_id):
        data = update(
            Notification
        ).where(
            Notification.user_id == user_id
        ).values(
            {"read": True}
        ).execution_options(
            synchronize_session="fetch"
        )
        await db.execute(data)
        try:
            await db.commit()
            logging.info(msg=f"Notification read successfully for user ID: {user_id}",
                         extra={"custom_args": "READ_NOTIFICATION_OPERATION",
                                "user_id": user_id})
        except Exception as e:
            await db.rollback()
            logging.error(msg=f"Failed to read notification for user ID: {user_id}. Error: {e}",
                          extra={"custom_args": "READ_NOTIFICATION_OPERATION", 
                                 "user_id": user_id})
        return True

    @classmethod
    async def get_user_notification_count(cls, user_id):
        notification = select(
            func.count(Notification.notification_id)
        ).where(
            Notification.user_id == user_id,
            Notification.read == False
        )
        notification = await db.execute(notification)
        return notification.scalar()

    @classmethod
    async def get_device_token_of_user(cls, user_id):
        user_device = select(
            UserDevice.device_token
        ).where(
            UserDevice.user_id == user_id
        )

        user_device = await db.execute(user_device)
        return user_device.all()

    @classmethod
    async def add_update_device_token(cls, user_id, device_token):
        # check used_id in user device
        # if user_id -> then update device_token
        # else add device_token
        user_device = select(
            UserDevice.device_id,
            UserDevice.user_id,
            UserDevice.device_token
        ).where(
            UserDevice.user_id == user_id
        )

        user_device = await db.execute(user_device)
        user_device = user_device.one_or_none()
        if user_device:
            data = update(
                UserDevice
            ).where(
                UserDevice.user_id == user_id
            ).values(
                {"device_token": device_token}
            ).execution_options(
                synchronize_session="fetch"
            )
            await db.execute(data)
            try:
                await db.commit()
                logging.info(msg=f"Device token for user {user_id} updated successfully",
                         extra={"custom_args": "ADD_UPDATE_DEVICE_TOKEN_OPERATION", 
                                "user_id": user_id})
            except Exception as e:
                await db.rollback()
                logging.error(msg=f"Failed to update device token for user {user_id}. Error: {e}",
                          extra={"custom_args": "ADD_UPDATE_DEVICE_TOKEN_OPERATION",
                                 "user_id": user_id})
            return True
        else:
            user_device = UserDevice(
                user_id = user_id,
                device_token = device_token
            )
            db.add(user_device)
            try:
                await db.commit()
                logging.info(msg=f"Device token for user {user_id} added successfully",
                         extra={"custom_args": "ADD_UPDATE_DEVICE_TOKEN_OPERATION", 
                                "user_id": user_id})
            except Exception as e:
                await db.rollback()
                logging.error(msg=f"Failed to add device token for user {user_id}. Error: {e}",
                          extra={"custom_args": "ADD_UPDATE_DEVICE_TOKEN_OPERATION",
                                 "user_id": user_id})
            return True

    @classmethod
    async def add_notification(cls, user_id, message):
        notification = Notification(
            user_id = user_id,
            message = message,
            read = False
        )
        db.add(notification)
        try:
            await db.commit()
            logging.info(msg=f"Notification added successfully for user ID: {user_id}",
                         extra={"custom_args": "ADD_NOTIFICATION_OPERATION", 
                                "user_id": user_id})
        except Exception as e:
            await db.rollback()
            logging.error(msg=f"Failed to add notification for user ID: {user_id}. Error: {e}",
                          extra={"custom_args": "ADD_NOTIFICATION_OPERATION", 
                                 "user_id": user_id})
        return notification

    @classmethod
    async def update_notification(cls, notification_id):
        data = update(
            Notification
        ).where(
            Notification.notification_id == notification_id
        ).values(
            {"is_pushed": True}
        ).execution_options(
            synchronize_session="fetch"
        )
        await db.execute(data)
        try:
            await db.commit()
            logging.info(msg=f"Notification with ID {notification_id} updated successfully",
                         extra={"custom_args": "UPDATE_NOTIFICATION_OPERATION", 
                                "notification_id": notification_id})
        except Exception as e:
            await db.rollback()
            logging.error(msg=f"Failed to update notification with ID {notification_id}. Error: {e}",
                          extra={"custom_args": "UPDATE_NOTIFICATION_OPERATION", 
                                 "notification_id": notification_id})
