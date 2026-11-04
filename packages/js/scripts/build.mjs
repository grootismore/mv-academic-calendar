import { build } from "esbuild";
import { copyFileSync, rmSync, mkdirSync } from "node:fs";
rmSync("dist", { recursive: true, force: true }); mkdirSync("dist");
for (const entry of ["index", "ics"]) {
  const common = { entryPoints: [`src/${entry}.js`], bundle: true, minify: false, target: "es2020", logLevel: "warning" };
  await build({ ...common, format: "esm", outfile: `dist/${entry}.js` });
  await build({ ...common, format: "cjs", outfile: `dist/${entry}.cjs` });
  copyFileSync(`src/${entry}.d.ts`, `dist/${entry}.d.ts`);
}
for (const f of ["LICENSE", "DATA-LICENSE.md"]) copyFileSync(`../../${f}`, f);
console.log("built");
