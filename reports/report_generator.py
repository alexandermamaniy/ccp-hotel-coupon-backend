import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile

def generate_pdf(processed_data, coupon_gral_information, from_date_report, current_day, hotelier_name):

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    x = 50
    y = 750
    p.drawString(x+150, y, f"{hotelier_name} Roupon Report")
    y -= 50
    p.drawString(x+100, y, f"User coupon interaction from {from_date_report} to {current_day}")
    y -= 50
    if not bool(processed_data):
        p.drawString(x, y, f"Your coupons have not been viewed or redeemed")
    else:
        for key, value in processed_data.items():
            coupon_title = "Coupon: "+value['coupon_title']
            p.drawString(x, y, (f"{coupon_title: <45}"
                                f"Views: {value['view']: <10}"
                                f"Redeems: {value['redeem']: <10}"))
            y -= 20

    y -= 50
    p.drawString(x + 150, y, f"General information about your coupons")
    y -= 50
    for key, value in coupon_gral_information.items():
        coupon_title = "Coupon: "+value['title']
        discount = value['discount'] + "%"
        p.drawString(x, y, (f"{coupon_title: <40}"
                            f"Quantity: {value['quantity']: <7}"
                            f"Discount: {discount: <7}"
                            f"Redeemeds: {value['how_many_have_redeemed']: <7}"
                            f"Used: {value['how_many_have_used']: <7}"))
        y -= 20

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer