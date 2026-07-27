"""
تقرير PDF لقائمة الطلبات — دعم كامل للغة العربية.
- حجم A4 صارم — المحتوى لا يتجاوز الحدود أبداً
- خط 9pt موحّد في جسم الجدول
- هيدر منظم + فوتر مع رقم الصفحة على كل صفحة
- ألوان النظام (--ab-primary #00663d)
"""
from __future__ import annotations

import io
import os
from datetime import datetime

try:
    import arabic_reshaper
    from bidi.algorithm import get_display as bidi_display
    _ARABIC_SUPPORT = True
except ImportError:
    _ARABIC_SUPPORT = False

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

pt = 1  # ReportLab uses points as base unit (1pt = 1)
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---------------------------------------------------------------------------
# قياسات الصفحة
# ---------------------------------------------------------------------------
PAGE_W, PAGE_H = A4                  # 595.28 × 841.89 pt
MARGIN_H       = 1.5 * cm            # هامش أفقي (يمين ويسار)
MARGIN_TOP     = 3.6 * cm            # مساحة الهيدر
MARGIN_BOTTOM  = 2.0 * cm            # مساحة الفوتر
CONTENT_W      = PAGE_W - 2 * MARGIN_H   # العرض المتاح للمحتوى ≈ 512 pt

# ---------------------------------------------------------------------------
# لوحة الألوان (متوافقة مع --ab-primary)
# ---------------------------------------------------------------------------
CLR_PRIMARY   = colors.HexColor('#00663d')
CLR_PRI_DARK  = colors.HexColor('#09572b')
CLR_PRI_LIGHT = colors.HexColor('#e8f4ed')
CLR_ALT_ROW   = colors.HexColor('#f6f9f8')
CLR_TOTAL_ROW = colors.HexColor('#aee6c6')
CLR_GRID      = colors.HexColor('#d2e3c8')
CLR_WHITE     = colors.white
CLR_GREY      = colors.HexColor('#525451')
CLR_GREY_LT   = colors.HexColor('#969798')

# ---------------------------------------------------------------------------
# تسجيل الخط العربي
# ---------------------------------------------------------------------------
_FONT      = 'Helvetica'
_FONT_BOLD = 'Helvetica-Bold'
_FONT_ITALIC = 'Helvetica-Oblique'


def _register_arabic_font() -> None:
    global _FONT, _FONT_BOLD, _FONT_ITALIC
    regular_candidates = [
        os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts', 'NotoNaskhArabic.ttf'),
        os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts', 'Amiri-Regular.ttf'),
        r'C:\Windows\Fonts\arial.ttf',
        r'C:\Windows\Fonts\tahoma.ttf',
        '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf',
        '/usr/share/fonts/truetype/amiri/Amiri-Regular.ttf',
    ]
    italic_candidates = [
        os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts', 'NotoNaskhArabic-Italic.ttf'),
        r'C:\Windows\Fonts\ariali.ttf',    # Arial Italic
        r'C:\Windows\Fonts\tahomai.ttf',   # Tahoma (no italic, falls back)
        '/usr/share/fonts/truetype/amiri/Amiri-Italic.ttf',
    ]
    for path in regular_candidates:
        norm = os.path.normpath(path)
        if os.path.isfile(norm):
            try:
                pdfmetrics.registerFont(TTFont('Arabic', norm))
                _FONT = _FONT_BOLD = 'Arabic'
                break
            except Exception:
                continue

    if _FONT == 'Arabic':
        for path in italic_candidates:
            norm = os.path.normpath(path)
            if os.path.isfile(norm):
                try:
                    pdfmetrics.registerFont(TTFont('ArabicItalic', norm))
                    _FONT_ITALIC = 'ArabicItalic'
                    break
                except Exception:
                    continue


_register_arabic_font()


# ---------------------------------------------------------------------------
# معالجة النص العربي
# ---------------------------------------------------------------------------

def ar(text: str) -> str:
    """
تقرير PDF لقائمة الطلبات — دعم كامل للغة العربية.
- حجم A4 صارم — المحتوى لا يتجاوز الحدود أبداً
- خط 9pt موحّد في جسم الجدول
- هيدر منظم + فوتر مع رقم الصفحة على كل صفحة
- ألوان النظام (--ab-primary #00663d)
"""
    if not text:
        return ''
    text = str(text)
    if _ARABIC_SUPPORT:
        return bidi_display(arabic_reshaper.reshape(text))
    return text


# ---------------------------------------------------------------------------
# رسم الهيدر والفوتر مباشرةً على الكانفاس (خارج Flowable)
# ---------------------------------------------------------------------------

def _draw_header(canvas, doc, workshop_name: str) -> None:
    """
تقرير PDF لقائمة الطلبات — دعم كامل للغة العربية.
- حجم A4 صارم — المحتوى لا يتجاوز الحدود أبداً
- خط 9pt موحّد في جسم الجدول
- هيدر منظم + فوتر مع رقم الصفحة على كل صفحة
- ألوان النظام (--ab-primary #00663d)
"""
    canvas.saveState()

    # --- الشريط العلوي الأخضر (اسم الورشة + التاريخ) ---
    bar1_h = 1.4 * cm
    bar1_y = PAGE_H - bar1_h
    canvas.setFillColor(CLR_PRIMARY)
    canvas.rect(0, bar1_y, PAGE_W, bar1_h, fill=1, stroke=0)

    canvas.setFillColor(CLR_WHITE)
    canvas.setFont(_FONT_BOLD, 12)
    # اسم الورشة — جهة اليمين (RTL)
    canvas.drawRightString(PAGE_W - MARGIN_H,
                           bar1_y + (bar1_h - 12 * pt) / 2 + 2,
                           ar(workshop_name))

    # أيقونة + نص "نظام الورشة" — جهة اليسار
    canvas.setFont(_FONT, 9)
    canvas.setFillColor(colors.HexColor('#aee6c6'))
    canvas.drawString(MARGIN_H,
                      bar1_y + (bar1_h - 9 * pt) / 2 + 2,
                      ar(f'تاريخ الطباعة: {datetime.now().strftime("%Y-%m-%d")}'))

    # --- الشريط الثاني الرمادي الفاتح (عنوان التقرير) ---
    bar2_h = 0.9 * cm
    bar2_y = PAGE_H - bar1_h - bar2_h
    canvas.setFillColor(CLR_PRI_LIGHT)
    canvas.rect(0, bar2_y, PAGE_W, bar2_h, fill=1, stroke=0)

    canvas.setFont(_FONT_BOLD, 10)
    canvas.setFillColor(CLR_PRI_DARK)
    canvas.drawCentredString(PAGE_W / 2,
                             bar2_y + (bar2_h - 10 * pt) / 2 + 1,
                             ar('تقرير الطلبات'))

    # خط فاصل سفلي
    canvas.setStrokeColor(CLR_GRID)
    canvas.setLineWidth(0.75)
    canvas.line(MARGIN_H, bar2_y - 1, PAGE_W - MARGIN_H, bar2_y - 1)

    canvas.restoreState()


def _draw_footer(canvas, doc) -> None:
    """
تقرير PDF لقائمة الطلبات — دعم كامل للغة العربية.
- حجم A4 صارم — المحتوى لا يتجاوز الحدود أبداً
- خط 9pt موحّد في جسم الجدول
- هيدر منظم + فوتر مع رقم الصفحة على كل صفحة
- ألوان النظام (--ab-primary #00663d)
"""
    canvas.saveState()

    footer_y = MARGIN_BOTTOM - 0.8 * cm
    canvas.setStrokeColor(CLR_GRID)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN_H, footer_y + 5 * mm, PAGE_W - MARGIN_H, footer_y + 5 * mm)

    canvas.setFont(_FONT, 8)
    canvas.setFillColor(CLR_GREY_LT)

    canvas.drawString(MARGIN_H, footer_y,
                      ar(f'صفحة {doc.page}'))

    canvas.drawRightString(PAGE_W - MARGIN_H, footer_y,
                           ar('نظام إدارة الورشة — سري'))

    canvas.restoreState()


def _on_page(canvas, doc, workshop_name: str) -> None:
    _draw_header(canvas, doc, workshop_name)
    _draw_footer(canvas, doc)


# ---------------------------------------------------------------------------
# عرض الأعمدة — المجموع = CONTENT_W بالضبط (الأخير يُحسب ديناميكياً)
# ---------------------------------------------------------------------------
_COL_WIDTHS_MAIN = [
    2.0 * cm,   # رقم الطلب
    2.9 * cm,   # العميل
    2.7 * cm,   # المركبة
    2.5 * cm,   # الخدمة
    1.6 * cm,   # السعر
    1.5 * cm,   # الخصم
    1.7 * cm,   # الإجمالي
    2.1 * cm,   # الحالة
]
_COL_WIDTHS = _COL_WIDTHS_MAIN + [CONTENT_W - sum(_COL_WIDTHS_MAIN)]  # التاريخ


# ---------------------------------------------------------------------------
# المُولِّد الرئيسي
# ---------------------------------------------------------------------------

def generate_orders_pdf(
    orders: list,
    filters: dict | None = None,
    workshop_name: str = 'ورشة الزجاج',
) -> io.BytesIO:
    """
تقرير PDF لقائمة الطلبات — دعم كامل للغة العربية.
- حجم A4 صارم — المحتوى لا يتجاوز الحدود أبداً
- خط 9pt موحّد في جسم الجدول
- هيدر منظم + فوتر مع رقم الصفحة على كل صفحة
- ألوان النظام (--ab-primary #00663d)
"""
    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=MARGIN_H,
        leftMargin=MARGIN_H,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title=ar('تقرير الطلبات'),
        author=ar(workshop_name),
    )

    # --- أنماط النصوص ---
    meta_style = ParagraphStyle(
        'Meta',
        fontName=_FONT, fontSize=9, leading=13,
        textColor=CLR_GREY, alignment=TA_CENTER, spaceAfter=3,
    )
    filter_style = ParagraphStyle(
        'Filter',
        fontName=_FONT, fontSize=9, leading=13,
        textColor=CLR_GREY, alignment=TA_CENTER, spaceAfter=6,
    )
    summary_style = ParagraphStyle(
        'Summary',
        fontName=_FONT_BOLD, fontSize=10, leading=14,
        textColor=CLR_PRI_DARK, alignment=TA_CENTER, spaceBefore=10,
    )

    story: list = []

    # --- معلومات الفلاتر (تحت الهيدر مباشرةً) ---
    if filters:
        parts = []
        if filters.get('date_from'):
            parts.append(f'من: {filters["date_from"]}')
        if filters.get('date_to'):
            parts.append(f'إلى: {filters["date_to"]}')
        if filters.get('status'):
            parts.append(f'الحالة: {filters["status"]}')
        if parts:
            story.append(Paragraph(ar('الفلاتر: ' + ' | '.join(parts)), filter_style))

    story.append(HRFlowable(
        width='100%', thickness=0.5,
        color=CLR_GRID, spaceAfter=5,
    ))

    # --- بناء صفوف الجدول ---
    headers = [
        ar('رقم الطلب'), ar('العميل'), ar('المركبة'),
        ar('الخدمة'), ar('السعر'), ar('الخصم'),
        ar('الإجمالي'), ar('الحالة'), ar('التاريخ'),
    ]
    rows: list[list] = [headers]

    for order in orders:
        rows.append([
            ar(order.order_number),
            ar(order.customer_name),
            ar(order.vehicle_info),
            ar(order.category.name if order.category else '—'),
            f'{order.price:.2f}',
            f'{order.discount:.2f}',
            f'{order.final_price:.2f}',
            ar(order.status),
            order.created_at.strftime('%Y-%m-%d') if order.created_at else '',
        ])

    total = sum(o.final_price for o in orders)

    # صف الإجمالي
    rows.append([
        ar('المجموع'), '', '', '', '', '',
        f'{total:,.2f}', '', '',
    ])

    # --- إنشاء الجدول ---
    tbl = Table(
        rows,
        colWidths=_COL_WIDTHS,
        repeatRows=1,        # يكرر الرأس في كل صفحة
        splitByRow=True,     # يسمح بتقسيم الصفوف عبر الصفحات
        hAlign='CENTER',
    )

    tbl.setStyle(TableStyle([
        # ----- رأس الجدول -----
        ('BACKGROUND',    (0, 0),  (-1, 0),  CLR_PRIMARY),
        ('TEXTCOLOR',     (0, 0),  (-1, 0),  CLR_WHITE),
        ('FONTNAME',      (0, 0),  (-1, 0),  _FONT_BOLD),
        ('FONTSIZE',      (0, 0),  (-1, 0),  10),
        ('LINEBELOW',     (0, 0),  (-1, 0),  1.5, CLR_PRI_DARK),

        # ----- جسم الجدول -----
        ('FONTNAME',      (0, 1),  (-1, -2), _FONT),
        ('FONTSIZE',      (0, 1),  (-1, -2), 10),
        ('ROWBACKGROUNDS',(0, 1),  (-1, -2), [CLR_WHITE, CLR_ALT_ROW]),

        # ----- صف المجموع -----
        ('BACKGROUND',    (0, -1), (-1, -1), CLR_TOTAL_ROW),
        ('FONTNAME',      (0, -1), (-1, -1), _FONT_BOLD),
        ('FONTSIZE',      (0, -1), (-1, -1), 10),
        ('LINEABOVE',     (0, -1), (-1, -1), 1.0, CLR_PRIMARY),

        # ----- تنسيق عام -----
        ('ALIGN',         (0, 0),  (-1, -1), 'CENTER'),
        ('VALIGN',        (0, 0),  (-1, -1), 'MIDDLE'),
        ('GRID',          (0, 0),  (-1, -1), 0.4,  CLR_GRID),
        ('TOPPADDING',    (0, 0),  (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0),  (-1, -1), 5),
        ('LEFTPADDING',   (0, 0),  (-1, -1), 3),
        ('RIGHTPADDING',  (0, 0),  (-1, -1), 3),
    ]))

    story.append(tbl)

    # --- ملخص ---
    story.append(Paragraph(
        ar(f'إجمالي الطلبات: {len(orders)}   |   إجمالي الإيرادات: {total:,.2f} ر.س'),
        summary_style,
    ))

    # --- البناء النهائي ---
    page_cb = lambda c, d: _on_page(c, d, workshop_name)
    doc.build(story, onFirstPage=page_cb, onLaterPages=page_cb)

    buf.seek(0)
    return buf
