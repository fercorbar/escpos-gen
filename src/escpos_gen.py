import six
from math import *
from helpers.image import EscposImage
import logging
#Configuracion de logging
log = logging.getLogger('radmin_info')
console = logging.StreamHandler()
log.addHandler(console)
log.setLevel(logging.INFO)

exists_img_factor = False
img_factor = 11

class escGenerator:

    def __init__(self, paper_size="80mm"):
        self.commands = []
        if not paper_size in paper_sizes:
            paper_size="80mm"
        self.paper_size = "80mm"
        self.max_line_len = paper_sizes[paper_size]['max_line_len']
        self.lines_before_cut = 7

    def generate(self):
        allcommands = b''
        try:
            for command in self.commands:
                if isinstance(command, bytes):
                    allcommands += command
                else:
                    allcommands += bytes(command, '850')
        except Exception as e:
            pass
        return allcommands

    def reset(self):
        self.commands.append(b'\x1b\x40')

    def lf(self, times = 1):
        for _ in range(times):
            self.commands.append(b'\x0a')

    def cut_paper(self):
        """
        Inserts command to cut paper. Includes line feeds set on lines_before_cut.
        """
        self.lf(self.lines_before_cut)
        self.commands.append(b'\x1d\x56\x01')

    def tab(self):
        self.commands.append(b'\x09')

    def text_left(self):
        self.commands.append(b'\x1b\x61\x00')

    def text_center(self):
        self.commands.append(b'\x1b\x61\x01')

    def text_right(self):
        self.commands.append(b'\x1b\x61\x02')

    def text_tittle(self):
        self.commands.append(b'\x1b\x21\x38')

    def text_double(self):
        self.commands.append(b'\x1b\x21\x20')

    def text_total(self):
        self.commands.append(b'\x1b\x21\x30')

    def print_string(self, text):
        self.commands.append(b'\x1c\x2e')
        self.commands.append(b'\x1b\x74\x02')
        self.commands.append(text.encode('850'))

    def line(self, line_type = 0):
        """
        Insert command to print a line. Line types -> 0: dashed (Default), 1: double-dashed, 2: solid, 3: double-solid, 4: hatch-light, 5: hatch-normal, 6: hatch-dark, 7: hatch-solid.
        """
        types = {
            0: '-'.encode('850'),
            1: '='.encode('850'),
            2: b'\xc4',
            3: b'\xcd',
            4: b'\xb0',
            5: b'\xb1',
            6: b'\xb2',
            7: b'\xdf'
        }
        text = types.get(line_type)
        self.commands.append(b'\x1c\x2e')
        self.commands.append(b'\x1b\x74\x02')
        command = text*self.max_line_len
        self.commands.append(command)

    def open_drawer(self):
        self.commands.append(b'\x1b\x70\x00\x32\x32')

    def repeat_string(self, text, times):
        text = text.encode('850')
        text_to_print = (text * ((times/len(text))+1))[:times]
        self.commands.append(text_to_print)

    def ring_buzzer(self, rep):
        comandos = { '0': b'\x1b\x42\x00\x02', '1': b'\x1b\x42\x01\x02', '2': b'\x1b\x42\x02\x02', '3': b'\x1b\x42\x03\x02', '4': b'\x1b\x42\x04\x02', '5': b'\x1b\x42\x05\x02', '6': b'\x1b\x42\x06\x02', '7': b'\x1b\x42\x07\x02', '8': b'\x1b\x42\x08\x02', '9': b'\x1b\x42\x09\x02' }
        comando = comandos[str(rep)]
        self.commands.append(comando)

    def test(self):
        try:
            self.commands.append(b'\x1b\x70\x00\x32\x32')
            self.reset()
            self.print_string('Print test - Prueba de impresión')
            self.lf()
            self.print_string('ÁÉÍÓÚÑáéíóúñ!»«¹²³¥×@#$%^&*()-_+={}[]\/|¿?<>,.*~')
            for i in range(8):
                self.line(i)
            self.cut_paper()
            self.ring_buzzer(1)
        except Exception as e:
            return False, str(e)
        return True

    def set_table_row(self, isHeader, data, columns, style = "blank-line", separate = True, border_left = False, border_right = False, text_double = False):
        result = b''
        v = 'V'
        alignKey = 'header_align' if isHeader else 'data_align'

        rowLines = []
        for col in range(len(columns)):
            rowLines.append(int(ceil(float(len(data[col]))/float(columns[col]['width']))))
        lines = max(rowLines)

        for l in range(lines):
            # left
            if border_left: result += table_styles[style][v]
            #columns
            for col in range(len(columns)):
                textComplete = data[col]
                # text = textComplete[]
                if text_double:
                    width = columns[col]['width'] * 2
                else:
                    width = columns[col]['width']

                text = textComplete[(l*width):((l*width) + width)]
                if 'data_fill_car' in columns[col] and not isHeader:
                    if rowLines[col] == 1:
                        text = ('{:' + columns[col]['data_fill_car'] + alignments[columns[col][alignKey]] + str(columns[col]['width']) + '}').format(text)

                result += bytes(('{: '+ alignments[columns[col][alignKey]] + str(columns[col]['width']) + '}').format(text), '850')
                if not col == (len(columns)-1):
                    if separate:
                        result += table_styles[style][v]
            #right
            if border_right: result += table_styles[style][v]
            result += b'\x0a'

        
        
        return result

    def set_table_border(self, border, columns, style = "line", separate = True, border_left = False, border_right = False):
        result = b''
        h = 'H'
        if border == 'top': l, r, j = 'TL', 'TR', 'TV'
        elif border == 'bottom': l, r, j = 'BL', 'BR', 'BV'
        else: l, r, j = 'LH', 'RH', 'JO'

        if border_left: result += table_styles[style][l]
        for col in range(len(columns)):
            result += table_styles[style][h]*int(columns[col]['width'])
            if not col == (len(columns)-1):
                if separate:
                    result += table_styles[style][j]
        if border_right: result += table_styles[style][r]
        return result

    def table(self, data, options):
        self.reset()
        self.commands.append(b'\x1c\x2e')
        self.commands.append(b'\x1b\x74\x02')
        self.commands.append(b'\x1b\x33\x00')

        text_double = 'text_double' in options and options['text_double']

        if options['table_align'] == "center":
            self.text_center()
        elif options['table_align'] == "left":
            self.text_left()
        elif options['table_align'] == "right":
            self.text_right()
        if text_double:
            self.text_double()

        style = options['style']

        #set data columns width
        columns = options['columns']
        for i in range(len(columns)):
            if columns[i]['type'] == "data":
                col_max_len = 0
                for datum in data:
                    if len(str(datum[i])) > col_max_len: 
                        if text_double:
                            col_max_len = ceil(len(str(datum[i]))/2)
                        else:
                            col_max_len = len(str(datum[i]))

                if len(str(columns[i]['text'])) > col_max_len:
                    if text_double:
                        col_max_len = ceil(len(str(columns[i]['text'])) / 2)
                    else:
                        col_max_len = len(str(columns[i]['text']))
                columns[i]['width'] = col_max_len

        # set fill columns width
        colsTotalWith = 0
        fillColumnsCount = 0
        for column in columns:
            if column['type'] == "fill":
                fillColumnsCount += 1
            else:
                colsTotalWith += int(column['width'])
        if text_double:
            colFreeWidth = ceil(self.max_line_len/2) - colsTotalWith
        else:
            colFreeWidth = self.max_line_len - colsTotalWith
        if fillColumnsCount == 0:
            fillColsWith = 0
        else:
            fillColsWith = colFreeWidth
            if options['separate_cols']:
                fillColsWith = (fillColsWith - (len(columns) - 1))
            if options['border_left']: fillColsWith -= 1
            if options['border_right']: fillColsWith -= 1
            fillColsWith = floor(fillColsWith/fillColumnsCount)
        for col in range(len(columns)):
            if columns[col]['type'] == "fill": columns[col]['width'] = fillColsWith

        # top_border
        if options['border_top']:
            topBorder = self.set_table_border("top", columns, style, options['separate_cols'], options['border_left'], options['border_right'])
            self.commands.append(topBorder)
            self.lf()

        # column headers
        if options['show_headers']:
            headers=[]
            for column in columns:
                headers.append(column['text'])
            col_headers = self.set_table_row(True , headers, columns, style, options['separate_cols'], options['border_left'], options['border_right'], text_double)
            self.commands.append(col_headers)
            if options['separate_header']:
                if options['border_top']:
                    bordertype = "separator"
                else:
                    bordertype = "top"
                separator = self.set_table_border(bordertype, columns, style, options['separate_cols'], options['border_left'], options['border_right'])
                self.commands.append(separator)
                self.lf()

        # data
        if options['show_data']:
            # print(f'columns----------------{columns}')
            for i in range(len(data)):
                line = self.set_table_row(False, data[i], columns, style, options['separate_cols'], options['border_left'], options['border_right'], text_double)
                self.commands.append(line)
                if options['separate_rows']:
                    if not i == (len(data)-1):
                        separator = self.set_table_border('separator', columns, options['row_separator_style'], options['separate_cols'], options['border_left'], options['border_right'])
                        self.commands.append(separator)

        
        # border_bottom
        if options['border_bottom']:
            bottomBorder = self.set_table_border("bottom", columns, style, options['separate_cols'], options['border_left'], options['border_right'])
            self.commands.append(bottomBorder)
            self.lf()


        # items
        # tableLines = []
        # for i in range(len(data)):
        #     # calculate lines per column
        #     rowLines = []
        #     for col in range(len(columns)):
        #         rowLines.append(int(ceil(float(len(data[i][col]))/float(columns[col]['width']))))
        #     print(rowLines)
        #     tableLines.append(rowLines)

        self.commands.append(b'\x1b\x33\x3c')
        self.commands.append(b'\x1b\x02')
        self.reset()
        #self.cut_paper()

    def test(self):
        self.commands.append(b'\x1c\x2e')
        self.commands.append(b'\x1b\x74\x02')
        self.commands.append(b'\xb0'*10)
        # self.commands.append(b'\x18')
        # self.commands.append(b'\x1b\x24\x00\x00')
        # self.commands.append(b'\x1b\x5c\x00\x00')
        self.commands.append(b'\x1b\x64\x02')
        # self.reset()
        self.print_string('ABCD')
        #self.cut_paper()

    @staticmethod
    def _int_low_high(inp_number, out_bytes):
        """ Generate multiple bytes for a number: In lower and higher parts, or more parts as needed.

        :param inp_number: Input number
        :param out_bytes: The number of bytes to output (1 - 4).
        """
        max_input = (256 << (out_bytes * 8) - 1)
        if not 1 <= out_bytes <= 4:
            raise ValueError("Can only output 1-4 bytes")
        if not 0 <= inp_number <= max_input:
            raise ValueError("Number too large. Can only output up to {0} in {1} bytes".format(max_input, out_bytes))
        outp = b''
        for _ in range(0, out_bytes):
            outp += six.int2byte(inp_number % 256)
            inp_number //= 256
        return outp
    
    def print_image(self, image_size, img_source, high_density_vertical=True, high_density_horizontal=True, impl="bitImageRaster", fragment_height=3, center=True):
        global exists_img_factor
        global img_factor

        im = EscposImage(img_source, image_size, self.max_line_len)
        width = im.width
        height = im.height
        if exists_img_factor is False:
            if width == height:
                img_factor = 11
            # Only works with 200x100 or 400x200
            elif width == (height*2):
                img_factor = 10
            else:
                img_factor = 9
            exists_img_factor = True
        try:
            if image_size == 'sm':
                max_width = int((self.max_line_len * img_factor) * 0.5) 
            if image_size == 'md':
                max_width = int((self.max_line_len * img_factor) * 0.75) 
            if image_size == 'lg':
                max_width = (self.max_line_len * img_factor)
            if center:
                im.center(max_width)
        except KeyError:
            # If the printer's pixel width is not known, print anyways...
            pass
        except ValueError:
            # If the max_width cannot be converted to an int, print anyways...
            pass
        GS  = b'\x1d'
        ESC = b'\x1b'
        if im.height > fragment_height:
            fragments = im.split(fragment_height)
            for fragment in fragments:
                self.print_image(image_size, fragment,
                        high_density_vertical=high_density_vertical,
                        high_density_horizontal=high_density_horizontal,
                        impl=impl,
                        fragment_height=fragment_height)
            exists_img_factor = False
            return

        if impl == "bitImageRaster":
            # GS v 0, raster format bit image
            density_byte = (0 if high_density_horizontal else 1) + (0 if high_density_vertical else 2)
            header = GS + b"v0" + six.int2byte(density_byte) + self._int_low_high(im.width_bytes, 2) +\
                self._int_low_high(im.height, 2)
            self.commands.append(header + im.to_raster_format())

        if impl == "graphics":
            # GS ( L raster format graphics
            img_header = self._int_low_high(im.width, 2) + self._int_low_high(im.height, 2)
            tone = b'0'
            colors = b'1'
            ym = six.int2byte(1 if high_density_vertical else 2)
            xm = six.int2byte(1 if high_density_horizontal else 2)
            header = tone + xm + ym + colors + img_header
            raster_data = im.to_raster_format()
            self._image_send_graphics_data(b'0', b'p', header + raster_data)
            self._image_send_graphics_data(b'0', b'2', b'')

        if impl == "bitImageColumn":
            # ESC *, column format bit image
            density_byte = (1 if high_density_horizontal else 0) + (32 if high_density_vertical else 0)
            header = ESC + b"*" + six.int2byte(density_byte) + self._int_low_high(im.width, 2)
            outp = [ESC + b"3" + six.int2byte(16)]  # Adjust line-feed size
            for blob in im.to_column_format(high_density_vertical):
                outp.append(header + blob + b"\n")
            outp.append(ESC + b"2")  # Reset line-feed size
            self.commands.append(b''.join(outp))

    def _image_send_graphics_data(self, m, fn, data):
        GS  = b'\x1d'
        """
        Wrapper for GS ( L, to calculate and send correct data length.

        :param m: Modifier//variant for function. Usually '0'
        :param fn: Function number to use, as byte
        :param data: Data to send
        """
        header = self._int_low_high(len(data) + 2, 2)
        self.commands.append(GS + b'(L' + header + m + fn + data)
        
alignments = {
    "center": "^",
    "left": "<",
    "right": ">"
}
paper_sizes = {
    "58mm":{
        "max_line_len":32
        },
    "80mm":{
        "max_line_len":48
        }
    }

table_styles = {
    "line": {
        "TL": b'\xda',
        "TR": b'\xbf',
        "BL": b'\xc0',
        "BR": b'\xd9',
        "LH": b'\xc3',
        "RH": b'\xb4',
        "TV": b'\xc2',
        "BV": b'\xc1', 
        "JO": b'\xc5',
        "V": b'\xb3',
        "H": b'\xc4'
    },
    "dashed":{
        "TL": b'\xda',
        "TR": b'\xbf',
        "BL": b'\xc0',
        "BR": b'\xd9',
        "LH": b'\xc3',
        "RH": b'\xb4',
        "TV": b'\xc2',
        "BV": b'\xc1',
        "JO": b'\x2b',
        "V": b'\xdd',
        "H": b'\x2d'
    },
    "line-double":{
        "TL": b'\xc9',
        "TR": b'\xbb',
        "BL": b'\xc8',
        "BR": b'\xbc',
        "LH": b'\xcc',
        "RH": b'\xb9',
        "TV": b'\xcb',
        "BV": b'\xca',
        "JO": b'\xce',
        "V": b'\xba',
        "H": b'\xcd'
    },
    "shade-light":{
        "TL": b'\xb0',
        "TR": b'\xb0',
        "BL": b'\xb0',
        "BR": b'\xb0',
        "LH": b'\xb0',
        "RH": b'\xb0',
        "TV": b'\xb0',
        "BV": b'\xb0',
        "JO": b'\xb0',
        "V": b'\xb0',
        "H": b'\xb0'
    },
    "shade-medium":{
        "TL": b'\xb1',
        "TR": b'\xb1',
        "BL": b'\xb1',
        "BR": b'\xb1',
        "LH": b'\xb1',
        "RH": b'\xb1',
        "TV": b'\xb1',
        "BV": b'\xb1',
        "JO": b'\xb1',
        "V": b'\xb1',
        "H": b'\xb1'
    },
    "shade-dark":{
        "TL": b'\xb2',
        "TR": b'\xb2',
        "BL": b'\xb2',
        "BR": b'\xb2',
        "LH": b'\xb2',
        "RH": b'\xb2',
        "TV": b'\xb2',
        "BV": b'\xb2',
        "JO": b'\xb2',
        "V": b'\xb2',
        "H": b'\xb2'
    },
    "solid":{
        "TL": b'\xdb',
        "TR": b'\xdb',
        "BL": b'\xdb',
        "BR": b'\xdb',
        "LH": b'\xdb',
        "RH": b'\xdb',
        "TV": b'\xdb',
        "BV": b'\xdb',
        "JO": b'\xdb',
        "V": b'\xdb',
        "H": b'\xdb'
    },
    "blank":{
        "TL": b'\x20',
        "TR": b'\x20',
        "BL": b'\x20',
        "BR": b'\x20',
        "LH": b'\x20',
        "RH": b'\x20',
        "TV": b'\x20',
        "BV": b'\x20',
        "JO": b'\x20',
        "V": b'\x20',
        "H": b'\x20'
    },
    "blank-line":{
        "TL": b'\x20',
        "TR": b'\x20',
        "BL": b'\x20',
        "BR": b'\x20',
        "LH": b'\x20',
        "RH": b'\x20',
        "TV": b'\xc4',
        "BV": b'\xc4', 
        "JO": b'\xc4',
        "V": b'\x20',
        "H": b'\xc4'
    },
    "blank-dashed":{
        "TL": b'\x20',
        "TR": b'\x20',
        "BL": b'\x20',
        "BR": b'\x20',
        "LH": b'\x20',
        "RH": b'\x20',
        "TV": b'\x2d',
        "BV": b'\x2d', 
        "JO": b'\x2d',
        "V": b'\x20',
        "H": b'\x2d'
    },
    "asterisk":{
        "TL": b'\x2a',
        "TR": b'\x2a',
        "BL": b'\x2a',
        "BR": b'\x2a',
        "LH": b'\x2a',
        "RH": b'\x2a',
        "TV": b'\x2a',
        "BV": b'\x2a', 
        "JO": b'\x2a',
        "V": b'\x2a',
        "H": b'\x2a'
    }
}

options = {
    "columns":[
        {
            "text": "Cant",
            "type": "data",
            "header_align": "left",
            "data_align": "left"
        },
        {
            "text": "Descripción",
            "type": "fixed",
            "width": 13,
            "header_align": "center",
            "data_align": "left"
        },
        {
            "text": "Precio",
            "type": "data",
            "width": 8,
            "header_align": "center",
            "data_align": "right"
        }
    ]
}