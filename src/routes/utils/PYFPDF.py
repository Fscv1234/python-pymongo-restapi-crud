#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path

from fpdf import FPDF


class PYFPDF(FPDF):
    def __init__(self):
        FPDF.__init__(self, "P", "cm", [8.5,14.8])

        self.lcTitulo = "FORMATO"

        self.ln_h = 0.4
        self.row_square = None
        self.widths = []
        self.aligns = []
        self.bolds = []
        self.borders = []
        self.align = "L"
        self.bold = " "
        self.br = 0

    def set_row_square(self, h: float):
        self.row_square = h

    def set_h(self, h: float):
        self.ln_h = h

    def set_border(self, br: int):
        self.br = br

    def set_borders(self, br):
        self.borders = br

    def set_align(self, a):
        self.align = a

    def set_aligns(self, a):
        self.aligns = a

    def set_bold(self, b: str):
        self.bold = b

    def set_bolds(self, b):
        self.bolds = b

    def setHeader(self, titulo):
        if titulo is not None and len(titulo) > 0 and titulo.strip() != "":
            self.lcTitulo = titulo

    # def header(self):
    #     # loFirma = Config.PATH_PDF_SRC + "/logo.jpg"
    #     # if Path(loFirma).is_file():
    #     #     self.image(loFirma, 1, 1, 3, 1.8)

    #     self.ln(0.3)
    #     self.set_font("Arial", "B", 17)
    #     self.cell(0, 0, self.lcTitulo, 0, 0, "C")
    #     self.ln(1)

    # # Page footer
    # def footer(self):
    #     self.set_y(-0.6)
    #     self.set_font("Arial", "", 6)
    #     self.cell(0, 0.2, "Teléfono: 054-276764", 0, 2, "L")
    #     self.cell(0, 0.2, "Dirección: Calle León Velarde 406 Yanalnuara", 0, 2, "L")
    #     self.set_y(-0.6)
    #     self.cell(0, 0.2, "www.aliviari.pe", 0, 2, "R")
    #     self.cell(0, 0.2, "Pagina " + str(self.page_no()) + "/{nb}", 0, 2, "R")

    def vertical_align(self, txt, nc, nb):
        txt = str(txt)
        if nc > len(txt):
            ncols = 1
        else:
            ncols = (len(txt) // nc) + 1
        data = txt
        if ncols < nb:
            times = (nb - ncols) // 2
            data = "\n" * times + txt
        return data

    def is_string(self, s):
        if type(s) in [type(""), type("")]:
            return True
        return False

    def _percent(self, s):
        if "%" == s[-1]:
            return float(s[:-1])
        else:
            return 0

    def _width(self) -> float:
        return float(self.w - self.r_margin - self.l_margin - (2 * self.c_margin))

    def gety_end_page(self) -> float:
        y0 = int(self.page_break_trigger) - 1
        y1 = int(self.y) + 1
        return y0 if y1 < y0 else y1

    # adds a page break if h is too high
    def PageBreak(self, h) -> int:
        # If the height h would cause an overflow, add a new page immediately
        if (self.y + h) > self.page_break_trigger and self.accept_page_break():
            self.add_page(self.cur_orientation)
            return 1
        else:
            return 0

    # adds a link target page # and y
    def AddLinkTarget(self, y=-1, page=-1):
        self.links += [(page, y)]
        n = len(self.links) - 1
        # print "AddLinkTarget(y=",y,",page=",page,")=", n
        return n

    def _get_target_page_from_alias(self, s):
        # s= "{pageXXX}"
        if "{page" == s[:5]:
            page = int(s[5:-1])
        else:
            page = 0
        # print "_get_target_page_from_alias(%s)=" % s, page
        return page

    # def  text_direction(x, y, txt, angle, font_angle=0):
    #   font_angle +=90+txt_angle
    #   txt_angle

    # http://www.fpdf.org/en/script/script3.php
    def NbLines(self, w, txt: str) -> tuple:
        # Computes the number of lines a multi_cell  of width w will take
        if txt is not None and isinstance(txt, str):
            cw = self.current_font["cw"]

            if w == 0:
                w = self.w - self.r_margin - self.x

            wmax = (w - 2 * self.c_margin) * 1000 / self.font_size

            s = txt.replace("\r", "")

            nb = len(s)

            if nb > 0 and s[nb - 1] == "\n":
                nb -= 1

            sep = -1
            i = 0
            j = 0
            l = 0
            nl = 1
            nc = 0
            while i < nb:
                c = s[i]

                if c == "\n":
                    i += 1
                    sep = -1
                    j = i
                    l = 0
                    nl += 1
                    continue
                elif c == " ":
                    sep = i

                l += cw[c]

                if l > wmax:
                    if sep == -1:
                        if i == j:
                            i += 1
                    else:
                        i = sep + 1
                    sep = -1
                    j = i
                    l = 0
                    nl += 1
                else:
                    nc += 1
                    i += 1
        else:
            nl = 0
            nc = 0

        return (nl, nc)

    def row(self, data: list, wds: list = []):
        # Calculate the height of the row
        nb = 0
        # width calculate
        l = len(data) if len(data) > 0 else 1
        lwds = len(wds)
        if l == lwds:
            self.widths = wds
        else:
            div = self._width() / l
            for i in range(l - lwds):
                self.widths.append(div)
        # calculate row and colums
        l_row_col = (1, 1)
        for i in range(l):
            if data[i] is not None:
                # nb = max(nb, self.NbLines(self.widths[i], data[i]))
                l_row_col = max(l_row_col, self.NbLines(self.widths[i], data[i]))
        nb = l_row_col[0] if l_row_col[0] > 0 else 1
        nc = l_row_col[1]

        h = self.ln_h * nb
        if self.row_square is not None and self.row_square > h:
            h = self.row_square

        # Issue a page break first if needed
        # Generate issue when nb take a page
        self.PageBreak(h)
        # Draw the cells of the row
        for i in range(len(data)):
            w = self.widths[i]

            try:
                a = self.aligns[i]
            except Exception:
                if self.align == "L":
                    a = "L"
                else:
                    a = self.align
            try:
                b = self.bolds[i]
            except Exception:
                if self.bold == " ":
                    b = " "
                else:
                    b = "B"
            try:
                br = self.borders[i]
            except Exception:
                if self.br == 0:
                    br = 0
                else:
                    br = 1

            # Save the current position
            x = self.get_x()
            y = self.get_y()

            # Draw the border
            if br == 1:
                self.rect(x, y, w, h)
            # font
            if b == "B":
                self.set_font("", "B")
            # Print the text
            try:
                texto = str(data[i])
            except Exception:
                texto = " "
            # Vertical align
            # print('------------TEST')
            # print(data[i])
            # print(nb)
            # print(nc)
            # texto=self.vertical_align(data[i], nb, nc)
            # print(texto)
            self.multi_cell(w, self.ln_h, texto, 0, a)

            self.set_font("")
            # Put the position to the right of the cell
            self.set_xy(x + w, y)

        # Go to the next line
        self.ln(h)
        # Reset
        self.bolds = []
        self.aligns = []
        self.borders = []
        self.row_square = None

    # wrapper method for FPDF Table()
    def Table(self, tlist, w=None):
        ncols = len(tlist[0])

        if not w:
            wlist = [self._width() / ncols] * ncols
        elif self.is_string(w[0]):
            wlist = []
            for s in w:
                wlist += [self._width() * self._percent(s) / 100]

        else:
            wlist = w

        for lrow in tlist:
            self.row(lrow, wlist)

    def data_in_checktable(self, dict_data, width):
        xo = self.get_x()
        len_data = f = f_tmp = 0
        for laFila in dict_data:
            len_data += 1
            f_tmp = self.get_string_width(laFila["CDESCRI"]) + 2
            f = f_tmp if f_tmp > f else f
        rows = int(width / f) + 1
        if rows > len_data:
            rows = len_data
        f = width / rows
        i = 0
        for laFila in dict_data:
            if i == rows:
                i = 0
                self.ln()
                self.set_x(xo)
            if laFila["NOPCION"] == 1:
                self.cell(f, self.ln_h, laFila["CDESCRI"] + "     (X)", 1, 0, "L")
            else:
                self.cell(f, self.ln_h, laFila["CDESCRI"] + " ".ljust(5), 1, 0, "L")
            i += 1
        self.ln(self.ln_h + 0.2)

    def data_in_checktable_2(self, data, width):
        dict_data = data["MTABLA"]
        xo = self.get_x()
        len_data = f = f_tmp = 0
        for laFila in dict_data:
            len_data += 1
            f_tmp = self.get_string_width(laFila["CDESCRI"]) + 2
            f = f_tmp if f_tmp > f else f
        rows = int(width / f) + 1
        if rows > len_data:
            rows = len_data
        f = width / rows
        i = 0
        for idx, laFila in enumerate(dict_data):
            if i == rows:
                i = 0
                self.ln(self.ln_h + 0.2)
                self.set_x(xo)
            if data["NOPCION"] == idx:
                self.cell(f, self.ln_h, laFila["CDESCRI"] + "     (X)", 1, 0, "L")
            else:
                self.cell(f, self.ln_h, laFila["CDESCRI"] + " ".ljust(5), 1, 0, "L")
            i += 1
        self.ln(self.ln_h + 0.2)
