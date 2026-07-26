"""
إشعارات SMS عبر Twilio.
تُرسَل الرسائل فقط إذا كانت بيانات Twilio مُهيَّأة في متغيرات البيئة.
"""
from __future__ import annotations

import os
import logging

logger = logging.getLogger(__name__)

_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER', '')
_ENABLED = bool(_ACCOUNT_SID and _AUTH_TOKEN and _FROM_NUMBER)


def _get_client():
    """يُعيد عميل Twilio أو None إذا لم تكن المكتبة مثبّتة."""
    try:
        from twilio.rest import Client
        return Client(_ACCOUNT_SID, _AUTH_TOKEN)
    except Exception:
        return None


def send_sms(to: str, message: str) -> bool:
    """
    يُرسل رسالة SMS.

    :param to: رقم الهاتف بصيغة E.164 مثل +966xxxxxxxxx
    :param message: نص الرسالة
    :returns: True عند النجاح
    """
    if not _ENABLED:
        logger.debug('Twilio not configured — SMS skipped.')
        return False
    if not to or not to.strip():
        return False

    client = _get_client()
    if not client:
        return False

    try:
        msg = client.messages.create(
            body=message,
            from_=_FROM_NUMBER,
            to=to.strip(),
        )
        logger.info(f'SMS sent: SID={msg.sid}')
        return True
    except Exception as exc:
        logger.warning(f'SMS failed: {exc}')
        return False


def notify_order_created(order) -> bool:
    """يُخطر العميل بإنشاء الطلب."""
    if not order.customer or not order.customer.phone:
        return False
    msg = (
        f'مرحباً {order.customer.name}،\n'
        f'تم استلام طلبكم رقم {order.order_number} بنجاح.\n'
        f'سنتواصل معكم قريباً. شكراً لثقتكم.'
    )
    return send_sms(order.customer.phone, msg)


def notify_order_status_changed(order, old_status: str) -> bool:
    """يُخطر العميل بتغيير حالة الطلب."""
    if not order.customer or not order.customer.phone:
        return False
    msg = (
        f'مرحباً {order.customer.name}،\n'
        f'تم تحديث حالة طلبكم رقم {order.order_number}:\n'
        f'{old_status} ← {order.status}'
    )
    return send_sms(order.customer.phone, msg)
