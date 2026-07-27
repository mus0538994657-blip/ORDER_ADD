"""
PDF فاتورة / أمر عمل لطلب مفرد — دعم كامل للغة العربية RTL.
- A4 صارم — هيدر يعرض رقم الطلب والحالة
- جدول بنود RTL حقيقي (# يميناً — الإجمالي يساراً)
- جدولان جانبيان: بيانات العميل (يمين) | بيانات المركبة (يسار)
- تاريخ الطباعة بخط مائل (italic)
"""
from __future__ import annotations

from .pdf import (
    ar,
    PAGE_W, PAGE_H, MARGIN_H, MARGIN_BOTTOM, CONTENT_W,
    CLR_PRIMARY, CLR_PRI_DARK, CLR_PRI_LIGHT, CLR_ALT_ROW,
    CLR_TOTAL_ROW, CLR_GRID, CLR_WHITE, CLR_GREY, CLR_GREY_LT,
    _FONT, _FONT_BOLD, _FONT_ITALIC,
    cm, mm, colors, datetime,
    SimpleDocTemplate, A4, Table, TableStyle,
    Paragraph, Spacer, ParagraphStyle, TA_CENTER, TA_RIGHT,
)
import io
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

        # تاريخ الطباعة — خط مائل (italic simulation بتحويل affine)
        date_str = ar(f'تاريخ الطباعة: {datetime.now().strftime("%Y-%m-%d")}')
        date_x = MARGIN_H
        date_y = bar1_y + (bar1_h - 9) / 2 + 2
        canvas.saveState()
        canvas.setFont(_FONT_ITALIC, 9)
        canvas.setFillColor(colors.HexColor('#aee6c6'))
        # shear matrix لمحاكاة الخط المائل إذا لم يتوفر خط italic منفصل
        if _FONT_ITALIC == _FONT:  # fallback: لا يوجد خط italic منفصل
            canvas.transform(1, 0, -0.2, 1, date_x + 0.2 * date_y, 0)
            canvas.drawString(0, date_y, date_str)
        else:
            canvas.drawString(date_x, date_y, date_str)
        canvas.restoreState()

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

    # RTL: المركبة يسار — العميل يمين (في ReportLab LTR = يسار أولاً)
    info_outer = Table(
        [[veh_hdr, cust_hdr], [veh_tbl, cust_tbl]],
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

    # RTL: نبني البيانات بالترتيب اللوجيكي ثم نعكسها
    # الترتيب اللوجيكي: [#, كود, اسم, وصف, وحدة, كمية, سعر, إجمالي]
    # بعد العكس (لعرض RTL): [إجمالي, سعر, كمية, وحدة, وصف, اسم, كود, #]
    _widths_rtl = list(reversed(_ITEM_WIDTHS))

    def _rtl(row): return list(reversed(row))

    item_hdrs = _rtl([_p(t, _hdr_s) for t in
                      ['#', 'الكود', 'الاسم', 'الوصف', 'الوحدة', 'الكمية', 'سعر الوحدة', 'الإجمالي']])
    rows: list[list] = [item_hdrs]

    for i, item in enumerate(items, 1):
        rows.append(_rtl([
            _p(str(i), _num_s),
            _p(item.code, _num_s),
            _p(item.name),
            _p(item.description or ''),
            _p(item.unit, _num_s),
            _p(f'{item.quantity:g}', _num_s),
            _p(f'{item.unit_price:.2f}', _num_s),
            _p(f'{item.total:.2f}', _num_s),
        ]))

    # صفوف الملخص — بعد العكس: القيمة في col 0 (يسار=إجمالي)، الملصق يمتد 1→7
    subtotal = sum(it.total for it in items)
    # [value, '', '', '', '', '', '', label] ثم معكوس → [label, '', '', '', '', '', '', value]
    # نبني بالترتيب العادي ثم نعكس
    rows.append(_rtl([_p('المجموع', _smry_s), _p(''), _p(''), _p(''), _p(''), _p(''), _p(''), _p(f'{subtotal:.2f}', _num_s)]))
    if order.discount:
        rows.append(_rtl([_p('الخصم', _smry_s), _p(''), _p(''), _p(''), _p(''), _p(''), _p(''), _p(f'- {order.discount:.2f}', _num_s)]))
    rows.append(_rtl([_p('الإجمالي النهائي', _smry_w), _p(''), _p(''), _p(''), _p(''), _p(''), _p(''), _p(f'{order.final_price:.2f}', _smry_w)]))

    total_rows = len(rows)
    summary_start = total_rows - (3 if order.discount else 2)

    # بعد العكس: col 0 = إجمالي (يسار)، col 7 = # (يمين)
    # SPAN: الملصق في cols 0..6، القيمة في col 7
    items_tbl = Table(rows, colWidths=_widths_rtl, repeatRows=1, splitByRow=True)
    items_style = [
        # رأس الجدول
        ('BACKGROUND',    (0, 0),  (-1, 0),  CLR_PRIMARY),
        ('TEXTCOLOR',     (0, 0),  (-1, 0),  CLR_WHITE),
        # جسم الجدول
        ('ROWBACKGROUNDS',(0, 1),  (-1, summary_start - 1), [CLR_WHITE, CLR_ALT_ROW]),
        # صفوف الملخص — خلفية موحدة للصف بأكمله
        ('BACKGROUND',    (0, summary_start), (-1, -1), CLR_TOTAL_ROW),
        ('FONTNAME',      (0, summary_start), (-1, -1), _FONT_BOLD),
        # عام
        ('FONTNAME',      (0, 0),  (-1, -1), _FONT),
        ('FONTSIZE',      (0, 0),  (-1, -1), 9),
        ('FONTNAME',      (0, 0),  (-1, 0),  _FONT_BOLD),
        ('ALIGN',         (0, 0),  (-1, -1), 'CENTER'),
        ('VALIGN',        (0, 0),  (-1, -1), 'MIDDLE'),
        ('GRID',          (0, 0),  (-1, -1), 0.4, CLR_GRID),
        ('TOPPADDING',    (0, 0),  (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0),  (-1, -1), 5),
        ('LEFTPADDING',   (0, 0),  (-1, -1), 3),
        ('RIGHTPADDING',  (0, 0),  (-1, -1), 3),
    ]

    # SPAN: بعد العكس، الملصق (المجموع/الخصم/الإجمالي) في أعمدة 0→6، القيمة في col 7
    items_style.append(('SPAN', (0, summary_start), (-2, summary_start)))
    last_row = total_rows - 1
    if order.discount:
        items_style.append(('SPAN', (0, summary_start + 1), (-2, summary_start + 1)))
        items_style.append(('SPAN', (0, last_row), (-2, last_row)))
        items_style.append(('BACKGROUND', (0, last_row), (-1, last_row), CLR_PRIMARY))
        items_style.append(('TEXTCOLOR',  (0, last_row), (-1, last_row), CLR_WHITE))
    else:
        items_style.append(('SPAN', (0, last_row), (-2, last_row)))
        items_style.append(('BACKGROUND', (0, last_row), (-1, last_row), CLR_PRIMARY))
        items_style.append(('TEXTCOLOR',  (0, last_row), (-1, last_row), CLR_WHITE))

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

