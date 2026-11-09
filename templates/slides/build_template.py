"""Build the DC Lab template or recolour an editable code textbox. No network needed."""
from pathlib import Path
from copy import deepcopy
from types import SimpleNamespace
from zipfile import ZipFile, ZIP_DEFLATED
import argparse
import sys

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.oxml.xmlchemy import OxmlElement
from pptx.parts.slide import SlideLayoutPart
from pptx.opc.packuri import PackURI
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.shapes.shapetree import SlideShapes
try:
    from pygments import lex
except ImportError:
    # Also support the system Pygments package in the existing local slide venv.
    sys.path.append('/usr/lib/python3/dist-packages')
    from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.token import Token

ROOT = Path(__file__).resolve().parent
BG = 'F5F8FF'
INK = '21283C'
BLUE = '0C0A9E'
MUTED = '57627B'
RULE = 'CCD4E4'
CYAN = '187F93'
PINK = 'B43177'
NAVY = '1A1B26'
PALE = 'C0CAF5'
MONO = 'Noto Sans Mono'
SANS = 'Ubuntu Sans'
W, H = 13.333333, 7.5


def rgb(h):
    return RGBColor.from_string(h)


def rect(s, x, y, w, h, fill=None, stroke=None, name='Panel'):
    sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.name = name
    if fill:
        sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
    else:
        sh.fill.background()
    if stroke:
        sh.line.color.rgb = rgb(stroke); sh.line.width = Pt(.8)
    else:
        sh.line.fill.background()
    sh._element.spPr.append(OxmlElement('a:effectLst'))
    for ref in sh._element.xpath('./p:style/a:effectRef'):
        ref.set('idx', '0')
    return sh


def txt(s, x, y, w, h, value, size=20, color=INK, bold=False, font=SANS, name='Text'):
    sh = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    sh.name = name
    tf = sh.text_frame
    tf.word_wrap = True; tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, line in enumerate(value.split('\n')):
        p = tf.paragraphs[0] if not i else tf.add_paragraph()
        p.text = line; p.font.name = font; p.font.size = Pt(size)
        p.font.bold = bold; p.font.color.rgb = rgb(color)
        p.space_after = Pt(7); p.line_spacing = Pt(size * 1.22)
        p.alignment = PP_ALIGN.LEFT
        pr = p._p.get_or_add_pPr(); pr.set('marL', '0'); pr.set('indent', '0')
        pr.append(OxmlElement('a:buNone'))
    return sh


def line(s, x1, y1, x2, y2, color=RULE, width=1, arrow=False, ends=None):
    sh = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    sh.line.color.rgb = rgb(color); sh.line.width = Pt(width)
    sh._element.spPr.append(OxmlElement('a:effectLst'))
    for ref in sh._element.xpath('./p:style/a:effectRef'):
        ref.set('idx', '0')
    if arrow:
        tail = OxmlElement('a:tailEnd'); tail.set('type', 'triangle')
        sh.line._get_or_add_ln().append(tail)
    if ends:
        sh.begin_connect(ends[0], 3); sh.end_connect(ends[1], 1)
    return sh


def ph(s, x, y, w, h, value, idx, kind='body', size=20, color=INK, font=SANS, bold=False):
    sh = txt(s, x, y, w, h, value, size, color, bold, font, f'{kind.upper()} | {value.split(chr(10))[0]}')
    nv = sh._element.find('.//{http://schemas.openxmlformats.org/presentationml/2006/main}nvPr')
    node = OxmlElement('p:ph'); node.set('type', kind); node.set('idx', str(idx)); nv.append(node)
    if kind == 'pic':
        sh.fill.solid(); sh.fill.fore_color.rgb = rgb('EAF0FA')
        sh.line.color.rgb = rgb('9AAAC4'); sh.line.width = Pt(1)
        sh.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        sh.text_frame.margin_left = sh.text_frame.margin_right = Inches(.25)
        sh.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    return sh


def picture(s, x, y, w, h, label='Insert picture', idx=10):
    return ph(s, x, y, w, h, label, idx, 'pic', 15, MUTED, MONO)


def logos(s, x=10.42, y=.37):
    # Original artwork, with aspect ratio preserved on a white backing.
    from PIL import Image
    for filename, dx, maxw in [('itc.jpg', 0, .48), ('dclab.jpg', .65, 1.48)]:
        p = ROOT / 'assets' / filename
        with Image.open(p) as im:
            a = im.width / im.height
        height = min(.44, maxw / a); width = height * a
        rect(s, x + dx - .04, y - .04, width + .08, .52, 'FFFFFF', name='Logo backing')
        sh = s.shapes.add_picture(str(p), Inches(x + dx), Inches(y + (.44-height)/2), width=Inches(width), height=Inches(height))
        sh.name = 'BRAND | ' + filename


def footer(s, dark=False):
    c = '828BB8' if dark else MUTED
    line(s, .58, 7.03, 12.75, 7.03, '343B54' if dark else RULE, .65)
    txt(s, .6, 7.14, 6.2, .19, 'DC LAB / CRASH COURSE', 9, c, font=MONO)
    txt(s, 8.15, 7.14, 4.55, .19, '>_ terminal gremlin (c-lydia ^_^)', 8.5, c, font=MONO)


def heading(s, label, title, dark=False):
    txt(s, .6, .4, 9.4, .28, label, 10, '48CAE4' if dark else CYAN, font=MONO)
    ph(s, .6, .99, 12.05, .95, title, 0, 'title', 29, PALE if dark else BLUE, MONO, True)
    line(s, .6, 1.96, 12.73, 1.96, '343B54' if dark else RULE)
    logos(s); footer(s, dark)


def note(s, value):
    s.notes_slide.notes_text_frame.text = value


def code_colour(token):
    if token in Token.Comment: return '9AA6CF'
    if token in Token.Keyword: return 'BB9AF7'
    if token in Token.Literal.String: return '9ECE6A'
    if token in Token.Literal.Number: return 'FF9E64'
    if token in Token.Name.Function: return '7AA2F7'
    if token in Token.Name.Builtin or token in Token.Keyword.Type: return '48CAE4'
    if token in Token.Operator: return '7DCFFF'
    return 'C0CAF5'


def highlight(sh, source, language='cpp', size=17):
    """Real editable text runs, never an image of code."""
    source = source.expandtabs(2).rstrip('\n')
    maxchars = int((sh.width / 914400 - .42) * 72 / (size * .61))
    maxlines = int((sh.height / 914400 - .32) * 72 / (size * 1.28))
    lines = source.splitlines()
    if len(lines) > maxlines or max(map(len, lines), default=0) > maxchars:
        raise ValueError(f'Code exceeds this box: use at most {maxlines} lines and {maxchars} columns at {size} pt, or use a wider layout.')
    tf = sh.text_frame; tf.clear(); tf.word_wrap = False
    tf.margin_left = tf.margin_right = Inches(.21)
    tf.margin_top = tf.margin_bottom = Inches(.16)
    tf.auto_size = MSO_AUTO_SIZE.NONE
    p = tf.paragraphs[0]
    def setup(p):
        p.font.name = MONO; p.font.size = Pt(size); p.font.color.rgb = rgb(PALE)
        p.space_after = Pt(0); p.space_before = Pt(0); p.line_spacing = Pt(size * 1.28)
        p.alignment = PP_ALIGN.LEFT
        pr = p._p.get_or_add_pPr(); pr.set('marL', '0'); pr.set('indent', '0')
        pr.append(OxmlElement('a:buNone'))
    setup(p)
    tokens = list(lex(source, get_lexer_by_name(language, stripnl=False, ensurenl=False)))
    for token, value in tokens:
        for i, chunk in enumerate(value.split('\n')):
            if i:
                p = tf.add_paragraph(); setup(p)
            if chunk:
                r = p.add_run(); r.text = chunk; r.font.name = MONO
                r.font.size = Pt(size); r.font.color.rgb = rgb(code_colour(token))
    return sh


def codebox(s, x, y, w, h, source, language='cpp', size=17, name='CODE'):
    rect(s, x, y, w, h, '16161E', '343B54', name='Code surface')
    sh = txt(s, x, y, w, h, '', size, PALE, font=MONO, name=name)
    return highlight(sh, source, language, size)


def build():
    p = Presentation(); p.slide_width = Inches(W); p.slide_height = Inches(H)
    master = p.slide_master
    blank = deepcopy(p.slide_layouts[6]._element)
    for child in list(blank.spTree):
        if child.tag.rsplit('}', 1)[-1] in {'sp', 'pic', 'graphicFrame', 'cxnSp', 'grpSp'}:
            blank.spTree.remove(child)
    # Drop unused stock layouts so New Slide shows only this course's layouts.
    for item in list(master._element.sldLayoutIdLst):
        master.part.drop_rel(item.rId); master._element.sldLayoutIdLst.remove(item)
    for sh in list(master.shapes):
        sh._element.getparent().remove(sh._element)
    theme = master.part.part_related_by(RT.THEME)
    from lxml import etree
    t = etree.fromstring(theme.blob)
    ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
    for path, font in [('majorFont', MONO), ('minorFont', SANS)]:
        t.find(f'.//a:{path}/a:latin', ns).set('typeface', font)
    for key, color in [('dk1', INK), ('lt1', BG), ('dk2', NAVY), ('lt2', 'EAF0FA'), ('accent1', BLUE), ('accent2', CYAN), ('accent3', PINK), ('accent4', '7AA2F7'), ('accent5', '9ECE6A'), ('accent6', 'E0AF68')]:
        el = t.find(f'.//a:clrScheme/a:{key}', ns)
        for ch in list(el): el.remove(ch)
        c = etree.SubElement(el, '{'+ns['a']+'}srgbClr'); c.set('val', color)
    theme._blob = etree.tostring(t, xml_declaration=True, encoding='UTF-8', standalone=True)

    layouts = []
    def layout(name, dark=False):
        index = len(layouts) + 1
        el = deepcopy(blank); el.cSld.set('name', f'{index:02} / {name}')
        el.set('type', 'cust'); el.set('preserve', '1')
        part = SlideLayoutPart(PackURI(f'/ppt/slideLayouts/slideLayout{index}.xml'), 'application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml', p.part.package, el)
        part.relate_to(master.part, RT.SLIDE_MASTER)
        rid = master.part.relate_to(part, RT.SLIDE_LAYOUT)
        lid = OxmlElement('p:sldLayoutId'); lid.set('id', str(2147483648 + index)); lid.set('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id', rid)
        master._element.sldLayoutIdLst.append(lid)
        lay = part.slide_layout
        bg = el.cSld.get_or_add_bg(); bgpr = bg.get_or_add_bgPr()
        solid = OxmlElement('a:solidFill'); c = OxmlElement('a:srgbClr'); c.set('val', NAVY if dark else BG); solid.append(c); bgpr.append(solid)
        proxy = SimpleNamespace(shapes=SlideShapes(el.spTree, lay))
        layouts.append(lay)
        return proxy

    def instance(lay, instructions):
        s = p.slides.add_slide(layouts[-1])
        # Keep native placeholder XML and useful example text/styles on gallery slides.
        for sh in list(s.shapes):
            sh._element.getparent().remove(sh._element)
        for sh in lay.shapes:
            if sh.is_placeholder:
                s.shapes._spTree.insert_element_before(deepcopy(sh._element), 'p:extLst')
        note(s, instructions)
        return s

    s = layout('Cover / hero picture')
    logos(s, .65, .47); footer(s)
    txt(s, .65, 1.55, 7, .3, 'DC LAB / ELECTRONICS + CONTROL', 11, CYAN, font=MONO)
    ph(s, .65, 2.12, 6.5, 2.1, '[Crash course\ntitle goes here]', 0, 'title', 37, BLUE, MONO, True)
    ph(s, .67, 4.52, 5.8, .9, '[A practical question this session answers.]', 1, size=21)
    ph(s, .67, 5.95, 5.7, .45, '[Session 01]  /  [date]  /  [duration]', 2, size=12, color=MUTED, font=MONO)
    picture(s, 7.6, 1.58, 5.05, 4.9, 'ROBOT / BENCH / HARDWARE\nInsert a real photograph')
    line(s, 7.34, 1.58, 7.34, 6.48, PINK, 2)
    instance(s, 'START HERE. Duplicate the slide you need, or choose Home > New Slide > a DC Lab layout. Replace bracketed text. Use the picture placeholder icon to insert your own photo; crop to fill or fit as needed. Change logos in View > Slide Master (LibreOffice: View > Master Slide). All logos are original unmodified artwork. Titles use Noto Sans Mono, body text Ubuntu Sans; install these or substitute your preferred fonts consistently. 16:9 format.')

    s = layout('Session map')
    heading(s, '00 / BEFORE WE TOUCH THE HARDWARE', 'Today, we will [build / measure / debug]')
    for i,(verb,desc) in enumerate([('Understand', '[The one idea learners need]'),('Trace', '[Follow the signal or data path]'),('Build', '[The thing learners will make]'),('Verify', '[A measurement that proves it works]')]):
        y = 2.25 + i * 1.03
        txt(s, .65, y, .65, .5, f'{i+1:02}', 25, BLUE, True, MONO)
        ph(s, 1.6, y, 3, .5, verb, 2+i*2, size=22, bold=True)
        ph(s, 5, y+.02, 7.3, .6, desc, 3+i*2, size=20, color=MUTED)
        line(s, 1.6, y+.78, 12.65, y+.78)
    instance(s, 'Use four actions with visible outcomes. Replace the verbs if your session has a different rhythm. Keep detail in speaker notes.')

    s = layout('Chapter / one question', True)
    footer(s, True)
    ph(s, .68, .65, 8, .4, '01 / [CHAPTER NAME]', 1, size=13, color='48CAE4', font=MONO)
    txt(s, .68, 1.7, 2, 1.2, '>_', 69, '48CAE4', font=MONO)
    ph(s, .68, 3.1, 11.6, 1.55, '[What changes when\nwe remove delay()?]', 0, 'title', 36, PALE, MONO, True)
    ph(s, .72, 5.6, 10.5, .7, '[Ask for a prediction before showing the answer.]', 2, size=21, color='A9B1D6')
    instance(s, 'Use the chapter title as a question. Pause for predictions. This dark transition is also useful before a live demo.')

    s = layout('Concept + picture')
    heading(s, '01 / CONCEPT', '[Name the thing. Explain what it does.]')
    ph(s, .67, 2.38, 4.35, .8, '[One-sentence mental model]', 1, size=25, bold=True)
    ph(s, .67, 3.55, 4.35, 1.7, '[What goes in?]\n[What changes?]\n[What comes out?]', 2, size=21)
    ph(s, .67, 5.85, 4.35, .55, '[One important constraint]', 3, size=17, color=PINK)
    picture(s, 5.55, 2.3, 7.1, 3.98)
    ph(s, 5.55, 6.43, 7.1, .32, '[Figure / source / what to notice]', 4, size=12, color=MUTED)
    instance(s, 'Use the photo or diagram as the evidence. The left column should explain how to read it. Picture space is approximately 16:9. Keep the source in the caption or notes.')

    s = layout('Large figure + caption')
    heading(s, '02 / LOOK CLOSELY', '[Give the viewer a reason to look]')
    picture(s, .66, 2.22, 12, 4.08, 'SCHEMATIC / DIAGRAM / SCREENSHOT\nInsert figure here')
    ph(s, .67, 6.47, 11.9, .34, '[Figure 01]  [What this figure demonstrates]  /  [source]', 1, size=13, color=MUTED)
    instance(s, 'Best for circuit diagrams, timing plots, architecture exports and screenshots. Use Fit rather than Fill when cropping would hide labels. Prefer the editable architecture layout when creating a new diagram.')

    s = layout('Two pictures / compare')
    heading(s, '03 / COMPARE', '[What changed between these two?]')
    ph(s, .67, 2.2, 5.7, .5, '[A / before]', 1, size=19, color=BLUE, bold=True)
    ph(s, 6.95, 2.2, 5.7, .5, '[B / after]', 2, size=19, color=BLUE, bold=True)
    picture(s, .67, 2.91, 5.7, 3.2, 'BEFORE / INPUT', 10)
    picture(s, 6.95, 2.91, 5.7, 3.2, 'AFTER / OUTPUT', 11)
    ph(s, .67, 6.33, 5.7, .48, '[What to notice]', 3, size=16, color=MUTED)
    ph(s, 6.95, 6.33, 5.7, .48, '[What to notice]', 4, size=16, color=MUTED)
    instance(s, 'Two independent picture placeholders. Use identical crops/scales for comparisons. Suitable for oscilloscope captures, wiring changes or debug output.')

    s = layout('Code + explanation', True)
    heading(s, '04 / READ THE CODE', '[One small idea in code]', True)
    rect(s, .65, 2.35, 8.15, 4.22, '16161E', '343B54')
    txt(s, .85, 2.47, 7.5, .3, 'C++ / timing.cpp', 11, '48CAE4', font=MONO)
    ph(s, 9.18, 2.55, 3.43, .8, '[Read it in this order]', 1, size=22, color=PALE, bold=True)
    ph(s, 9.18, 3.55, 3.43, 2.4, '01  [Read the time]\n02  [Check elapsed time]\n03  [Do a short task]', 2, size=18, color='A9B1D6')
    slide = instance(s, 'CODE is editable text, with syntax colours stored as rich-text runs. PowerPoint/LibreOffice do not automatically recolour new code. Replace text normally, or run build_template.py --highlight to refresh colours. Duplicate this populated slide to retain the code; a new slide from this layout provides the surrounding structure. Sample illustrates relative reset, not a drift-free scheduler. read_sensor and poll_serial are application-defined functions, not a complete firmware program.')
    codebox(slide, .78, 2.85, 7.9, 3.65, (ROOT/'code_samples/timing.cpp').read_text(), size=15)

    s = layout('Code / wide', True)
    heading(s, '05 / WALK THROUGH IT', '[A full-width code walkthrough]', True)
    rect(s, .65, 2.3, 12.02, 3.88, '16161E', '343B54')
    ph(s, .86, 6.42, 11.7, .4, '[Ask: what runs next, and why?]', 1, size=18, color='48CAE4')
    slide = instance(s, 'Full-width editable code. Duplicate this slide and use the syntax-colouring helper for a longer snippet. The same helper accepts cpp, c, python, bash, json, yaml and other Pygments language aliases. Sample is illustrative pseudocode in C++ syntax, not complete firmware.')
    codebox(slide, .8, 2.48, 11.72, 3.5, '// Keep each task short enough to return promptly.\nvoid loop() {\n  const uint32_t now = millis();\n  update_inputs(now);\n  update_control(now);\n  update_outputs(now);\n  service_telemetry(now);\n}', size=19)

    s = layout('Editable signal path')
    heading(s, '06 / FOLLOW THE SIGNAL', '[Trace the path from input to output]')
    ph(s, .67, 2.23, 11.9, .55, '[Label every arrow with what actually crosses the boundary.]', 1, size=19, color=MUTED)
    ph(s, .67, 6.4, 11.9, .4, '[Takeaway: where is the interface most likely to fail?]', 2, size=18, color=PINK)
    slide = instance(s, 'All nodes, labels and connectors on this slide are native editable shapes. Connectors are attached to nodes, so endpoints track moved nodes. Select individual parts in the Selection Pane. Copy these parts onto another slide or duplicate the whole slide. This is a generic logical path, not a wiring schematic.')
    nodes=[]
    for x,title,sub in [( .75,'INPUT','[sensor / command]'),(4.88,'COMPUTE','[state / control]'),(9.02,'OUTPUT','[driver / actuator]')]:
        sh=rect(slide,x,3.45,3.55,1.12,'FFFFFF',BLUE,name='NODE | '+title); nodes.append(sh)
        sh.text_frame.text=title; sh.text_frame.vertical_anchor=MSO_ANCHOR.MIDDLE
        q=sh.text_frame.paragraphs[0]; q.alignment=PP_ALIGN.CENTER; q.font.name=MONO;q.font.size=Pt(22);q.font.bold=True;q.font.color.rgb=rgb(BLUE)
        txt(slide,x,4.84,3.55,.45,sub,15,MUTED,font=MONO)
    line(slide,4.3,4.01,4.88,4.01,CYAN,2,True,(nodes[0],nodes[1]))
    line(slide,8.43,4.01,9.02,4.01,PINK,2,True,(nodes[1],nodes[2]))
    txt(slide,3.72,3.01,1.7,.3,'[data]',12,CYAN,font=MONO)
    txt(slide,8.08,3.01,1.7,.3,'[command]',12,PINK,font=MONO)

    s = layout('Equation + visual')
    heading(s, '07 / MAKE THE MATH PHYSICAL', '[What does the equation predict?]')
    rect(s, .66, 2.35, 5.1, 2.1, 'EAF0FA')
    ph(s, .92, 2.95, 4.6, .9, 'D = t_on / T', 1, size=31, color=BLUE, font=MONO, bold=True)
    ph(s, .72, 4.83, 4.9, 1.45, 'D      [duty ratio]\nt_on   [high time]\nT      [period]', 2, size=17, color=INK, font=MONO)
    picture(s, 6.22, 2.36, 6.44, 3.61, 'WAVEFORM / GEOMETRY / PHYSICAL MODEL')
    ph(s, 6.23, 6.2, 6.44, .52, '[State assumptions and units.]', 3, size=17, color=MUTED)
    instance(s, 'Simple equation is editable text. For fractions, matrices and advanced notation, replace it with Insert > Equation in PowerPoint or Insert > Object > Formula in LibreOffice. Keep variable definitions and units visible.')

    s = layout('Measured data / chart')
    heading(s, '08 / CHECK THE MEASUREMENT', '[Does the measurement match the prediction?]')
    ph(s, 9.18, 2.45, 3.3, .7, '[Read the trend]', 1, size=23, bold=True)
    ph(s, 9.18, 3.5, 3.3, 2.3, '[Expected behaviour]\n[Observed deviation]\n[Likely cause]', 2, size=19)
    ph(s, .68, 6.49, 11.9, .3, 'ILLUSTRATIVE DATA / replace with your own measurements', 3, size=12, color=PINK, font=MONO)
    slide = instance(s, 'Chart is a native PowerPoint scatter chart with an embedded editable workbook. Right-click > Edit Data to replace values. LibreOffice can edit chart data too. This slide contains deliberately illustrative data, not real experiment results.')
    from pptx.chart.data import XyChartData
    from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_MARKER_STYLE
    data=XyChartData()
    for name,ys in [('Expected',[0,.825,1.65,2.475,3.3]),('Measured (example)',[.02,.79,1.61,2.42,3.22])]:
        series=data.add_series(name)
        for x,y in zip([0,25,50,75,100],ys): series.add_data_point(x,y)
    chart=slide.shapes.add_chart(XL_CHART_TYPE.XY_SCATTER_LINES, Inches(.7), Inches(2.3), Inches(8), Inches(4),data).chart
    chart.has_legend=True;chart.legend.position=XL_LEGEND_POSITION.BOTTOM;chart.legend.font.name=SANS;chart.legend.font.size=Pt(12)
    for axis,title in [(chart.category_axis,'Duty cycle (%)'),(chart.value_axis,'Average voltage (V)')]:
        axis.has_title=True;axis.axis_title.text_frame.text=title
        axis.axis_title.text_frame.paragraphs[0].font.size=Pt(13)
        axis.tick_labels.font.size=Pt(12);axis.tick_labels.font.name=SANS
    chart.category_axis.minimum_scale=0;chart.category_axis.maximum_scale=100
    chart.value_axis.minimum_scale=0;chart.value_axis.maximum_scale=3.5
    for series,c in zip(chart.series,[CYAN,PINK]):
        series.format.line.color.rgb=rgb(c);series.format.line.width=Pt(2)
        series.marker.style=XL_MARKER_STYLE.CIRCLE;series.marker.size=6
        series.marker.format.fill.solid();series.marker.format.fill.fore_color.rgb=rgb(c)
        series.marker.format.line.color.rgb=rgb(c)

    s = layout('Hardware + callouts')
    heading(s, '09 / AT THE BENCH', '[Orient the board before connecting it]')
    picture(s,.67,2.3,7.35,4.12,'BOARD / WIRING / BENCH PHOTO')
    for i in range(3):
        y=2.4+i*1.36
        txt(s,8.6,y,.5,.5,f'{i+1:02}',23,PINK,True,MONO)
        ph(s,9.25,y,3.35,.46,f'[Connection {i+1}]',1+i*2,size=20,bold=True)
        ph(s,9.25,y+.56,3.35,.62,'[Pin / voltage / direction]',2+i*2,size=16,color=MUTED)
    slide=instance(s,'Insert a photo. Move the three numbered markers onto the relevant hardware features. They are ordinary editable shapes, separate from the picture placeholder. Use one clear connection per callout. Validate actual wiring against your hardware documentation.')
    for i in range(3):
        sh=slide.shapes.add_shape(MSO_SHAPE.OVAL,Inches(1.05+i*2.25),Inches(4.2),Inches(.45),Inches(.45))
        sh.name=f'CALLOUT | move marker {i+1}';sh.fill.solid();sh.fill.fore_color.rgb=rgb(PINK);sh.line.fill.background()
        sh.text_frame.text=str(i+1);sh.text_frame.margin_top=0;sh.text_frame.margin_bottom=0;sh.text_frame.vertical_anchor=MSO_ANCHOR.MIDDLE
        q=sh.text_frame.paragraphs[0];q.alignment=PP_ALIGN.CENTER;q.font.name=MONO;q.font.size=Pt(16);q.font.color.rgb=rgb('FFFFFF')

    s=layout('Lab / steps + done condition')
    heading(s,'10 / YOUR TURN','[Build a small thing. Prove it works.]')
    for i,v in enumerate(['[Connect / configure]','[Change one variable]','[Measure and record]']):
        y=2.5+i*1.12;txt(s,.7,y,.55,.55,f'{i+1:02}',25,BLUE,True,MONO)
        ph(s,1.6,y,6.4,.68,v,i+1,size=23)
        line(s,1.6,y+.83,8.2,y+.83)
    rect(s,8.75,2.3,3.9,4.15,'EAF0FA')
    txt(s,9.05,2.62,3.3,.4,'DONE WHEN',13,CYAN,True,MONO)
    ph(s,9.05,3.35,3.25,1.45,'[A visible result or measurable pass condition]',4,size=23,bold=True)
    ph(s,9.05,5.35,3.25,.65,'[Timebox: 10 min]',5,size=16,color=MUTED,font=MONO)
    instance(s,'Write the done condition first. It should be observable, such as a waveform, reading, test result or robot motion. Avoid more than three steps. Add preparation details in the notes.')

    s=layout('Debug / symptom to test')
    heading(s,'11 / DEBUGGING','[Start with evidence, then change one thing]')
    for x,w,v in [(.7,3.2,'SYMPTOM'),(4.1,4,'CHECK FIRST'),(8.5,4.1,'EXPECTED EVIDENCE')]:
        txt(s,x,2.38,w,.4,v,12,CYAN,True,MONO)
    for i in range(3):
        y=3.1+i*1.08
        for j,(x,w,v) in enumerate([(.7,3.1,'[What you observe]'),(4.1,3.9,'[A specific probe or test]'),(8.5,4.1,'[What a healthy result shows]')]):
            ph(s,x,y,w,.72,v,1+i*3+j,size=19,color=PINK if j==0 else INK)
        line(s,.7,y+.86,12.6,y+.86)
    instance(s,'Use three real failure modes. Make each test concrete: where to probe, what to print or which variable to inspect. Keep corrective actions in speaker notes until the evidence supports them.')

    s=layout('Predict / reveal')
    heading(s,'12 / CHECK UNDERSTANDING','[What happens next?]')
    ph(s,.7,2.42,6.4,1.5,'[Ask one question that exposes the mental model.]',1,size=29,bold=True)
    ph(s,.7,4.65,6.4,1.2,'[A]  [First possibility]\n[B]  [Second possibility]',2,size=21)
    picture(s,7.75,2.4,4.9,3.4,'CODE OUTPUT / TRACE / SMALL FIGURE')
    ph(s,7.75,6.06,4.9,.5,'[Explain your reasoning.]',3,size=18,color=PINK)
    instance(s,'Duplicate this slide for an answer reveal. Keep the answer in speaker notes on the question slide. Replace the figure with a small trace, code excerpt or image; use a code layout for longer snippets.')

    s=layout('Recap / next experiment')
    heading(s,'13 / TAKE IT BACK TO THE ROBOT','[Three things worth remembering]')
    for i in range(3):
        y=2.35+i*1.05;txt(s,.72,y,.6,.5,f'{i+1:02}',25,BLUE,True,MONO)
        ph(s,1.65,y,10.8,.65,'[A short statement learners can use]',i+1,size=25)
    line(s,.7,5.8,12.6,5.8,PINK,1.5)
    ph(s,.72,6.1,11.8,.6,'NEXT / [A small experiment to try independently]',4,size=20,color=PINK)
    instance(s,'End with actionable statements, not a list of section titles. The next experiment should reuse the same tools and change one variable.')

    s=layout('References + resources')
    heading(s,'14 / KEEP EXPLORING','[Datasheets, code and things to read]')
    for i in range(3):
        y=2.35+i*1.25
        ph(s,.7,y,8.3,.45,'[Resource title / author]',1+i*2,size=22,bold=True)
        ph(s,.7,y+.52,8.3,.45,'[Exact URL / page / revision]',2+i*2,size=14,color=CYAN,font=MONO)
    picture(s,9.7,2.55,2.7,2.7,'QR / REPO LOGO',10)
    ph(s,9.45,5.65,3.15,.8,'[Short link learners can type]',7,size=16,color=MUTED,font=MONO)
    instance(s,'Use exact sources and revision numbers where relevant. The QR area is a picture placeholder, not a working QR code. Insert a generated QR only after the destination is final. Add hyperlinks to the resource titles using Insert > Link.')

    s=layout('Blank canvas / spare parts')
    heading(s,'15 / MAKE IT YOURS','[Your title]')
    slide=instance(s,'Blank content area for your own composition. Spare parts shown here are editable normal-slide objects: copy the labels, arrow or note to another slide. Delete them when not needed. Body area: x 0.65–12.65 inches, y 2.2–6.8 inches. Use the Selection Pane to rename and select objects. Add a logo via Insert > Pictures; use the original artwork and preserve its aspect ratio.')
    txt(slide,.75,2.5,5.5,.65,'[A blank page for the next idea.]',24,MUTED)
    for i,(label,c) in enumerate([('OBSERVE',CYAN),('QUESTION',BLUE),('WATCH OUT',PINK)]):
        x=.75+i*3.95;line(slide,x,4.25,x+3.45,4.25,c,2)
        txt(slide,x,4.5,3.45,.42,label,14,c,True,MONO)
        txt(slide,x,5.13,3.45,.95,'[One short note]',20,INK)
    line(slide,.75,6.49,3.2,6.49,CYAN,2,True)
    txt(slide,3.55,6.32,5.5,.4,'[label the signal / action]',15,MUTED,font=MONO)

    p.core_properties.title='DC Lab — Terminal Gremlin / Crash Course Template'
    p.core_properties.subject='Editable teaching layouts for electronics, embedded software and robotics'
    p.core_properties.author='c-lydia / DC Lab'
    p.core_properties.keywords='DC Lab, crash course, editable template, terminal gremlin'
    pptx=ROOT/'DCLab_Crash_Course.pptx';p.save(pptx)
    with ZipFile(pptx) as src,ZipFile(ROOT/'DCLab_Crash_Course.potx','w',ZIP_DEFLATED) as dst:
        for entry in src.infolist():
            data=src.read(entry.filename)
            if entry.filename=='[Content_Types].xml':
                data=data.replace(b'application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml',b'application/vnd.openxmlformats-officedocument.presentationml.template.main+xml')
            dst.writestr(entry,data)
    print(f'Built {len(p.slides)} slides and {len(layouts)} native layouts: {pptx}')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--highlight',type=Path,help='Existing PPTX to recolour')
    parser.add_argument('--slide',type=int,default=7,help='Slide number, starting at 1')
    parser.add_argument('--shape',default='CODE',help='Textbox name in Selection Pane')
    parser.add_argument('--source',type=Path)
    parser.add_argument('--language',default='cpp')
    parser.add_argument('--size',type=float,default=15)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.highlight:
        if not args.source or not args.output:
            parser.error('--highlight needs --source and --output')
        if args.output.resolve()==args.highlight.resolve():
            parser.error('Choose a different --output to preserve the original deck')
        p=Presentation(args.highlight)
        target=next((s for s in p.slides[args.slide-1].shapes if s.name==args.shape),None)
        if target is None: parser.error(f'No shape named {args.shape} on slide {args.slide}')
        highlight(target,args.source.read_text(),args.language,args.size)
        p.save(args.output);print(args.output)
    else:
        build()
