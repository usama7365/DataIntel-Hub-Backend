const express = require("express");
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
    updateProfile,
    updatePassword,

    createUserProfile,
    getUserProfile,
    updateUser,
    updateUserProfile,
} = require("../controllers/userController");
const { isAuthenticatedUser } = require("../middleware/authentication");

const router = express.Router();


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
