const express = require("express");
const app = express();
const cors = require("cors");
const bodyParser = require("body-parser");
const cookieParser = require("cookie-parser");

const errorMiddleWare = require("./middleware/error");

app.use(express.json());
app.use(cookieParser());

// parse requests of content-type - application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({ extended: true }));

// parse requests of content-type - application/json
app.use(bodyParser.json());

app.use(
    cors({
        origin: true,
        credentials: true,
    })
);

const user = require("./routes/userRoutes");
//User Routes
app.use("/api", user);

//data-input

//Middleware of errors
app.use(errorMiddleWare);

module.exports = app;
