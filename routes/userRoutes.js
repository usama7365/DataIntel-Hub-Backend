
const express = require("express");
const { uploadCSVToS3 } = require("../utils/s3upload.js");
const { upload } = require("../middleware/upload.js");
const {
    registerUser,
    loginUser,
    logout,
    forgotPassword,
    resetPassword,
    verifyEmail,
    resendVerificationEmail,
    getAllUser,
    getUserDetails,
    updatePassword,
    updateUser,
} = require("../controllers/userController.js");
const { isAuthenticatedUser } = require("../middleware/authentication.js");

const router = express.Router();


router.post("/upload-csv", upload.single("file"), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ message: "No file uploaded" });
    }

    const s3Url = await uploadCSVToS3(req.file.buffer, req.file.originalname);
    res.status(200).json({ message: "Uploaded successfully", url: s3Url });
  } catch (err) {
    res.status(500).json({ message: err.message || "Upload failed" });
  }
});



//user registration and login
router.route("/register").post(registerUser);
router.route("/verify/:token").get(verifyEmail);
router.route("/email/resend").post(resendVerificationEmail);
router.route("/login").post(loginUser);
router.route("/password/forgot").post(forgotPassword);
router.route("/password/reset/:token").put(resetPassword);
router.route("/logout").get(logout);
router.route("/me").get(isAuthenticatedUser, getUserDetails);
router.route("/me/update").put(isAuthenticatedUser, updateUser);
router.route("/password/update").put(isAuthenticatedUser, updatePassword);

//admin routes
router.route("/admin/users").get(getAllUser);

module.exports = router;
