import time
import os

def write_qr(qr_data, module_size, file_dir):
    file_start = '''
%!PS-Adobe-3.0 EPSF-3.0
%%Creator: PyQR
%%Title: QR.eps
%%CreationDate: 20240610
%%Pages: 1
%%BoundingBox: 0 0 612 792
%%Document-Fonts: Helvetica
%%LanguageLevel: 3
%%EndComments
%%BeginProlog
%%EndProlog
%%Page: 1 1
save'''
    add_module = f'''
/module_size {module_size} def\n'''
    add_bits = '''
/on_bit {gsave 0 0 0 1 setcmykcolor newpath 0 0 moveto 0 module_size lineto module_size module_size lineto module_size 0 lineto 0 0 lineto fill stroke grestore } bind def
/off_bit {gsave 0 0 0 0 setcmykcolor newpath 0 0 moveto 0 module_size lineto module_size module_size lineto module_size 0 lineto 0 0 lineto fill stroke grestore } bind def
/qr_code {
    gsave
'''

    file_end = '''
    grestore
} bind def
20 20 translate qr_code
restore showpage
%
% End of page
%
%%Trailer
%%EOF'''


    if file_dir is None:
        filename = f'qr_{time.time()}.ps'
        qr_file = open(filename, 'x')
    else:
        try:
            filename = file_dir
            qr_file = open(filename, 'x')
        except:
            raise ValueError(f"{file_dir} Does Not Exist")

    qr_file.write(file_start)
    qr_file.write(add_module)
    qr_file.write(add_bits)
    state = 'off_bit'
    for coord, state in qr_data:
        x, y = coord
        if state == 1:
            state = 'on_bit'
        else:
            state = 'off_bit'
        qr_file.write(f'''
    gsave {x*module_size} {y*module_size} translate {state} grestore''')
    qr_file.write(file_end)
    qr_file.close()

    os.startfile(filename)

def get_ps_string(qr_data, module_size):
    full_ps_string = ''
    file_start = '''
/qr_code {
    gsave\n'''
    add_module = f'''
    /module_size {module_size} def\n'''
    add_bits = '''
    /on_bit {gsave 0 0 0 1 setcmykcolor newpath 0 0 moveto 0 module_size lineto module_size module_size lineto module_size 0 lineto 0 0 lineto fill stroke grestore } bind def
    /off_bit {gsave 0 0 0 0 setcmykcolor newpath 0 0 moveto 0 module_size lineto module_size module_size lineto module_size 0 lineto 0 0 lineto fill stroke grestore } bind def
    /qr_data {
        gsave
    '''

    file_end = '''
        grestore
    } bind def
    20 20 translate qr_data
    grestore
} bind def
'''

    full_ps_string += file_start
    full_ps_string += add_module
    full_ps_string += add_bits

    state = 'off_bit'
    for coord, state in qr_data:
        x, y = coord
        if state == 1:
            state = 'on_bit'
        else:
            state = 'off_bit'
        full_ps_string += f'''
        gsave {x*module_size} {y*module_size} translate {state} grestore'''

    full_ps_string += file_end

    return full_ps_string
