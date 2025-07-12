const multer = require("multer");

const storage = multer.memoryStorage(); // store file in memory as buffer
const upload = multer({
  storage,
  fileFilter: (req, file, cb) => {
    if (file.mimetype === "text/csv") {
      cb(null, true);
    } else {
      cb(new Error("Only CSV files are allowed"));
    }
  },
//   limits: { fileSize: 5 * 1024 * 1024 }, // 5MB max
});

module.exports = { upload };
