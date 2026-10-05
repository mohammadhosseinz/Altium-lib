# Add a new library

Keep each new part or module in a separate folder. An optional nested folder can group its Altium files. Existing library folders do not need renaming.

```text
PART_NAME/
  PART_NAME_Altium/
    PART_NAME.SchLib
    PART_NAME.PcbLib
    PART_NAME.LibPkg            # optional
    README.md
    Pin_Mapping.csv
    Verification.json           # optional
    Preview.png                 # or separate symbol/footprint previews
    3D/
      model.step                # when available
```

## Document the part

Write an English `README.md` in the library folder. Include:

- The exact part or module variant and links to the source datasheet or model.
- The creator, source, and redistribution permission for third-party CAD models and photographs.
- A preview image embedded with a relative path, clearly identified as a library preview or product photo.
- A file list and instructions for loading the source libraries in Altium Designer.
- The top-view orientation, pin 1 location, and pin numbering convention.
- Pitch, row spacing, board outline, pad and drill sizes, and relevant mounting height.
- Mechanical layers, antenna clearance or other placement constraints where applicable.
- Checks completed and checks still pending, including whether hardware was measured and Altium was tested.

Additional language versions may use a suffix such as `README_FA.md`, linked from the English README.

## Record the pin map

Use one row per pad. When coordinates are known, use columns such as:

```csv
pad,pin,function,x_mm,y_mm
```

If coordinates are not known, record side and position instead. Match the symbol and footprint designators exactly.

## Check before publishing

- Compare symbol pins, footprint pads, and pin-map rows by number and name.
- Open both library files in Altium, place the symbol, transfer it to a PCB, and inspect the 3D view when Altium is available.
- Check the footprint orientation and dimensions against a physical module or a trusted mechanical drawing.
- Confirm that STEP placement and height match the intended mounting method.
- Confirm that the files do not refer to personal or temporary filesystem paths.
- Keep generated output and backups out of the commit.
- Check that third-party models and photographs may be redistributed publicly.
- Add a row to [LIBRARY_INDEX.csv](../LIBRARY_INDEX.csv) and link the new README and preview from the root [README.md](../README.md).
