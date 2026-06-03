import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const clientRoot = path.resolve(__dirname, "..");
const projectRoot = path.resolve(clientRoot, "..");
const distDir = path.join(clientRoot, "dist");

const flaskTemplatesDir = path.join(projectRoot, "server", "app", "templates");
const flaskStaticDir = path.join(projectRoot, "server", "app", "static");
const flaskAssetsDir = path.join(flaskStaticDir, "assets");

function copyFile(source, destination) {
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.copyFileSync(source, destination);
}

function copyDir(source, destination) {
  fs.rmSync(destination, { recursive: true, force: true });
  fs.mkdirSync(destination, { recursive: true });

  for (const entry of fs.readdirSync(source, { withFileTypes: true })) {
    const sourcePath = path.join(source, entry.name);
    const destinationPath = path.join(destination, entry.name);

    if (entry.isDirectory()) {
      copyDir(sourcePath, destinationPath);
    } else {
      copyFile(sourcePath, destinationPath);
    }
  }
}

if (!fs.existsSync(distDir)) {
  console.error("The Vite dist folder does not exist. Run npm run build first.");
  process.exit(1);
}

copyFile(path.join(distDir, "index.html"), path.join(flaskTemplatesDir, "index.html"));
copyDir(path.join(distDir, "assets"), flaskAssetsDir);

console.log("Copied React build into Flask:");
console.log(`- ${path.join(flaskTemplatesDir, "index.html")}`);
console.log(`- ${flaskAssetsDir}`);
