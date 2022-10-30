#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import os
from pathlib import Path
from sys import stderr
from .decorators import exception_handler

from .PYFPDF import PYFPDF


class PaymentPDF:
    def __init__(self, p_cPath, p_cCodigo):
        self.codigo = p_cCodigo
        self.lcPath = p_cPath
        Path(p_cPath).mkdir(parents=True, exist_ok=True)
        self.paData = None
        self.paDatos = None
        self.error = None
        self.l_w = 0
        self.l_h = 0.4
        print(self.lcPath, file=stderr)
        print(self.codigo, file=stderr)

    def setData(self, data):
        self.paData = data

    def setDatos(self, datos):
        self.paDatos = datos

    def setWidth(self, w):
        self.l_w = w

    def setHeigth(self, h):
        self.l_h = h

    @exception_handler(False)
    def mxprint(self, CATEGORIES, PRICES, DATE_FORMAT):
        if self.paData is None:
            raise ValueError("DATA NO DEFINIDA")
        loPdf = PYFPDF()
        loPdf.alias_nb_pages()
        loPdf.add_page()
        loPdf.setHeader("BOLETA")
        loPdf.set_margins(1, 1.6, 1.2)
        loPdf.set_font("Arial", "", 6)
        self.setWidth(loPdf._width())
        w1 = self.l_w * 0.1
        w2 = self.l_w * 0.2
        w3 = self.l_w * 0.3
        w4 = self.l_w * 0.4
        w6 = self.l_w * 0.6
        loPdf.set_border(1)
        print("----DATA", file=stderr)
        print(self.paData, file=stderr)
        loPdf.row(["COMPROBANTE:", self.paData["id"]], [w4, w6])
        loPdf.row(["FECHA:", datetime.now().strftime(DATE_FORMAT)], [w4, w6])
        loPdf.row(["NOMBRE", self.paData["name"]], [w4, w6])
        total = 0
        print("---DATOS", file=stderr)
        print(self.paDatos, file=stderr)
        if self.paDatos is not None:
            for i, item in enumerate(self.paDatos):
                print(item, file=stderr)
                cat = item["categoryid"]
                total += PRICES[cat]
                print(total, file=stderr)
                print(CATEGORIES[cat], file=stderr)
                print(PRICES[cat], file=stderr)
                loPdf.row([i, item["ticketid"],CATEGORIES[cat], PRICES[cat]], [w1, w2, w4, w3])
            loPdf.row(["", "TOTAL", total], [w1, w6, w3])
            loPdf.set_border(0)
        total_path = os.path.join(self.lcPath, self.codigo+".pdf")
        loPdf.output(total_path, "F")
        print("------------------PATH--------------")
        print(total_path, file=stderr)
