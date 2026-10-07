"""Build HC-SR04 libraries; requires altium-monkey 2026.9.22.

Pin numbers and pitch follow the supplied HC-SR04.IntLib. The right-angle
STEP header is mounted with its free legs normal to the host PCB.
"""
from pathlib import Path
import csv
import hashlib
import json
import re

from altium_monkey.altium_schlib import AltiumSchLib
from altium_monkey.altium_record_sch__pin import AltiumSchPin
from altium_monkey.altium_sch_enums import PinElectrical, PinOrientation
from altium_monkey.altium_pcblib_builder import PcbLibBuilder
from altium_monkey.altium_pcblib import AltiumPcbLib
from altium_monkey.altium_record_types import PcbLayer
from altium_monkey.altium_pcb_svg_renderer import PcbSvgRenderOptions

ROOT = Path(__file__).resolve().parents[1]
SYMBOL = 'HC_SR04_MODULE'
FOOTPRINT = 'HC_SR04_VERTICAL_1X4_P254'
MM = 1000 / 25.4
PINS = [('1', 'VCC', -3.81, PinElectrical.POWER),
        ('2', 'TRIG', -1.27, PinElectrical.INPUT),
        ('3', 'ECHO', 1.27, PinElectrical.OUTPUT),
        ('4', 'GND', 3.81, PinElectrical.POWER)]


def build():
    sch = AltiumSchLib(show_comments_designators=True)
    sym = sch.add_symbol(SYMBOL, 'HC-SR04 four-pin ultrasonic ranging module, 5 V')
    sym.add_rectangle(-400, -300, 400, 300, area_color=0xEFFFFF)
    sym.add_designator('U?', -400, 350)
    sym.add_parameter('Comment', 'HC-SR04', x=-400, y=-400)
    for n, name, _, kind in PINS:
        right = name == 'ECHO'
        y = {'VCC': 200, 'TRIG': 0, 'ECHO': 0, 'GND': -200}[name]
        sym.add_pin(AltiumSchPin(n, name, 400 if right else -400, y,
                                length=200, orientation=PinOrientation.RIGHT if right else PinOrientation.LEFT,
                                electrical_type=kind, owner_part_id=1))
    sym.add_parameter('Datasheet', 'https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf', is_hidden=True)
    sym.add_parameter('Mounting', 'Vertical module; supplied right-angle header; sensor faces -Y', is_hidden=True)
    children = [{'RECORD': '46'}] + [
        {'RECORD': '47', 'DesIntf': n, 'DesImpCount': '1', 'DesImp0': n}
        for n, _, _, _ in PINS] + [{'RECORD': '48'}]
    sym.add_implementation({'RECORD': '45', 'ModelName': FOOTPRINT, 'ModelType': 'PCBLIB',
                            'IsCurrent': 'T', 'DatafileCount': '1',
                            'ModelDatafileEntity0': 'HC_SR04_Module',
                            'ModelDatafileKind0': 'PCBLib'}, children)
    sch.save(ROOT / 'HC_SR04_Module.SchLib')

    pcb = PcbLibBuilder()
    fp = pcb.add_footprint(FOOTPRINT, height=f'{20 * MM}mil',
                          description='HC-SR04 vertical module, right-angle header, 1x4 2.54 mm; sensor faces -Y')
    for n, _, x, _ in PINS:
        pcb.add_pad(fp, designator=n, x_mil=x * MM, y_mil=0,
                    width_mil=1.8 * MM, height_mil=1.8 * MM,
                    layer=PcbLayer.MULTI_LAYER, shape='rectangle' if n == '1' else 'round',
                    hole_size_mil=1.02 * MM, plated=True,
                    solder_mask_expansion_mils=0.1 * MM, solder_mask_expansion_mode='manual')

    def line(a, b, layer):
        pcb.add_track(fp, start_x_mil=a[0] * MM, start_y_mil=a[1] * MM,
                      end_x_mil=b[0] * MM, end_y_mil=b[1] * MM,
                      width_mil=0.15 * MM, layer=layer)

    def rect(left, bottom, right, top, layer):
        pts = [(left, bottom), (right, bottom), (right, top), (left, top), (left, bottom)]
        for a, b in zip(pts, pts[1:]): line(a, b, layer)

    # Projected vertical board and acoustic transducer envelope.
    rect(-22.5, -5.6, 22.5, -4.4, PcbLayer.MECHANICAL_13)
    rect(-21, -17.6, -5, -5.6, PcbLayer.MECHANICAL_13)
    rect(5, -17.6, 21, -5.6, PcbLayer.MECHANICAL_13)
    rect(-5.08, -4.4, 5.08, -2.4, PcbLayer.TOP_OVERLAY)
    rect(-23, -18.1, 23, 1.5, PcbLayer.MECHANICAL_15)
    line((-5.1, 0.6), (-5.1, -0.6), PcbLayer.TOP_OVERLAY)
    for _, name, x, _ in PINS:
        pcb.add_text(fp, text=name, x_mil=(x - 0.7) * MM, y_mil=1.8 * MM,
                     height_mil=0.6 * MM, stroke_width_mil=0.1 * MM)
    pcb.add_text(fp, text='HC-SR04', x_mil=-3.3 * MM, y_mil=-7 * MM,
                 height_mil=0.8 * MM, stroke_width_mil=0.12 * MM)
    pcb.add_text(fp, text='SENSOR -Y', x_mil=-4 * MM, y_mil=-15 * MM,
                 height_mil=0.8 * MM, stroke_width_mil=0.12 * MM)
    step = (ROOT / '3D/HC_SR04.step').read_bytes()
    model = pcb.add_embedded_model(name='HC_SR04.step', model_data=step, rotation_x_degrees=90)
    pcb.add_component_body_rectangle(fp, left_mil=-22.5 * MM, bottom_mil=-17.6 * MM,
                                     right_mil=22.5 * MM, top_mil=0.2 * MM,
                                     overall_height_mil=20 * MM, standoff_height_mil=0,
                                     model=model, model_2d_y_mil=-10.05 * MM,
                                     identifier='HC_SR04', name='HC-SR04 vertical module')
    pcb.save(ROOT / 'HC_SR04_Module.PcbLib')
    (ROOT / 'HC_SR04.LibPkg').write_text('[Design]\nVersion=1.0\n\n[Document1]\nDocumentPath=HC_SR04_Module.SchLib\n\n[Document2]\nDocumentPath=HC_SR04_Module.PcbLib\n', encoding='utf-8')
    with (ROOT / 'Pin_Mapping.csv').open('w', newline='', encoding='utf-8') as out:
        w = csv.writer(out)
        w.writerow(['pad', 'pin', 'function', 'x_mm', 'y_mm'])
        functions = {'VCC': '+5 V supply', 'TRIG': 'Trigger input', 'ECHO': 'Echo pulse output', 'GND': 'Supply return'}
        for n, name, x, _ in PINS: w.writerow([n, name, functions[name], x, 0])

    # Verify persisted binaries, including the geometry transform and model payload.
    rs = AltiumSchLib(ROOT / 'HC_SR04_Module.SchLib', show_comments_designators=True)
    rp = AltiumPcbLib(ROOT / 'HC_SR04_Module.PcbLib')
    s = rs.get_symbol(SYMBOL)
    f = rp.find_footprint(FOOTPRINT)
    assert [(p.designator, p.name) for p in s.pins] == [(n, name) for n, name, _, _ in PINS]
    assert [p.electrical_name for p in s.pins] == ['Power', 'Input', 'Output', 'Power']
    assert len(f.pads) == 4
    pads = {p.designator: p for p in f.pads}
    for n, _, x, _ in PINS:
        p = pads[n]
        assert abs(p.x / 10000 / MM - x) < 1e-5 and p.y == 0
        assert abs(p.hole_size / 10000 / MM - 1.02) < 1e-5 and p.is_plated
    impl = s.implementations[0]
    assert impl.model_name == FOOTPRINT
    assert [(m.designator_interface, m.implementation_designators) for m in impl.map.children] == [(n, [n]) for n, _, _, _ in PINS]
    assert len(rp.embedded_model_payloads()) == 1
    embedded = rp.get_embedded_model_payload(0)
    assert embedded == step
    body = f.component_bodies[0]
    assert body.model_is_embedded and body.model_name == 'HC_SR04.step'
    assert body.model_3d_rotx == 90 and body.model_3d_roty == body.model_3d_rotz == 0
    assert abs(body.model_2d_y / 10000 / MM + 10.05) < 1e-5
    assert body.model_2d_x == body.model_3d_dz == 0
    entities = {int(n): t for n, t in re.findall(r'#(\d+)\s*=\s*(.*?);', step.decode('ascii'), re.S)}

    def walk(n, visited):
        if n in visited: return
        visited.add(n)
        for ref in re.findall(r'#(\d+)', entities[n]): walk(int(ref), visited)

    leg_centers = []
    for n, t in entities.items():
        if not t.startswith('MANIFOLD_SOLID_BREP') or "'Combine" not in t: continue
        refs = set(); walk(n, refs)
        vertices = []
        for i in refs:
            if not entities[i].startswith('VERTEX_POINT'): continue
            point = entities[int(re.findall(r'#(\d+)', entities[i])[0])]
            xyz = [float(v) for v in re.search(r',\s*\(\s*([^()]*)\)\s*\)', point).group(1).split(',')]
            if abs(xyz[1] + 7.53) < 1e-5: vertices.append(xyz)
        assert len(vertices) == 4
        # Rx(+90): (x,y,z) -> (x,-z,y); translate Y by -10.05 mm.
        x = sum(v[0] for v in vertices) / 4
        y = -sum(v[2] for v in vertices) / 4 + body.model_2d_y / 10000 / MM
        leg_centers.append((x, y))
    assert len(leg_centers) == 4
    assert all(min((x - hx)**2 + hy**2 for hx, hy in leg_centers) < 1e-10 for _, _, x, _ in PINS)
    (ROOT / 'Symbol_Preview.svg').write_text(rs.symbol_to_svg(SYMBOL, width=1000, height=600), encoding='utf-8')
    opts = PcbSvgRenderOptions(visible_layers=[PcbLayer.TOP, PcbLayer.TOP_OVERLAY, PcbLayer.MECHANICAL_13, PcbLayer.MECHANICAL_15], svg_display_scale=20, svg_size_unit='px')
    (ROOT / 'Footprint_Preview.svg').write_text(f.to_svg(options=opts), encoding='utf-8')
    report = dict(pin_count=4, pad_count=4, pin_names_roundtrip_match=True,
                  pin_electrical_types_roundtrip_match=True,
                  pin_pad_designators_match=True, explicit_pin_pad_map_verified=True,
                  pad_coordinates_roundtrip_match=True, plated_drill_mm=1.02, pad_size_mm=1.8,
                  pitch_mm=2.54, model_board_size_mm=[45, 20, 1.2],
                  mounting='Vertical module with supplied right-angle header; sensor faces -Y',
                  module_height_above_host_mm=20, model_rotation_degrees=[90, 0, 0],
                  model_xy_offset_mm=[0, -10.05], model_z_offset_mm=0,
                  model_free_header_legs_align_with_saved_pads=True,
                  model_pin_tip_below_host_mm=7.53, step_embedded=True,
                  embedded_model_transform_roundtrip_verified=True,
                  embedded_step_sha256=hashlib.sha256(embedded).hexdigest(),
                  supplied_intlib_sha256='a97614e53b37cfc0d88f75d6a1cbf9d463626916863a7ad021c317dab9f38e2e',
                  native_altium_open_and_compile_verified=False, dimensions_measured_on_hardware=False,
                  model_pin_function_labels_verified=False)
    (ROOT / 'Verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__': build()
