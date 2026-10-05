"""Build and read back the MINI-360 libraries (requires altium-monkey 2026.9.22)."""
from pathlib import Path
import csv
import hashlib
import json
import math
import re

from altium_monkey.altium_schlib import AltiumSchLib
from altium_monkey.altium_record_sch__pin import AltiumSchPin
from altium_monkey.altium_sch_enums import PinElectrical, PinOrientation
from altium_monkey.altium_pcblib_builder import PcbLibBuilder
from altium_monkey.altium_pcblib import AltiumPcbLib
from altium_monkey.altium_record_types import PcbLayer
from altium_monkey.altium_pcb_svg_renderer import PcbSvgRenderOptions

ROOT = Path(__file__).resolve().parents[1]
SYMBOL = 'MINI_360_MODULE'
FOOTPRINT = 'MINI_360_4P_1640X1040'
MM = 1000 / 25.4
PINS = [('1', 'IN+', -8.2, -5.2), ('2', 'IN-', -8.2, 5.2),
        ('3', 'OUT-', 8.2, 5.2), ('4', 'OUT+', 8.2, -5.2)]
SOURCE = 'https://eshop.eca.ir/ماژول-تغذیه-ولتاژ-و-شارژ/14379-ماژول-رگولاتور-dc-به-dc-متغیر-کاهنده-2-آمپر-mini-360.html'


def build():
    sch = AltiumSchLib(show_comments_designators=True)
    sym = sch.add_symbol(SYMBOL, 'MINI-360 adjustable non-isolated buck converter module')
    sym.add_rectangle(-450, -250, 450, 250, area_color=0xEFFFFF)
    sym.add_designator('U?', -450, 300)
    sym.add_parameter('Comment', 'MINI-360', x=-450, y=-350)
    sym.add_label('BUCK', -100, -40)
    for number, name, x, y in PINS:
        # The stored pin location is at the body; the free end extends outward.
        sym.add_pin(AltiumSchPin(number, name, -450 if x < 0 else 450,
                                150 if name.endswith('+') else -150,
                                length=200,
                                orientation=PinOrientation.LEFT if x < 0 else PinOrientation.RIGHT,
                                electrical_type=PinElectrical.POWER, owner_part_id=1))
    for name, value in [('Supplier', 'ECA'), ('Supplier Part Number', '3011015132'),
                        ('Supplier URL', SOURCE), ('Input Voltage', '4.75-23 V (supplier)'),
                        ('Output Voltage', '1-17 V adjustable (supplier)'),
                        ('Output Current', '1.8 A continuous / 2 A peak (supplier)'),
                        ('IC Variant', 'Unconfirmed: ECA MP1482; supplied archive MP2307'),
                        ('Mechanical Basis', 'Supplied HW-187 STEP, 18 x 12 mm; verify hardware')]:
        sym.add_parameter(name, value, is_hidden=True)
    children = [{'RECORD': '46'}] + [
        {'RECORD': '47', 'DesIntf': n, 'DesImpCount': '1', 'DesImp0': n}
        for n, _, _, _ in PINS] + [{'RECORD': '48'}]
    sym.add_implementation({'RECORD': '45', 'ModelName': FOOTPRINT, 'ModelType': 'PCBLIB',
                            'IsCurrent': 'T', 'DatafileCount': '1',
                            'ModelDatafileEntity0': 'MINI_360_Module',
                            'ModelDatafileKind0': 'PCBLib'}, children)
    sch.save(ROOT / 'MINI_360_Module.SchLib')

    pcb = PcbLibBuilder()
    fp = pcb.add_footprint(FOOTPRINT, height=f'{5.75 * MM}mil',
                          description='MINI-360 HW-187 model geometry; 18x12 mm; four wire/header connections')
    for n, _, x, y in PINS:
        pcb.add_pad(fp, designator=n, x_mil=x * MM, y_mil=y * MM,
                    width_mil=1.8 * MM, height_mil=1.8 * MM,
                    layer=PcbLayer.MULTI_LAYER, shape='rectangle' if n == '1' else 'round',
                    hole_size_mil=1.0 * MM, plated=True,
                    solder_mask_expansion_mils=0.1 * MM, solder_mask_expansion_mode='manual')

    def line(a, b, layer, width=0.15):
        pcb.add_track(fp, start_x_mil=a[0] * MM, start_y_mil=a[1] * MM,
                      end_x_mil=b[0] * MM, end_y_mil=b[1] * MM,
                      width_mil=width * MM, layer=layer)

    def rect(x, y, layer):
        corners = [(-x, -y), (x, -y), (x, y), (-x, y), (-x, -y)]
        for a, b in zip(corners, corners[1:]):
            line(a, b, layer)

    rect(9, 6, PcbLayer.MECHANICAL_13)
    rect(9.7, 6.7, PcbLayer.MECHANICAL_15)
    # Break overlay near the corner pads, retaining solder-mask clearance.
    for y in [-6, 6]: line((-6.95, y), (6.95, y), PcbLayer.TOP_OVERLAY)
    for x in [-9, 9]: line((x, -3.95), (x, 3.95), PcbLayer.TOP_OVERLAY)
    line((-9.5, -4), (-9.5, -6.5), PcbLayer.TOP_OVERLAY)
    line((-9.5, -6.5), (-7, -6.5), PcbLayer.TOP_OVERLAY)
    for n, name, x, y in PINS:
        pcb.add_text(fp, text=name, x_mil=(-7 if x < 0 else 4.5) * MM,
                     y_mil=(4.1 if y > 0 else -4.9) * MM,
                     height_mil=0.65 * MM, stroke_width_mil=0.12 * MM)
    pcb.add_text(fp, text='MINI-360', x_mil=-3.6 * MM, y_mil=-0.4 * MM,
                 height_mil=0.8 * MM, stroke_width_mil=0.12 * MM)
    step = (ROOT / '3D/MINI_360_HW187.step').read_bytes()
    model = pcb.add_embedded_model(name='MINI_360_HW187.step', model_data=step,
                                   rotation_z_degrees=-90, z_offset_mil=-14 * MM)
    pcb.add_component_body_rectangle(fp, left_mil=-9 * MM, bottom_mil=-6 * MM,
                                     right_mil=9 * MM, top_mil=6 * MM,
                                     overall_height_mil=5.75 * MM, standoff_height_mil=2 * MM,
                                     model=model, model_2d_x_mil=-0.133657042013 * MM,
                                     model_2d_y_mil=-0.631833289516 * MM,
                                     identifier='MINI_360_HW187', name='MINI-360 module')
    pcb.save(ROOT / 'MINI_360_Module.PcbLib')
    with (ROOT / 'Pin_Mapping.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['pad', 'pin', 'function', 'x_mm', 'y_mm'])
        for n, name, x, y in PINS:
            w.writerow([n, name, {'IN+': 'Positive input', 'IN-': 'Input return (common GND)',
                                'OUT+': 'Positive adjustable output', 'OUT-': 'Output return (common GND)'}[name], x, y])

    # All checks below use the saved binary files, not the builder's in-memory state.
    rs = AltiumSchLib(ROOT / 'MINI_360_Module.SchLib', show_comments_designators=True)
    rp = AltiumPcbLib(ROOT / 'MINI_360_Module.PcbLib')
    s = rs.get_symbol(SYMBOL)
    f = rp.find_footprint(FOOTPRINT)
    assert [(p.designator, p.name) for p in s.pins] == [(n, name) for n, name, _, _ in PINS]
    assert len(f.pads) == 4
    actual = {p.designator: p for p in f.pads}
    for n, _, x, y in PINS:
        p = actual[n]
        assert abs(p.x / 10000 / MM - x) < 1e-5
        assert abs(p.y / 10000 / MM - y) < 1e-5
        assert abs(p.hole_size / 10000 / MM - 1) < 1e-5
        assert p.is_plated
    impl = s.implementations[0]
    assert impl.model_name == FOOTPRINT
    assert [(m.designator_interface, m.implementation_designators) for m in impl.map.children] == [(n, [n]) for n, _, _, _ in PINS]
    # Payload accessor returns decompressed STEP bytes.
    assert len(rp.embedded_model_payloads()) == 1
    embedded = rp.get_embedded_model_payload(0)
    assert embedded == step
    body = f.component_bodies[0]
    assert body.model_is_embedded and body.model_name == 'MINI_360_HW187.step'
    assert body.model_3d_rotx == body.model_3d_roty == 0
    assert body.model_3d_rotz == -90
    assert abs(body.model_3d_dz / 10000 / MM + 14) < 1e-5
    # Extract the four 1.2 mm hole axes directly from the original STEP entities.
    entities = {int(n): t.replace('\n', '') for n, t in
                re.findall(r'#(\d+)\s*=\s*(.*?);', step.decode('ascii'), re.S)}
    holes = []
    for entity in entities.values():
        if not entity.startswith('CYLINDRICAL_SURFACE'):
            continue
        ref, radius = re.search(r'#(\d+),([\d.E+-]+)\)', entity).groups()
        if abs(float(radius) - 0.6) > 1e-7:
            continue
        point_ref = re.findall(r'#(\d+)', entities[int(ref)])[0]
        xyz = [float(v) for v in re.search(r',\((.*?)\)\)', entities[int(point_ref)]).group(1).split(',')]
        angle = math.radians(body.model_3d_rotz)
        x = xyz[0] * math.cos(angle) - xyz[1] * math.sin(angle) + body.model_2d_x / 10000 / MM
        y = xyz[0] * math.sin(angle) + xyz[1] * math.cos(angle) + body.model_2d_y / 10000 / MM
        holes.append((x, y))
    assert len(holes) == 4
    assert all(min(math.hypot(x - hx, y - hy) for hx, hy in holes) < 1e-5
               for _, _, x, y in PINS)
    (ROOT / 'Symbol_Preview.svg').write_text(rs.symbol_to_svg(SYMBOL, width=1000, height=600), encoding='utf-8')
    opts = PcbSvgRenderOptions(visible_layers=[PcbLayer.TOP, PcbLayer.TOP_OVERLAY,
                                             PcbLayer.MECHANICAL_13, PcbLayer.MECHANICAL_15],
                               svg_display_scale=40, svg_size_unit='px')
    (ROOT / 'Footprint_Preview.svg').write_text(f.to_svg(options=opts), encoding='utf-8')
    report = dict(pin_count=4, pad_count=4, pin_names_roundtrip_match=True,
                  pin_pad_designators_match=True, explicit_pin_pad_map_verified=True,
                  pad_coordinates_roundtrip_match=True, plated_drill_mm=1.0, pad_size_mm=1.8,
                  board_outline_mm=[18, 12], hole_center_spacing_mm=[16.4, 10.4],
                  model_hole_diameter_mm=1.2, model_rotation_z_degrees=-90,
                  model_xy_offset_mm=[-0.133657042013, -0.631833289516],
                  model_z_offset_mm=-14, module_board_bottom_above_host_mm=2,
                  model_top_above_host_mm=5.75, step_embedded=True,
                  model_hole_axes_align_with_saved_pads=True,
                  embedded_model_transform_roundtrip_verified=True,
                  step_identical_to_supplied_model=True,
                  embedded_step_sha256=hashlib.sha256(embedded).hexdigest(),
                  supplier_nominal_outline_mm=[17, 11],
                  mechanical_basis='Supplied STEP; supplier dimensions differ',
                  native_altium_open_and_compile_verified=False, dimensions_measured_on_hardware=False)
    (ROOT / 'Verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    build()
