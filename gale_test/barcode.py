#!/usr/bin/env python3

from reportlab.lib.pagesizes import A4
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.barcode.eanbc import Ean13BarcodeWidget
from reportlab.graphics import renderPDF
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus.flowables import PageBreak

"""
Adjust pagesize, number of labels, barcode size and
positions of barcode and description to your needs.
"""
from reportlab.lib.units import inch, mm
# pagesize=(4*inch, 3*inch), rightMargin=0, leftMargin=0, topMargin=1*mm, bottomMargin=0
PAGESIZE = (4*inch, 3*inch)
NUM_LABELS_X = 1
NUM_LABELS_Y = 1
BAR_WIDTH = 1.5
BAR_HEIGHT = 51.0
TEXT_Y = 80
BARCODE_Y = 17


LABEL_WIDTH = PAGESIZE[0] / NUM_LABELS_X
LABEL_HEIGHT = PAGESIZE[1] / NUM_LABELS_Y
SHEET_TOP = PAGESIZE[1]


def label(ean13, description):
    """
    Generate a drawing with EAN-13 barcode and descriptive text.

    :param ean13: The EAN-13 Code.
    :type ean13: str
    :param description: Short product description.
    :type description: str
    :return: Drawing with barcode and description
    :rtype: Drawing
    """
    text = String(0, TEXT_Y, description, fontName="Helvetica-Bold",
                  fontSize=12, textAnchor="middle")
    text.x = LABEL_WIDTH / 2  # center text (anchor is in the middle)

    barcode = Ean13BarcodeWidget(ean13)
    barcode.barWidth = BAR_WIDTH
    barcode.barHeight = BAR_HEIGHT
    x0, y0, bw, bh = barcode.getBounds()
    barcode.x = (LABEL_WIDTH - bw) / 2  # center barcode
    barcode.y = BARCODE_Y  # spacing from label bottom (pt)

    label_drawing = Drawing(LABEL_WIDTH, LABEL_HEIGHT)
    label_drawing.add(text)
    label_drawing.add(barcode)
    return label_drawing


def fill_sheet(canvas, label_drawing):
    """
    Simply fill the given ReportLab canvas with label drawings.

    :param canvas: The ReportLab canvas
    :type canvas: Canvas
    :param label_drawing: Contains Drawing of configured size
    :type label_drawing: Drawing
    """
    for u in range(0, NUM_LABELS_Y):
        for i in range(0, NUM_LABELS_X):
            x = i * LABEL_WIDTH
            y = SHEET_TOP - 1.5*inch 
            renderPDF.draw(label_drawing, canvas, x, y)


if __name__ == '__main__':
    canvas = Canvas("ean-stick.pdf", pagesize= (4*inch, 3*inch))
    for i in range(0,1000):
    
        sticker = label('54320725860', 'SHIPPR-PRJ13' + str(i))
        
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(10, 65, "Shipment ID")
        canvas.drawString(10, 50, "54320725860")
        canvas.drawString(10, 35, "Delivery on")
        canvas.drawString(10, 20, "18/07/2018")
        canvas.drawString(145, 65, "Ship To:")
        
        address = "House No xyz street 123 Indiranagar Bangalore 560093"
        address = address.split()
        address_str = ""
        address_str_test = ""
        j = 0
        for i in range(len(address)):
            address_str_test += address[i] + str(" ")
            
            if len(address_str_test) > 25:
                address_str_test = address[i] + str(" ")
               
                canvas.drawString(145, 50 - 15*j, address_str)
                j += 1
                address_str = address_str_test
            else:
                address_str = address_str_test
        canvas.drawString(145, 50 - 15*j, address_str)
        
        
        fill_sheet(canvas, sticker)
        canvas.showPage()
    canvas.save()