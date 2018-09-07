from gluon.contrib.pyfpdf import FPDF, HTMLMixin
class Report(FPDF, HTMLMixin):
    def header(self):
        import os
        logo = os.path.join(request.folder, 'static', 'images', 'Logo_MF.png')
        self.image(logo, 10, 8, 35)
        self.set_font('Arial','',12)
        self.cell(35) # padding
        self.cell(120, 10, 'M&F Engenharia e Construções'.decode('UTF-8').encode('cp1252'), 0, 0, 'C')
        self.set_font('Arial', '', 10)
        self.cell(35,10,response.pedido.decode('UTF-8').encode('cp1252'),0,0,'R')
        self.ln(5)
        self.cell(35) # padding
        self.cell(120, 10, 'Av: Francisco Prestes Maia, 995 - Centro - Amparo-SP'.decode('UTF-8').encode('cp1252'), 0, 0, 'C')
        self.cell(35, 10, response.dtpedido, 0, 0, 'R')
        self.ln(5)
        self.cell(35) # padding
        self.cell(120, 10, '(19) 3817-2349 - email: mfengenharia.amparo@gmail.com'.decode('UTF-8').encode('cp1252'), 0, 0, 'C')
        pagina = "       Página: %s/%s" %('{:0>3}'.format(self.page_no()), '{:0>6}'.format(self.alias_nb_pages()))
        self.cell(35, 10, pagina.decode('UTF-8').encode('cp1252'), 0, 0,'L')
        self.ln(15)
        self.line(10, 32, 200, 32)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial','I',8)
        txt = 'Av: Francisco Prestes Maia, 995 - Centro - Amparo-SP - Fone:(19)38172349 - Email: mfengenharia.amparo@gmail.com'
        self.cell(190,10,txt,0,0,'C')

    def texto(self,w=2,texto='',margem=10,fonte='Times',size=10,tipo=''):
        self.set_x(margem)
        self.set_font(fonte, tipo, size)
        #self.write(w, texto.decode('UTF-8').encode('cp1252'))