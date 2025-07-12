//creating token and saving in cookie
const sendToken = (user, statusCode, res) => {
    const token = user.getJWTToken();

    //options for cookie to send token to cookie
    const options = {
        expires: new Date(
            Date.now() + process.env.COOKIE_EXPIRE * 24 * 60 * 60 * 1000 // currenttime+2* 24*60*60*1000// it means it will be expired in 2 days if cookie expiry number is 2
        ),
        httpOnly: true,
    };

    res.status(statusCode).cookie("token", token, options).json({
        success: true,
        user,
        token,
    });
};

module.exports = sendToken;
