
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { v4 as uuidv4 } from "uuid";
import path from "path";
import dotenv from "dotenv";


const s3 = new S3Client({
  region: process.env.AWS_REGION,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  },
});

export const uploadCSVToS3 = async (fileBuffer, originalName) => {
  const fileExt = path.extname(originalName);
  const fileName = `uploads/csv/${uuidv4()}${fileExt}`;

  const uploadParams = {
    Bucket: process.env.AWS_S3_BUCKET_NAME,
    Key: fileName,
    Body: fileBuffer,
    ContentType: "text/csv",
  };

  try {
    await s3.send(new PutObjectCommand(uploadParams));
    return `https://${process.env.AWS_S3_BUCKET_NAME}.s3.${process.env.AWS_REGION}.amazonaws.com/${fileName}`;
  } catch (err) {
    console.error("S3 upload error:", err);
    throw new Error("Failed to upload file to S3");
  }
};
