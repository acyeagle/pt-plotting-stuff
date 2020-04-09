
import canvas_data_getter as getter
import canvas_data_plotter as plotter
from matplotlib.backends.backend_pdf import PdfPages
from pprint import pprint

### Configurable params: ###
OUTPUT_FILE = 'test.pdf'
COLOR = None # Maybe this should be defined in the plotter?

# Only specify one (or none) of these things:
SECTIONS = ['ENGR 216 101']
PROF = None     
PT = None

### Get the section info from Canvas ###
if not SECTIONS:
    if PROF:
        SECTIONS = getter.get_prof_sections(PROF)
    elif PT:
        SECTIONS = getter.get_pt_sections(PT)
    else:
        SECTIONS = getter.get_all_sections()
else:
    SECTIONS = getter.get_sections(SECTIONS)

### Create the report for the found sections. ###
with PdfPages(OUTPUT_FILE) as pdf:
    all_data = []
    for section in SECTIONS:
        print(f'*** On section {section.name} ***')
        data = getter.get_the_data(section)
        #pprint(data)
        fig = plotter.make_figure(COLOR, data)
        pdf.savefig(fig)

    
