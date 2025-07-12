const app = require("./app");
const cors = require("cors");

const dotenv = require("dotenv");
const connnectDatabase = require("./config/db.js");

// Handling Uncaught Exception
process.on("uncaughtException", (err) => {
    console.log(`Error: ${err.message}`);
    console.log(`Shutting down the server due to Uncaught Exception`);
    process.exit(1);
});
// shuaib;

//Config path
dotenv.config();

//Connecting Database
connnectDatabase();

app.use(
    cors({
        origin: true,
        credentials: true,
    })
);

//creating server
const server = app.listen(process.env.PORT, () => {
    console.log(`Server is working on http://localhost:${process.env.PORT}`);
});

// Unhandled Promise Rejection
process.on("unhandledRejection", (err) => {
    console.log(`Error: ${err.message}`);
    console.log(`Shutting down the server due to Unhandled Promise Rejection`);

    server.close(() => {
        process.exit(1);
    });
});
