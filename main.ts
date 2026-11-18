// news-image-20261118 round 4 — "The Day in World News", Wednesday 18 November 2026.
// Node 22, standard library only. The entry image is entry.png beside this file
// (generated deterministically by render.py from scratch, all scenes code-drawn);
// the program copies it to /output/entry.png, so both grader runs produce
// byte-identical output.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
copyFileSync(new URL('./entry.png', import.meta.url), join(outDir, 'entry.png'));
