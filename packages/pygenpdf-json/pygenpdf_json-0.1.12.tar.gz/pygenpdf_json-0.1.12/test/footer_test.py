import os
from pygenpdf import *

def main():
    doc = Document()
    dir_now = os.path.dirname(os.path.abspath(__file__))
    doc.set_default_font(dir_now + "/liberation", "LiberationSans")
    doc.set_title("report genpdf")
    doc.set_paper_size(Size().A4())
    
    ## only three paragraphs maximum
    doc.set_head_page([Paragraph("una linea head").aligned(Alignment.RIGHT).styled(Style().with_font_size(8)),
                       Paragraph("otra linea head").aligned(Alignment.RIGHT).styled(Style().with_font_size(9)),
                       Paragraph("y la otra linea head").aligned(Alignment.RIGHT).styled(Style().with_font_size(7))])
    
    doc.set_head_page_count(Paragraph("Pagina").aligned(Alignment.CENTER).styled(Style().bold().with_font_size(8)))
    
    #only three paragraphs maximum
    doc.set_footer_page([Paragraph("una linea footer").aligned(Alignment.LEFT).styled(Style().with_font_size(20).with_color(Color().rgb(230,0,0))),
                       Paragraph("otra linea footer").aligned(Alignment.LEFT).styled(Style().with_font_size(9).with_color(Color().rgb(230,0,0))),
                       Paragraph("y la otra linea footer").aligned(Alignment.LEFT).styled(Style().with_font_size(7).with_color(Color().rgb(230,0,0)))])
    
    
    doc.set_margins(Margins().trbl(7,10,10,10))
    doc.set_line_spacing(1.0)                         
            
    for line in range(250):
        doc.push(Paragraph("line " + str(line)))
    doc.push(PageBreak())
    
    doc.render_json_file(dir_now + "/footer_test.pdf")
    
    
if __name__=="__main__":
    main()
