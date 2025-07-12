
// const { S3Client, PutObjectCommand } = require("@aws-sdk/client-s3");
const { v4: uuidv4 } = require("uuid");
const path = require("path");
const fs = require("fs");
require("dotenv").config();

// Comment out S3 client configuration
// const s3 = new S3Client({
//   region: process.env.AWS_REGION,
//   credentials: {
//     accessKeyId: process.env.AWS_ACCESS_KEY_ID,
//     secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
//   },
// });

// Create sheet_dump directory if it doesn't exist
const sheetDumpDir = path.join(__dirname, "../sheet_dump");
if (!fs.existsSync(sheetDumpDir)) {
  fs.mkdirSync(sheetDumpDir, { recursive: true });
}

const uploadCSVToLocal = async (fileBuffer, originalName) => {
  const fileExt = path.extname(originalName);
  const fileName = `${uuidv4()}${fileExt}`;
  const filePath = path.join(sheetDumpDir, fileName);

  try {
    // Write file to local directory
    fs.writeFileSync(filePath, fileBuffer);
    console.log(`File saved locally: ${filePath}`);
    
    // Return the local file path
    return filePath;
  } catch (err) {
    console.error("Local file save error:", err);
    throw new Error("Failed to save file locally");
  }
};

// Comment out the original S3 upload function
// const uploadCSVToS3 = async (fileBuffer, originalName) => {
//   const fileExt = path.extname(originalName);
//   const fileName = `uploads/csv/${uuidv4()}${fileExt}`;

//   const uploadParams = {
//     Bucket: process.env.AWS_S3_BUCKET,
//     Key: fileName,
//     Body: fileBuffer,
//     ContentType: "text/csv",
//   };

//   try {
//     await s3.send(new PutObjectCommand(uploadParams));
//     return `https://${process.env.AWS_S3_BUCKET}.s3.${process.env.AWS_REGION}.amazonaws.com/${fileName}`;
//   } catch (err) {
//     console.error("S3 upload error:", err);
//     throw new Error("Failed to upload file to S3");
//   }
// };

module.exports = { uploadCSVToLocal };
