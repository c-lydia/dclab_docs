"""Move the template's visible layout artwork onto individual editable slides.

Preserves the original deck. Images remain native pictures, text becomes ordinary
text boxes, and picture placeholders retain their insert-picture behaviour.
"""
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from pptx import Presentation
from pptx.enum.shapes import PP_PLACEHOLDER
from pptx.dml.color import RGBColor

ROOT = Path(__file__).resolve().parent
R_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'


def readable_name(shape, element, index):
    if shape.name == 'CODE':
        name = 'CODE'
    elif shape.name.startswith('BRAND | '):
        name = 'LOGO / ' + ('ITC' if 'itc' in shape.name else 'DC Lab') + ' / replace or move'
    elif shape.is_placeholder and shape.placeholder_format.type == PP_PLACEHOLDER.PICTURE:
        name = 'PICTURE SLOT / ' + shape.text.split('\n')[0]
    elif shape.has_text_frame and shape.text.strip():
        name = 'TEXT / ' + shape.text.strip().replace('\n', ' ')[:68]
    elif shape.shape_type == 13:
        name = 'PICTURE / ' + shape.name
    else:
        name = 'SHAPE / ' + shape.name
    # Keep names unique while leaving CODE addressable by the highlighter.
    if name != 'CODE':
        name += f' [{index:02}]'
    element.xpath('.//p:cNvPr')[0].set('name', name)


def build():
    p = Presentation(ROOT / 'DCLab_Crash_Course.pptx')
    for slide in p.slides:
        layout = slide.slide_layout
        original = list(slide.shapes)
        local_placeholders = {
            sh.placeholder_format.idx: sh for sh in original if sh.is_placeholder
        }
        chosen = set()
        ordered = []
        # Reproduce the visual stack, substituting edited slide-level text for
        # the corresponding layout placeholder rather than duplicating it.
        for sh in layout.shapes:
            local = local_placeholders.get(sh.placeholder_format.idx) if sh.is_placeholder else None
            if local is not None:
                ordered.append(('slide', local, slide.part)); chosen.add(local.shape_id)
            else:
                ordered.append(('layout', sh, layout.part))
        for sh in original:
            if sh.shape_id not in chosen:
                ordered.append(('slide', sh, slide.part))

        copies = []
        id_map = {}
        for index, (origin, sh, part) in enumerate(ordered, 2):
            element = deepcopy(sh._element)
            id_map[(origin, sh.shape_id)] = index
            element.xpath('.//p:cNvPr')[0].set('id', str(index))
            readable_name(sh, element, index)
            if sh.is_placeholder and sh.placeholder_format.type != PP_PLACEHOLDER.PICTURE:
                for ph in element.xpath('.//p:ph'):
                    ph.getparent().remove(ph)
            if part is not slide.part:
                for child in element.iter():
                    for attr, value in list(child.attrib.items()):
                        if attr.startswith('{' + R_NS + '}'):
                            rel = part.rels[value]
                            target = rel.target_ref if rel.is_external else rel.target_part
                            child.set(attr, slide.part.relate_to(target, rel.reltype, rel.is_external))
            copies.append((origin, element))
        # Connector attachments must follow the newly assigned shape IDs.
        for origin, element in copies:
            for endpoint in element.xpath('.//a:stCxn | .//a:endCxn'):
                endpoint.set('id', str(id_map[(origin, int(endpoint.get('id')))]))
        for sh in original:
            sh._element.getparent().remove(sh._element)
        for _, element in copies:
            slide.shapes._spTree.insert_element_before(element, 'p:extLst')

        # The background colour is now a slide setting, independent of a master.
        colours = layout._element.xpath('./p:cSld/p:bg/p:bgPr/a:solidFill/a:srgbClr')
        if colours:
            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb = RGBColor.from_string(colours[0].get('val'))
        old_notes = slide.notes_slide.notes_text_frame.text
        old_notes = old_notes.replace(
            'Change logos in View > Slide Master (LibreOffice: View > Master Slide).',
            'Click a logo directly to move, resize, delete or replace its picture.'
        ).replace(
            'Duplicate the slide you need, or choose Home > New Slide > a DC Lab layout.',
            'Duplicate the slide you need to retain all editable elements.'
        )
        slide.notes_slide.notes_text_frame.text = (
            'DIRECT EDIT VERSION: All visible artwork is on this slide. Click logos, '
            'labels, footer text, rules and panels directly. Text uses ordinary text boxes. '
            'Use the Selection Pane for small objects; items are named TEXT / LOGO / SHAPE. '
            'Duplicate a complete slide to reuse the design. New Slide layouts supply only '
            'basic placeholders. Background colour: Format Background / Slide Properties.\n\n'
            + old_notes
        )

    # Only invisible picture-slot geometry remains on the layouts. Native
    # inserted pictures need it to inherit their position and dimensions.
    # There is no old text, logo, border or fill to show through after deletion.
    for layout in p.slide_layouts:
        for sh in list(layout.shapes):
            if sh.is_placeholder and sh.placeholder_format.type == PP_PLACEHOLDER.PICTURE:
                sh.text_frame.clear()
                sh.fill.background()
                sh.line.fill.background()
            else:
                sh._element.getparent().remove(sh._element)
    for sh in list(p.slide_master.shapes):
        sh._element.getparent().remove(sh._element)
    p.core_properties.title = 'DC Lab Crash Course — Directly Editable'
    output = ROOT / 'DCLab_Crash_Course_Editable.pptx'
    p.save(output)
    with ZipFile(output) as src, ZipFile(output.with_suffix('.potx'), 'w', ZIP_DEFLATED) as dst:
        for entry in src.infolist():
            data = src.read(entry.filename)
            if entry.filename == '[Content_Types].xml':
                data = data.replace(
                    b'application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml',
                    b'application/vnd.openxmlformats-officedocument.presentationml.template.main+xml'
                )
            dst.writestr(entry, data)
    print(f'Created {output}: {len(p.slides)} slides with directly selectable artwork.')


if __name__ == '__main__':
    build()
