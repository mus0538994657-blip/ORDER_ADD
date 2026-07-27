"""
تقارير PDF بدعم كامل للغة العربية.
- حجم A4 صارم — المحتوى لا يتجاوز الحدود أبداً
- خط 10pt موحّد في جسم الجدول
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


def _register_arabic_font() -> None:
    global _FONT, _FONT_BOLD
    candidates = [
        os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts', 'NotoNaskhArabic.ttf'),
        os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts', 'Amiri-Regular.ttf'),
        r'C:\Windows\Fonts\arial.ttf',
        r'C:\Windows\Fonts\tahoma.ttf',
        '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf',
        '/usr/share/fonts/truetype/amiri/Amiri-Regular.ttf',
    ]
    for path in candidates:
        norm = os.path.normpath(path)
        if os.path.isfile(norm):
            try:
                pdfmetrics.registerFont(TTFont('Arabic', norm))
                _FONT = _FONT_BOLD = 'Arabic'
                return
            except Exception:
                continue


_register_arabic_font()


# ---------------------------------------------------------------------------
# معالجة النص العربي
# ---------------------------------------------------------------------------

def ar(text: str) -> str:
    """يُعيد تشكيل النص العربي ليُعرض بشكل صحيح في PDF."""
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
    هيدر منظم على كل صفحة:
    ┌──────────────────────────────────────────────────┐
    │  تاريخ الطباعة          [Logo/Name] ورشة الزجاج │  ← شريط أخضر
    │  تقرير الطلبات                                   │  ← شريط رمادي فاتح
    └──────────────────────────────────────────────────┘
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
    """فوتر: رقم الصفحة يسار، نص الحقوق يمين."""
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
    يُنشئ PDF للطلبات بمواصفات:
    - A4 — هوامش 1.5cm
    - خط 10pt في جسم الجدول، 10pt bold في الرأس
    - هيدر (اسم الورشة + التاريخ + عنوان) على كل صفحة
    - فوتر (رقم الصفحة) على كل صفحة
    - splitByRow=True لضمان عدم تجاوز حدود الصفحة
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


# ---------------------------------------------------------------------------
# PDF طلب مفرد (فاتورة / أمر عمل)
# ---------------------------------------------------------------------------

# عرض الأعمدة لجدول بنود الطلب — مجموعها = CONTENT_W (18cm)
# 0.6 + 2.0 + 4.0 + 4.0 + 1.5 + 1.5 + 2.2 + 2.2 = 18.0 cm
_ITEM_COL_FIXED = (0.6 + 2.0 + 4.0 + 1.5 + 1.5 + 2.2 + 2.2) * cm  # 14 cm
_ITEM_WIDTHS = [
    0.6 * cm,                          # #
    2.0 * cm,                          # الكود
    4.0 * cm,                          # الاسم
    CONTENT_W - _ITEM_COL_FIXED,       # الوصف ≈ 4 cm (ديناميكي)
    1.5 * cm,                          # الوحدة
    1.5 * cm,                          # الكمية
    2.2 * cm,                          # سعر الوحدة
    2.2 * cm,                          # الإجمالي
]


def _info_table(pairs: list[tuple[str, str]], label_w: float = 3.0 * cm) -> Table:
    """ينشئ جدول بيانات info مكوّن من سطرين (label | value)."""
    val_w = CONTENT_W / 2 - label_w
    lbl_style = ParagraphStyle('InfoLbl', fontName=_FONT_BOLD, fontSize=9,
                               leading=12, textColor=CLR_GREY, alignment=TA_RIGHT,
                               wordWrap='RTL')
    val_style = ParagraphStyle('InfoVal', fontName=_FONT, fontSize=9,
                               leading=12, textColor=CLR_PRI_DARK, alignment=TA_RIGHT,
                               wordWrap='RTL')
    data = [
        [Paragraph(ar(k), lbl_style), Paragraph(ar(str(v) if v else '—'), val_style)]
        for k, v in pairs
    ]
    col_w = [label_w, val_w]
    tbl = Table(data, colWidths=col_w)
    tbl.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',    (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING',   (0, 0), (-1, -1), 4),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 4),
        ('LINEBELOW',     (0, -1), (-1, -1), 0.4, CLR_GRID),
    ]))
    return tbl


def generate_order_pdf(order, items: list, workshop_name: str = 'ورشة الزجاج') -> io.BytesIO:
    """
    يُنشئ PDF لطلب مفرد (أمر عمل / فاتورة) بمحتوى:
    - هيدر: اسم الورشة + رقم الطلب + التاريخ
    - جدولان جانبيان: بيانات العميل | بيانات المركبة
    - جدول بنود الطلب مع الإجمالي
    - ملاحظات (إن وجدت)
    """
    buf = io.BytesIO()

    # هيدر خاص بالطلب يُعيد تعريف bar2 ليُظهر رقم الطلب
    def _draw_order_header(canvas, doc) -> None:
        canvas.saveState()

        # شريط أخضر — اسم الورشة + تاريخ الطباعة
        bar1_h = 1.4 * cm
        bar1_y = PAGE_H - bar1_h
        canvas.setFillColor(CLR_PRIMARY)
        canvas.rect(0, bar1_y, PAGE_W, bar1_h, fill=1, stroke=0)

        canvas.setFillColor(CLR_WHITE)
        canvas.setFont(_FONT_BOLD, 12)
        canvas.drawRightString(PAGE_W - MARGIN_H,
                               bar1_y + (bar1_h - 12) / 2 + 2,
                               ar(workshop_name))
        canvas.setFont(_FONT, 9)
        canvas.setFillColor(colors.HexColor('#aee6c6'))
        canvas.drawString(MARGIN_H,
                          bar1_y + (bar1_h - 9) / 2 + 2,
                          ar(f'تاريخ الطباعة: {datetime.now().strftime("%Y-%m-%d")}'))

        # شريط رقم الطلب + الحالة
        bar2_h = 1.0 * cm
        bar2_y = PAGE_H - bar1_h - bar2_h
        canvas.setFillColor(CLR_PRI_LIGHT)
        canvas.rect(0, bar2_y, PAGE_W, bar2_h, fill=1, stroke=0)

        canvas.setFont(_FONT_BOLD, 11)
        canvas.setFillColor(CLR_PRI_DARK)
        canvas.drawRightString(PAGE_W - MARGIN_H,
                               bar2_y + (bar2_h - 11) / 2 + 1,
                               ar(f'أمر العمل رقم: {order.order_number}'))

        canvas.setFont(_FONT, 9)
        canvas.setFillColor(CLR_GREY)
        created = order.created_at.strftime('%Y-%m-%d') if order.created_at else ''
        canvas.drawString(MARGIN_H,
                          bar2_y + (bar2_h - 9) / 2 + 1,
                          ar(f'الحالة: {order.status}    |    التاريخ: {created}'))

        canvas.setStrokeColor(CLR_GRID)
        canvas.setLineWidth(0.75)
        canvas.line(MARGIN_H, bar2_y - 1, PAGE_W - MARGIN_H, bar2_y - 1)

        canvas.restoreState()

    def _draw_order_footer(canvas, doc) -> None:
        canvas.saveState()
        footer_y = MARGIN_BOTTOM - 0.8 * cm
        canvas.setStrokeColor(CLR_GRID)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN_H, footer_y + 5 * mm, PAGE_W - MARGIN_H, footer_y + 5 * mm)
        canvas.setFont(_FONT, 8)
        canvas.setFillColor(CLR_GREY_LT)
        canvas.drawString(MARGIN_H, footer_y, ar(f'صفحة {doc.page}'))
        canvas.drawRightString(PAGE_W - MARGIN_H, footer_y, ar(workshop_name + ' — وثيقة سرية'))
        canvas.restoreState()

    MARGIN_TOP_ORDER = 2.8 * cm  # هيدر الطلب أطول قليلاً

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=MARGIN_H,
        leftMargin=MARGIN_H,
        topMargin=MARGIN_TOP_ORDER,
        bottomMargin=MARGIN_BOTTOM,
        title=ar(f'طلب {order.order_number}'),
        author=ar(workshop_name),
    )

    section_title_style = ParagraphStyle(
        'SectionTitle',
        fontName=_FONT_BOLD, fontSize=10, leading=14,
        textColor=CLR_WHITE, alignment=TA_RIGHT,
        leftPadding=6, rightPadding=6,
        spaceAfter=0,
    )
    notes_style = ParagraphStyle(
        'Notes',
        fontName=_FONT, fontSize=9, leading=14,
        textColor=CLR_GREY, alignment=TA_RIGHT,
        spaceBefore=4,
    )

    def section_header(title: str):
        """شريط عنوان القسم."""
        p = Paragraph(ar(title), section_title_style)
        t = Table([[p]], colWidths=[CONTENT_W])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), CLR_PRIMARY),
            ('LEFTPADDING',  (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING',   (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 5),
        ]))
        return t

    story: list = []

    # ─── قسم بيانات العميل والمركبة جانبياً ───
    cust = order.customer
    veh  = order.vehicle

    cust_pairs = [
        ('الاسم',    cust.name   if cust else ''),
        ('الهاتف',   cust.phone  if cust else ''),
        ('البريد',   cust.email  if cust else ''),
        ('العنوان',  cust.address if cust else ''),
    ]
    veh_pairs = [
        ('الماركة',   veh.make        if veh else ''),
        ('الموديل',   veh.model       if veh else ''),
        ('سنة الصنع', str(veh.year)   if veh and veh.year else ''),
        ('رقم اللوحة', veh.plate_number if veh else ''),
    ]

    cust_tbl = _info_table(cust_pairs, label_w=2.5 * cm)
    veh_tbl  = _info_table(veh_pairs,  label_w=2.5 * cm)

    # عنوان القسمين
    cust_hdr = Table(
        [[Paragraph(ar('بيانات العميل'), section_title_style)]],
        colWidths=[CONTENT_W / 2 - 3],
    )
    cust_hdr.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CLR_PRIMARY),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    veh_hdr = Table(
        [[Paragraph(ar('بيانات المركبة'), section_title_style)]],
        colWidths=[CONTENT_W / 2 - 3],
    )
    veh_hdr.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CLR_PRIMARY),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    gap = 6
    half = CONTENT_W / 2 - gap / 2

    info_outer = Table(
        [[cust_hdr, veh_hdr], [cust_tbl, veh_tbl]],
        colWidths=[half, half],
        spaceBefore=4,
    )
    info_outer.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
        ('TOPPADDING',    (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('LINEAFTER',     (0, 0), (0, -1), 0.5, CLR_GRID),
    ]))

    story.append(info_outer)
    story.append(Spacer(1, 0.3 * cm))

    # ─── جدول البنود ───
    story.append(section_header('بنود الطلب'))
    story.append(Spacer(1, 2))

    # أنماط خلايا الجدول (تلتف داخل عرض العمود)
    _hdr_s = ParagraphStyle('IH', fontName=_FONT_BOLD, fontSize=9, leading=11,
                             textColor=CLR_WHITE, alignment=TA_CENTER, wordWrap='RTL')
    _num_s = ParagraphStyle('IN', fontName=_FONT,      fontSize=9, leading=11,
                             textColor=CLR_PRI_DARK, alignment=TA_CENTER)
    _txt_s = ParagraphStyle('IT', fontName=_FONT,      fontSize=9, leading=11,
                             textColor=CLR_PRI_DARK, alignment=TA_RIGHT, wordWrap='RTL')
    _smry_s= ParagraphStyle('IS', fontName=_FONT_BOLD, fontSize=9, leading=11,
                             textColor=CLR_PRI_DARK, alignment=TA_RIGHT, wordWrap='RTL')
    _smry_w= ParagraphStyle('ISW', fontName=_FONT_BOLD, fontSize=9, leading=11,
                              textColor=CLR_WHITE, alignment=TA_RIGHT, wordWrap='RTL')

    def _p(text, style=None):
        return Paragraph(ar(str(text)) if text else '', style or _txt_s)

    item_hdrs = [_p(t, _hdr_s) for t in
                 ['#', 'الكود', 'الاسم', 'الوصف', 'الوحدة', 'الكمية', 'سعر الوحدة', 'الإجمالي']]
    rows: list[list] = [item_hdrs]

    for i, item in enumerate(items, 1):
        rows.append([
            _p(str(i), _num_s),
            _p(item.code, _num_s),
            _p(item.name),
            _p(item.description or ''),
            _p(item.unit, _num_s),
            _p(f'{item.quantity:g}', _num_s),
            _p(f'{item.unit_price:.2f}', _num_s),
            _p(f'{item.total:.2f}', _num_s),
        ])

    # صف المجموع
    subtotal = sum(it.total for it in items)
    rows.append([_p('المجموع', _smry_s), _p(''), _p(''), _p(''), _p(''), _p(''), _p(''), _p(f'{subtotal:.2f}', _num_s)])
    if order.discount:
        rows.append([_p('الخصم', _smry_s), _p(''), _p(''), _p(''), _p(''), _p(''), _p(''), _p(f'- {order.discount:.2f}', _num_s)])
    rows.append([_p('الإجمالي النهائي', _smry_w), _p(''), _p(''), _p(''), _p(''), _p(''), _p(''), _p(f'{order.final_price:.2f}', _smry_w)])

    total_rows = len(rows)
    summary_start = total_rows - (3 if order.discount else 2)

    items_tbl = Table(rows, colWidths=_ITEM_WIDTHS, repeatRows=1, splitByRow=True)
    items_style = [
        # رأس الجدول
        ('BACKGROUND',    (0, 0),  (-1, 0),  CLR_PRIMARY),
        ('TEXTCOLOR',     (0, 0),  (-1, 0),  CLR_WHITE),
        ('FONTNAME',      (0, 0),  (-1, 0),  _FONT_BOLD),
        ('FONTSIZE',      (0, 0),  (-1, 0),  10),
        # جسم الجدول
        ('FONTNAME',      (0, 1),  (-1, summary_start - 1), _FONT),
        ('FONTSIZE',      (0, 1),  (-1, summary_start - 1), 10),
        ('ROWBACKGROUNDS',(0, 1),  (-1, summary_start - 1), [CLR_WHITE, CLR_ALT_ROW]),
        # صفوف الملخص
        ('BACKGROUND',    (0, summary_start), (-1, -1), CLR_TOTAL_ROW),
        ('FONTNAME',      (0, summary_start), (-1, -1), _FONT_BOLD),
        ('FONTSIZE',      (0, summary_start), (-1, -1), 10),
        ('SPAN',          (0, summary_start), (-2, summary_start)),
        # عام
        ('ALIGN',         (0, 0),  (-1, -1), 'CENTER'),
        ('VALIGN',        (0, 0),  (-1, -1), 'MIDDLE'),
        ('GRID',          (0, 0),  (-1, -1), 0.4, CLR_GRID),
        ('TOPPADDING',    (0, 0),  (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0),  (-1, -1), 5),
        ('LEFTPADDING',   (0, 0),  (-1, -1), 3),
        ('RIGHTPADDING',  (0, 0),  (-1, -1), 3),
    ]

    # SPAN لصفوف الخصم والإجمالي النهائي
    if order.discount:
        items_style.append(('SPAN', (0, summary_start + 1), (-2, summary_start + 1)))
        items_style.append(('SPAN', (0, summary_start + 2), (-2, summary_start + 2)))
        items_style.append(('BACKGROUND', (0, summary_start + 2), (-1, summary_start + 2), CLR_PRIMARY))
        items_style.append(('TEXTCOLOR',  (0, summary_start + 2), (-1, summary_start + 2), CLR_WHITE))
    else:
        items_style.append(('SPAN', (0, summary_start + 1), (-2, summary_start + 1)))
        items_style.append(('BACKGROUND', (0, summary_start + 1), (-1, summary_start + 1), CLR_PRIMARY))
        items_style.append(('TEXTCOLOR',  (0, summary_start + 1), (-1, summary_start + 1), CLR_WHITE))

    items_tbl.setStyle(TableStyle(items_style))
    story.append(items_tbl)

    # ─── ملاحظات ───
    if order.notes:
        story.append(Spacer(1, 0.3 * cm))
        story.append(section_header('ملاحظات'))
        story.append(Spacer(1, 2))
        story.append(Paragraph(ar(order.notes), notes_style))

    cb = lambda c, d: (_draw_order_header(c, d), _draw_order_footer(c, d))

    def _page_cb(canvas, doc):
        _draw_order_header(canvas, doc)
        _draw_order_footer(canvas, doc)

    doc.build(story, onFirstPage=_page_cb, onLaterPages=_page_cb)
    buf.seek(0)
    return buf

