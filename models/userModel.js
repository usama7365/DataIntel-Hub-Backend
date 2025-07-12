const mongoose = require("mongoose");
const validator = require("Validator");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const crypto = require("crypto");
const userSchema = new mongoose.Schema({
    firstName: {
        type: String,
        required: [true, "Please Enter your first name"],
    },
    lastName: {
        type: String,
        required: [true, "Please Enter your last name"],
    },
    email: {
        type: String,
        unique: true,
        required: [true, "Please Enter your email"],
        validate: [validator.isEmail, "Please Enter a valid Email"],
    },
   
    password: {
        type: String,
        required: [true, "Please Enter your password"],

        minLength: [8, "Password should be greater than 8 characters"],
        select: false,
    },

    role: {
        type: String,
        default: "user",
    },
    isVerified: { type: Boolean, default: false },
    resetPasswordToken: String,
    resetPasswordExpire: Date,
    verifyEmailToken: String,
    verifyEmailExpire: Date,
});

//event for password encryption
userSchema.pre("save", async function (next) {
    if (!this.isModified("password")) {
        next();
    }

    this.password = await bcrypt.hash(this.password, 10);
});

//JWT TOKEN
userSchema.methods.getJWTToken = function () {
    return jwt.sign({ id: this._id }, process.env.JWT_SECRET, {
        expiresIn: process.env.JWT_EXPIRE,
    });
};

//Comparing password with database
userSchema.methods.comparePassword = async function (enteredPassword) {
    return await bcrypt.compare(enteredPassword, this.password);
};

//Generating password reset token

userSchema.methods.getResetPasswordToken = function () {
    //Generating token
    const resetToken = crypto.randomBytes(20).toString("hex");

    // Hashing and adding resetPasswordToken to userSchema
    this.resetPasswordToken = crypto
        .createHash("sha256")
        .update(resetToken)
        .digest("hex");

    //expiring token
    this.resetPasswordExpire = Date.now() + 15 * 60 * 1000;

    return resetToken;
};

userSchema.methods.getVerifyEmail = function () {
    //generating token
    const verifyToken = crypto.randomBytes(20).toString("hex");

    // Hashing and adding verifyEmailToken to userSchema
    this.verifyEmailToken = crypto
        .createHash("sha256")
        .update(verifyToken)
        .digest("hex");

    this.verifyEmailExpire = Date.now() + 24 * 60 * 60 * 1000; // Token expires after 24 hours

    return verifyToken;
};

module.exports = mongoose.model("User", userSchema);
