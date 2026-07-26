"""
إنشاء تقارير PDF بدعم كامل للغة العربية.
يستخدم arabic-reshaper + python-bidi + ReportLab.
"""
from __future__ import annotations

import io
import os
from datetime import datetime
from typing import List

try:
    import arabic_reshaper
    from bidi.algorithm import get_display as bidi_display
    _ARABIC_SUPPORT = True
except ImportError:
    _ARABIC_SUPPORT = False

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---------------------------------------------------------------------------
# تسجيل الخط العربي
# ---------------------------------------------------------------------------

_FONT = 'Helvetica'
_FONT_BOLD = 'Helvetica-Bold'

def _register_arabic_font() -> None:
    global _FONT, _FONT_BOLD
    candidates = [
        # خط موجود في مجلد المشروع (الأفضل)
        os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts', 'NotoNaskhArabic.ttf'),
        os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts', 'Amiri-Regular.ttf'),
        # خطوط Windows
        r'C:\Windows\Fonts\arial.ttf',
        r'C:\Windows\Fonts\tahoma.ttf',
        # Linux/macOS
        '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf',
        '/usr/share/fonts/truetype/amiri/Amiri-Regular.ttf',
    ]
    for path in candidates:
        norm = os.path.normpath(path)
        if os.path.isfile(norm):
            try:
                pdfmetrics.registerFont(TTFont('Arabic', norm))
                _FONT = 'Arabic'
                _FONT_BOLD = 'Arabic'
                return
            except Exception:
                continue

_register_arabic_font()


# ---------------------------------------------------------------------------
# دالة إعادة تشكيل النص العربي
# ---------------------------------------------------------------------------

def ar(text: str) -> str:
    """يُعيد تشكيل النص العربي ليُعرض بشكل صحيح في PDF."""
    if not text:
        return ''
    text = str(text)
    if _ARABIC_SUPPORT:
        reshaped = arabic_reshaper.reshape(text)
        return bidi_display(reshaped)
    return text


# ---------------------------------------------------------------------------
# إنشاء PDF التقرير
# ---------------------------------------------------------------------------

def generate_orders_pdf(orders: list, filters: dict = None) -> io.BytesIO:
    """
    يُنشئ تقرير PDF للطلبات.

    :param orders: قائمة كائنات Order
    :param filters: قاموس يصف الفلاتر المطبقة (اختياري)
    :returns: BytesIO جاهز للإرسال
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    # الأنماط
    title_style = ParagraphStyle(
        'Title',
        fontName=_FONT_BOLD,
        fontSize=16,
        textColor=colors.HexColor('#1B4F72'),
        alignment=1,  # center
        spaceAfter=6,
    )
    sub_style = ParagraphStyle(
        'Sub',
        fontName=_FONT,
        fontSize=9,
        textColor=colors.grey,
        alignment=1,
        spaceAfter=12,
    )
    cell_style = ParagraphStyle(
        'Cell',
        fontName=_FONT,
        fontSize=8,
        alignment=1,
    )

    story = []

    # العنوان
    story.append(Paragraph(ar('تقرير الطلبات'), title_style))
    story.append(Paragraph(
        ar(f'تاريخ التقرير: {datetime.utcnow().strftime("%Y-%m-%d")}'),
        sub_style,
    ))

    # تفاصيل الفلاتر
    if filters:
        parts = []
        if filters.get('date_from'):
            parts.append(f'من: {filters["date_from"]}')
        if filters.get('date_to'):
            parts.append(f'إلى: {filters["date_to"]}')
        if filters.get('status'):
            parts.append(f'الحالة: {filters["status"]}')
        if parts:
            story.append(Paragraph(ar(' | '.join(parts)), sub_style))

    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#1B4F72')))
    story.append(Spacer(1, 0.3 * cm))

    # رؤوس الجدول
    headers = [
        ar('رقم الطلب'), ar('العميل'), ar('المركبة'),
        ar('الخدمة'), ar('السعر'), ar('الخصم'),
        ar('الإجمالي'), ar('الحالة'), ar('التاريخ'),
    ]

    # بناء صفوف البيانات
    rows = [headers]
    for order in orders:
        rows.append([
            ar(order.order_number),
            ar(order.customer_name),
            ar(order.vehicle_info),
            ar(order.category.name if order.category else ''),
            f'{order.price:.2f}',
            f'{order.discount:.2f}',
            f'{order.final_price:.2f}',
            ar(order.status),
            order.created_at.strftime('%Y-%m-%d') if order.created_at else '',
        ])

    # صف الإجماليات
    total = sum(o.final_price for o in orders)
    rows.append([
        ar('الإجمالي'), '', '', '', '', '',
        f'{total:.2f}', '', '',
    ])

    # عرض الأعمدة
    col_widths = [2.5*cm, 3.5*cm, 3.5*cm, 3*cm,
                  1.8*cm, 1.8*cm, 2*cm, 2.5*cm, 2.2*cm]

    table = Table(rows, colWidths=col_widths, repeatRows=1)

    hdr_color = colors.HexColor('#1B4F72')
    alt_color = colors.HexColor('#EBF5FB')
    total_color = colors.HexColor('#D5E8D4')

    style = TableStyle([
        # رأس الجدول
        ('BACKGROUND',   (0, 0), (-1, 0), hdr_color),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.white),
        ('FONTNAME',     (0, 0), (-1, 0), _FONT_BOLD),
        ('FONTSIZE',     (0, 0), (-1, 0), 9),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME',     (0, 1), (-1, -1), _FONT),
        ('FONTSIZE',     (0, 1), (-1, -1), 8),
        ('GRID',         (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, alt_color]),
        # صف الإجماليات
        ('BACKGROUND',   (0, -1), (-1, -1), total_color),
        ('FONTNAME',     (0, -1), (-1, -1), _FONT_BOLD),
        ('TOPPADDING',   (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 5),
    ])
    table.setStyle(style)
    story.append(table)

    # ملخص في الأسفل
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        ar(f'إجمالي عدد الطلبات: {len(orders)}  |  إجمالي الإيرادات: {total:.2f} ر.س'),
        ParagraphStyle('Footer', fontName=_FONT_BOLD, fontSize=9,
                       textColor=colors.HexColor('#1B4F72'), alignment=1),
    ))

    doc.build(story)
    buf.seek(0)
    return buf
