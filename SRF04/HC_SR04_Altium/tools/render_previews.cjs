// Requires Node.js and sharp; rasterize the binary-readback SVG previews.
const fs = require('fs');
const path = require('path');
const sharp = require('sharp');
const root = path.resolve(__dirname, '..');
(async () => {
  for (const name of ['Symbol', 'Footprint']) {
    let svg = fs.readFileSync(path.join(root, `${name}_Preview.svg`), 'utf8');
    // Darken yellow overlay only in the illustration for contrast on white.
    if (name === 'Footprint') svg = svg.replaceAll('#FFFF00', '#846400');
    await sharp(Buffer.from(svg), {density: 240})
      .flatten({background: '#ffffff'})
      .resize({width: name === 'Symbol' ? 880 : 1200})
      .png().toFile(path.join(root, `${name}_Preview.png`));
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
