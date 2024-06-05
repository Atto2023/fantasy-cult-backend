from fastapi import status
import logging
from src.services.notification.schema import NotificationSchema
from src.services.notification.serializer import ResponseNotificationSerializer
from src.utils.jwt import auth_check
from src.utils.response import (
    SuccessResponseSerializer, 
    response_structure
)

class NotificationController:

    @classmethod
    async def get_notification(cls, token, authorize,limit,offset):
        await auth_check(authorize=authorize, token=token)
        user_id = authorize.get_jwt_subject()

        notification = await NotificationSchema.get_notification(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        notification = [ResponseNotificationSerializer(**(i._asdict())) for i in notification]
        serializer = SuccessResponseSerializer(
            message="Notification List",
            data=notification
        )
        logging.info(
                    msg="Notification List",
                    extra={"custom_args": "GET-notification",
                    "user_id":user_id
                    }
        )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )

    @classmethod
    async def read_notification(cls, token, authorize):
        await auth_check(authorize=authorize, token=token)
        user_id = authorize.get_jwt_subject()

        await NotificationSchema.read_notification(
            user_id=user_id
        )
        serializer = SuccessResponseSerializer(
            message="Read All Notification",
            data={}
        )
        logging.info(
                    msg="Read All Notification",
                    extra={"custom_args": "GET-notification/read",
                    "user_id":user_id
                }
        )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )

    @classmethod
    async def add_user_device(cls, device_token, token, authorize):
        await auth_check(authorize=authorize, token=token)
        user_id = authorize.get_jwt_subject()

        await NotificationSchema.add_update_device_token(
            user_id = user_id,
            device_token = device_token
        )

        serializer = SuccessResponseSerializer(
            message="Device Added Successfully",
            data={}
        )
        logging.info(
                msg="Device Added Successfully",
                extra={"custom_args": "GET-notification/device",
                "user_id":user_id
            }
        )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )

    @classmethod
    async def show_mark(cls, token, authorize):
        await auth_check(authorize=authorize, token=token)
        user_id = authorize.get_jwt_subject()

        unread_count = await NotificationSchema.get_user_notification_count(
            user_id = user_id
        )

        if unread_count <= 0:
            show_mark = False
        else:
            show_mark = True

        serializer = SuccessResponseSerializer(
            message = "Mark Response",
            data = {
                "show_mark": show_mark
            }
        )
        logging.info(
                msg="unRead All Notification",
                extra={"custom_args": "GET-notification/unread",
                "user_id":user_id
            }
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )