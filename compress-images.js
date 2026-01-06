const sharp = require("sharp");
const fs = require("fs");
const path = require("path");

// 配置
const SIZE_THRESHOLD = 300 * 1024; // 300KB
const QUALITY = 80; // 压缩质量 (1-100)
const TARGET_DIR = "./"; // 目标目录

// 支持的图片格式
const SUPPORTED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"];

async function getImageFiles(dir) {
  const files = [];
  const items = fs.readdirSync(dir, { withFileTypes: true });

  for (const item of items) {
    const fullPath = path.join(dir, item.name);

    if (item.isDirectory()) {
      // 跳过 node_modules 和 .git 目录
      if (item.name === "node_modules" || item.name === ".git") continue;
      files.push(...(await getImageFiles(fullPath)));
    } else {
      const ext = path.extname(item.name).toLowerCase();
      if (SUPPORTED_EXTENSIONS.includes(ext)) {
        files.push(fullPath);
      }
    }
  }

  return files;
}

async function compressImage(filePath) {
  const stats = fs.statSync(filePath);
  const fileSizeKB = (stats.size / 1024).toFixed(2);

  // 如果小于阈值，跳过
  if (stats.size < SIZE_THRESHOLD) {
    console.log(`⏭️  跳过 ${filePath} (${fileSizeKB} KB < 300 KB)`);
    return { skipped: true, path: filePath };
  }

  console.log(`🔄 压缩中 ${filePath} (${fileSizeKB} KB)...`);

  const ext = path.extname(filePath).toLowerCase();
  const tempPath = filePath + ".tmp";

  try {
    let sharpInstance = sharp(filePath);

    // 根据格式选择压缩参数
    switch (ext) {
      case ".jpg":
      case ".jpeg":
        sharpInstance = sharpInstance.jpeg({ quality: QUALITY, mozjpeg: true });
        break;
      case ".png":
        sharpInstance = sharpInstance.png({
          quality: QUALITY,
          compressionLevel: 9,
        });
        break;
      case ".webp":
        sharpInstance = sharpInstance.webp({ quality: QUALITY });
        break;
    }

    await sharpInstance.toFile(tempPath);

    const newStats = fs.statSync(tempPath);
    const newSizeKB = (newStats.size / 1024).toFixed(2);
    const savedPercent = ((1 - newStats.size / stats.size) * 100).toFixed(1);

    // 直接覆盖原图
    fs.unlinkSync(filePath);
    fs.renameSync(tempPath, filePath);
    console.log(
      `✅ 完成 ${filePath}: ${fileSizeKB} KB → ${newSizeKB} KB (${
        savedPercent > 0 ? "节省" : "增加"
      } ${Math.abs(savedPercent)}%)`
    );
    return {
      compressed: true,
      path: filePath,
      saved: stats.size - newStats.size,
    };
  } catch (error) {
    // 清理临时文件
    if (fs.existsSync(tempPath)) {
      fs.unlinkSync(tempPath);
    }
    console.error(`❌ 压缩失败 ${filePath}: ${error.message}`);
    return { error: true, path: filePath, message: error.message };
  }
}

async function main() {
  console.log("🖼️  图片压缩工具");
  console.log(`📁 扫描目录: ${path.resolve(TARGET_DIR)}`);
  console.log(`📏 大小阈值: ${SIZE_THRESHOLD / 1024} KB`);
  console.log(`🎨 压缩质量: ${QUALITY}%`);
  console.log("-----------------------------------\n");

  const imageFiles = await getImageFiles(TARGET_DIR);
  console.log(`📷 找到 ${imageFiles.length} 个图片文件\n`);

  let totalSaved = 0;
  let compressedCount = 0;
  let skippedCount = 0;
  let errorCount = 0;

  for (const file of imageFiles) {
    const result = await compressImage(file);
    if (result.compressed) {
      compressedCount++;
      totalSaved += result.saved;
    } else if (result.error) {
      errorCount++;
    } else {
      skippedCount++;
    }
  }

  console.log("\n-----------------------------------");
  console.log("📊 压缩完成统计:");
  console.log(`   ✅ 已压缩: ${compressedCount} 个文件`);
  console.log(`   ⏭️  已跳过: ${skippedCount} 个文件`);
  console.log(`   ❌ 失败: ${errorCount} 个文件`);
  console.log(`   💾 总共节省: ${(totalSaved / 1024 / 1024).toFixed(2)} MB`);
}

main().catch(console.error);
