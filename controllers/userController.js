const catchAsyncErrors = require("../middleware/asyncErrorHandler");
const User = require("../models/userModel");
const ErrorHandler = require("../utils/errorhandler");
const sendToken = require("../utils/jwtToken");

const sendEmail = require("../utils/sendEmail");
const crypto = require("crypto");

// register a user
exports.registerUser = catchAsyncErrors(async (req, res, next) => {
    // console.log("req.body", req.body);
    const user = await User.create(req.body);


    // Generate an email verification token for the user
    const verifyToken = user.getVerifyEmail();

    await user.save({ validateBeforeSave: false });

    // const verifyEmailUrl = `${req.protocol}://${req.get(
    //     "host"
    // )}/api/verify/${verifyToken}`;
    const verifyEmailUrl = `${process.env.FRONTEND_URL}/EmailVerification/${verifyToken}`;
    const message = `Your email verification token is :- \n\n ${verifyEmailUrl} \n\n If you have not requested this email then, please ingonore it`;
    const token = user.getJWTToken();

    try {
        await sendEmail({
            email: user.email,
            subject: `Data Intel Hub email verification`,
            message,
        });
        res.status(200).json({
            success: true,
            message: `Confirmation email sent to ${user.email} successfully`,
            user,
            token,
        });
    } catch (error) {
        user.verifyEmailToken = undefined;
        user.verifyEmailExpire = undefined;
        await user.save();
        return next(new ErrorHandler(error.message, 500));
    }

    // sendToken(user, 201, res);
});



exports.verifyEmail = catchAsyncErrors(async (req, res, next) => {
    const verifyEmailToken = crypto
        .createHash("sha256")
        .update(req.params.token)
        .digest("hex");

    // Find user with the email verification token
    const user = await User.findOne({
        verifyEmailToken,
        verifyEmailExpire: { $gt: Date.now() },
    });

    if (!user) {
        return next(
            new ErrorHandler("Invalid or expired email verification token", 400)
        );
    }

    // Update user's isVerified field to true
    user.isVerified = true;
    user.verifyEmailToken = undefined;
    user.verifyEmailExpire = undefined;
    await user.save({ validateBeforeSave: false });

    res.status(200).json({
        success: true,
        message: "Email verified successfully",
    });
});

//resend verification email
exports.resendVerificationEmail = catchAsyncErrors(async (req, res, next) => {
    const { email } = req.body;

    // Find the user with the specified email address
    const user = await User.findOne({ email });

    // Check if the user exists
    if (!user) {
        return next(new ErrorHandler("User not found", 404));
    }

    // Check if the user has already been verified
    if (user.isVerified) {
        return next(new ErrorHandler("User has already been verified", 400));
    }

    // Generate a new verification token for the user
    const verifyToken = user.getVerifyEmail();
    await user.save({ validateBeforeSave: false });

    // Send the verification email to the user
    // const verifyEmailUrl = `${req.protocol}://${req.get(
    //     "host"
    // )}/api/verify/${verifyToken}`;

    const verifyEmailUrl = `${process.env.FRONTEND_URL}/EmailVerification/${verifyToken}`;

    const message = `Your email verification token is :- \n\n ${verifyEmailUrl} \n\n If you have not requested this email then, please ingonore it`;

    try {
        await sendEmail({
            email: user.email,
            subject: `Data Intel Hub Email verification`,
            message,
        });
        res.status(200).json({
            success: true,
            message: `Verification email sent to ${user.email} successfully`,
        });
    } catch (error) {
        user.verifyEmailToken = undefined;
        user.verifyEmailExpire = undefined;
        await user.save({ validateBeforeSave: false });
        return next(new ErrorHandler(error.message, 500));
    }
});

//Login user
exports.loginUser = catchAsyncErrors(async (req, res, next) => {
    const { email, password } = req.body;
  
    //checking  user has given passwrord and email both
    if (!email || !password) {
        return next(new ErrorHandler("Please Enter Email and Password", 400));
    }
    const user = await User.findOne({ email }).select("+password");
    if (!user) {
        return next(new ErrorHandler("invalid Email or Password", 401));
    }

    if (!user.isVerified) {
        return next(
            new ErrorHandler("Please verify your email to login.", 401)
        );
    }

    //compare method is coming from userModel
    const isPasswordMatched = await user.comparePassword(password);

    if (!isPasswordMatched) {
        return next(new ErrorHandler("invalid Email or Password", 401));
    }

    const options = {
        expires: new Date(
            Date.now() + process.env.COOKIE_EXPIRE * 24 * 60 * 60 * 1000 // currenttime+2* 24*60*60*1000// it means it will be expired in 2 days if cookie expiry number is 2
        ),
        httpOnly: true,
    };

   

   
      const token = user.getJWTToken();

    res.status(200).cookie("token", token, options).json({
        success: true,
        message: "Login success",
        user,

        token,
    });

    // sendToken(user, 200, res);
});

//Logout
exports.logout = catchAsyncErrors(async (req, res, next) => {
    res.cookie("token", null, {
        expires: new Date(Date.now()),
        httpOnly: true,
    });

    res.status(200).json({
        success: true,
        message: "Logged out successfully",
    });
});

//Forgot password
exports.forgotPassword = catchAsyncErrors(async (req, res, next) => {
    console.log("req.body", req.body.email);
    const user = await User.findOne({ email: req.body.email });

    if (!user) {
        return next(new ErrorHandler("User not found", 404));
    }

    //Get ResetPassword Token
    const resetToken = user.getResetPasswordToken();

    await user.save({ validateBeforeSave: false });

    const resetPasswordUrl = `${process.env.FRONTEND_URL}/reset-password/${resetToken}`;
    // const resetPasswordUrl = `${req.protocol}://${req.get(
    //     "host"
    // )}/api/password/reset/${resetToken}`;

    const message = `Your password reset token is :- \n\n ${resetPasswordUrl} \n\n If you have not requested this email then, please ingonore it`;

    try {
        await sendEmail({
            email: user.email,
            subject: `EntrustUs Password Recovery`,
            message,
        });
        res.status(200).json({
            success: true,
            message: `Email sent to ${user.email} successfully`,
        });
    } catch (error) {
        user.resetPasswordToken = undefined;
        user.resetPasswordExpire = undefined;
        await user.save({ validateBeforeSave: false });
        return next(new ErrorHandler(error.message, 500));
    }
});

//reset password
exports.resetPassword = catchAsyncErrors(async (req, res, next) => {
    const resetPasswordToken = crypto
        .createHash("sha256")
        .update(req.params.token)
        .digest("hex");

    const user = await User.findOne({
        resetPasswordToken,
        resetPasswordExpire: { $gt: Date.now() },
    });

    if (!user) {
        return next(
            new ErrorHandler(
                "Rest Password Token is invalid or has been expired",
                400
            )
        );
    }

    if (req.body.password !== req.body.confirmPassword) {
        return next(new ErrorHandler("Password does not match", 400));
    }

    user.password = req.body.password;
    user.resetPasswordToken = undefined;
    user.resetPasswordExpire = undefined;

    await user.save();

    sendToken(user, 200, res);
});

//Get user detail for their profile
exports.getUserDetails = catchAsyncErrors(async (req, res, next) => {
    const user = await User.findById(req.user.id);
    res.status(200).json({
        success: true,
        user,
    });
});

//update user
exports.updateUser = catchAsyncErrors(async (req, res, next) => {
    // const newUserData = {
    //     name: req.body.name,
    //     email: req.body.name,
    // };
    // console.log(req.body);
    const user = await User.findByIdAndUpdate(req.user.id, req.body, {
        new: true,
        runValidators: true,
        useFindAndModify: false,
    });
    res.status(200).json({
        success: true,
        user,
    });
});

//update Password
exports.updatePassword = catchAsyncErrors(async (req, res, next) => {
    const user = await User.findById(req.user.id).select("+password");

    const isPasswordMatched = await user.comparePassword(req.body.oldPassword);
    if (!isPasswordMatched) {
        return next(new ErrorHandler("Old Password is incorrect", 400));
    }

    if (req.body.newPassword !== req.body.confirmPassword) {
        return next(new ErrorHandler("Password does not match", 400));
    }

    user.password = req.body.newPassword;
    await user.save();

    sendToken(user, 200, res);
});

//Get all users
//admin routes
exports.getAllUser = catchAsyncErrors(async (req, res, next) => {
    const users = await User.find();
    res.status(200).json({
        success: true,
        users,
    });
});
