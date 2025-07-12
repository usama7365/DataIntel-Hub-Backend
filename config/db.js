const mongoose = require("mongoose");

// export const connectDatabase = () => {
//     try {
//         mongoose.set("strictQuery", false);
//         mongoose.connect(process.env.MONGO_URI, () => {
//             // console.log(process.env.DATABASE_URL);
//             console.log("Connected to database...");
//         });
//     } catch (error) {
//         console.log(error);
//     }
// };

const connnectDatabase = () => {
    mongoose.set("strictQuery", false);

    mongoose
        .connect(process.env.MONGO_URI, {
            useNewUrlParser: true,
            useUnifiedTopology: true,
            // useCreateIndex: true,
        })
        .then((data) => {
            console.log(
                `MongoDb connected with server:${data.connection.host}`
            );
        });
};
//done this error handling in server.js
// mongoose.connection.on("error", (err) => {
//     console.log("mongodb runtime error", err);
// });

module.exports = connnectDatabase;
