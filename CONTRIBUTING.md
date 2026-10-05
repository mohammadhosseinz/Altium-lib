# Contributing

New Altium libraries are welcome. Each contribution should be editable, documented, and easy to check against the physical part.

## Before submitting

- Make sure the `.SchLib` and `.PcbLib` files open and work together.
- Confirm that the footprint name linked in the symbol matches the name in the `.PcbLib` file.
- Check that pin 1 agrees across the symbol, footprint, silkscreen, and pin map.
- Include pad numbers, pin names, and coordinates or orientation notes in the pin map.
- Confirm that an embedded STEP model does not depend on a local machine path.
- State which checks were performed and whether physical dimensions were measured on hardware.
- Include a preview of the symbol and footprint in the library's English `README.md`.
- Record the source and redistribution permission for any third-party CAD models or photographs.

## Naming and files

Use a folder named after the part or module. Keep symbol and footprint names short and stable. The recommended files are an English `README.md`, source libraries, a pin map (`Pin_Mapping.csv` or `PinMap.csv`), preview PNGs, and any applicable STEP models in `3D/`. Add `Verification.json` when machine-readable checks are available. Existing libraries may use different folder names; keep their paths stable.

Do not commit generated integrated libraries, temporary previews, backups, or `Project Outputs` directories. If a compiled `.IntLib` is needed for distribution, attach it to a release rather than treating it as source.

Follow the [new-library guide](docs/ADD_NEW_LIBRARY.md) for the full checklist, then add the library to [LIBRARY_INDEX.csv](LIBRARY_INDEX.csv) and the root [README.md](README.md).
