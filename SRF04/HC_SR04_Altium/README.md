# HC-SR04 ultrasonic module

Editable Altium Designer symbol and footprint for the **four-pin HC-SR04**, using the pin numbering and 2.54 mm pitch from the supplied `HC-SR04.IntLib`. The supplied STEP is embedded in the PCB library with the module mounted vertically using its right-angle header. This package does not represent the different SRF04 or five-pin HC-SRF05 modules.

[راهنمای فارسی](README_FA.md) · [Pin map](Pin_Mapping.csv) · [Verification report](Verification.json)

## Previews

![HC-SR04 supplied STEP model, vertical mounting](3D/Preview.png)

CAD render of the supplied geometry in the footprint orientation, with illustrative materials. The sensor faces negative Y; the host PCB surface is Z = 0.

| Schematic symbol | PCB footprint, top view |
| --- | --- |
| ![HC-SR04 schematic symbol](Symbol_Preview.png) | ![HC-SR04 vertical-module footprint](Footprint_Preview.png) |

Symbol and footprint previews are generated from the saved library files. They are not Altium screenshots.

## Files

| File | Contents |
| --- | --- |
| [HC_SR04_Module.SchLib](HC_SR04_Module.SchLib) | `HC_SR04_MODULE`, four pins with input/output electrical types and explicit footprint mapping |
| [HC_SR04_Module.PcbLib](HC_SR04_Module.PcbLib) | `HC_SR04_VERTICAL_1X4_P254`, plated through-hole pads and embedded STEP |
| [HC_SR04.LibPkg](HC_SR04.LibPkg) | Source library project for compilation in Altium |
| [Pin_Mapping.csv](Pin_Mapping.csv) | Pin functions and pad coordinates in millimeters |
| [3D/HC_SR04.step](3D/HC_SR04.step) | Byte-identical copy of the user-supplied `HC-SR04--3DModel-STEP-1.STEP` |
| [Verification.json](Verification.json) | Binary readback and model/header alignment checks |
| [tools/build_library.py](tools/build_library.py) | Rebuild and verify with `altium-monkey==2026.9.22` |
| [tools/render_model.py](tools/render_model.py), [tools/render_previews.cjs](tools/render_previews.cjs) | Reproduce the STEP render with cadquery-ocp-novtk 7.9.3.1.1 / NumPy / Pillow and the SVG-to-PNG previews with Node.js / sharp |

The supplied compiled IntLib was used as a reference. Following the repository convention, generated or supplied integrated libraries remain outside version control; editable sources are distributed here.

## Use in Altium Designer

1. Download the complete `HC_SR04_Altium` folder, keeping its source files together.
2. Open `HC_SR04.LibPkg` and compile it in Altium, or add both source libraries to your project.
3. Place `HC_SR04_MODULE` and use its linked `HC_SR04_VERTICAL_1X4_P254` footprint.
4. Transfer the component to the PCB and inspect its 3D view. The model is embedded and needs no external path.
5. Check the actual module's labels, header, mounting height and clearance before fabrication. Socket mounting or a straight header needs a different placement/model transform.

## Pin numbering and orientation

Component-side view of the host PCB, with positive Y upwards:

```text
         1       2       3       4
        VCC     TRIG    ECHO    GND
 X/mm  -3.81   -1.27   +1.27   +3.81     Y = 0
        square pad 1

       Vertical module body is toward -Y
       Acoustic faces point toward -Y
```

| Pin | Name | Function | Symbol type |
| --- | --- | --- | --- |
| 1 | VCC | +5 V supply | Power |
| 2 | TRIG | Trigger pulse input | Input |
| 3 | ECHO | Echo duration output | Output |
| 4 | GND | Supply return | Power |

The [HC-SR04 datasheet hosted by SparkFun](https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf) specifies 5 V operation and a 10 µs trigger pulse. Match the ECHO signal level to the receiving controller. The supplied IntLib used I/O types for TRIG and ECHO; these sources use Input and Output respectively. Pin numbering is preserved from the supplied IntLib. The STEP header has no verified electrical labels, so its pin function orientation must be compared with the actual module.

## Mechanical details

| Item | Value / basis |
| --- | --- |
| Header | 1 × 4, 2.54 mm pitch |
| Pad / plated drill | 1.80 / 1.02 mm; pad size is a design choice, drill follows supplied library |
| Solder-mask expansion | 0.10 mm per side |
| Module PCB | 45 × 20 × 1.2 mm, from supplied STEP |
| Board height above host | 20 mm in the selected vertical mounting |
| Board projection on host | X = ±22.5 mm, Y = −5.6 to −4.4 mm |
| Transducer projection | X = −21 to −5 and +5 to +21 mm; Y = −17.6 to −5.6 mm |
| Placement envelope | X = ±23 mm, Y = −18.1 to +1.5 mm; Mechanical 15 |
| Model transform | Rx = +90°, Ry = Rz = 0°; X = 0, Y = −10.05, Z = 0 mm |
| Header tip below host surface | 7.53 mm in the supplied geometry |

The transform turns the module PCB vertical and aligns the four free header legs with the host pads. The header plastic starts at the host surface. Mechanical 13 shows the projected board and transducers; Mechanical 15 is a placement margin, not an electrical or acoustic keepout. Top Overlay identifies the header, pin 1 and sensor direction. Mechanical 1 contains the 3D body. Leave the acoustic path clear and account for the long pin tails below the PCB. The STEP includes two diagonal 2 mm mounting holes in the vertical module; these are not holes in the host PCB footprint.

## Verification and provenance

Saved SchLib/PcbLib files were read back to check the pin names, four pad coordinates, plated drills, footprint link and one-to-one pin mapping. The embedded STEP was decompressed and compared byte-for-byte with the supplied model. Header free-end centers were extracted from STEP vertices, transformed using the saved body placement and matched to all four saved pads.

Native Altium opening, compilation, placement and 3D display have **not** been verified. No hardware dimensions have been measured.

The STEP header identifies SolidWorks 2017 / SwSTEP 2.0 and an export date of 2020-03-15; author and organization fields are blank. The supplied IntLib contains conversion-directory paths, which are not carried into these generated sources. Source download URLs and redistribution terms were not provided for either attachment; see [third-party notices](../../THIRD_PARTY_NOTICES.md).
