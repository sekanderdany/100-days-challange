let express = require('express');
let path = require('path');
let fs = require('fs');
let MongoClient = require('mongodb').MongoClient;
let bodyParser = require('body-parser');
let app = express();

app.use(bodyParser.urlencoded({
  extended: true
}));
app.use(bodyParser.json());

app.get('/', function (req, res) {
    res.sendFile(path.join(__dirname, "index.html"));
  });

app.get('/profile-picture', function (req, res) {
  let img = fs.readFileSync(path.join(__dirname, "images/profile-1.jpg"));
  res.writeHead(200, {'Content-Type': 'image/jpg' });
  res.end(img, 'binary');
});

// use when starting application locally with node command
let mongoUrlLocal = "mongodb://admin:password@localhost:27017";

// use when starting application as docker container, part of docker-compose
let mongoUrlDockerCompose = "mongodb://admin:password@mongodb";

// pass these options to mongo client connect request to avoid DeprecationWarning for current Server Discovery and Monitoring engine
let mongoClientOptions = { 
  useNewUrlParser: true, 
  useUnifiedTopology: true,
  serverSelectionTimeoutMS: 5000 // Timeout after 5 seconds instead of 30
};

// "user-account" in demo with docker
let databaseName = "user-account";
let collectionName = "users";

app.get('/get-profile', function (req, res) {
  let response = {};
  // Connect to the db using local application or docker compose variable in connection properties
  MongoClient.connect(mongoUrlLocal, mongoClientOptions, function (err, client) {
    if (err) {
      console.log('MongoDB connection error:', err.message);
      // Return empty profile if MongoDB is not available
      return res.send({});
    }

    let db = client.db(databaseName);

    let myquery = { userid: 1 };

    db.collection(collectionName).findOne(myquery, function (err, result) {
      if (err) {
        console.log('MongoDB query error:', err.message);
        client.close();
        return res.send({});
      }
      response = result;
      client.close();

      // Send response
      res.send(response ? response : {});
    });
  });
});

app.post('/update-profile', function (req, res) {
  let userObj = req.body;
  // Connect to the db using local application or docker compose variable in connection properties
  MongoClient.connect(mongoUrlLocal, mongoClientOptions, function (err, client) {
    if (err) {
      console.log('MongoDB connection error:', err.message);
      // Return the user object even if MongoDB is not available
      return res.send(userObj);
    }

    let db = client.db(databaseName);
    userObj['userid'] = 1;

    let myquery = { userid: 1 };
    let newvalues = { $set: userObj };

    db.collection(collectionName).updateOne(myquery, newvalues, {upsert: true}, function(err, result) {
      if (err) {
        console.log('MongoDB update error:', err.message);
      }
      client.close();
      // Send response after MongoDB operation completes
      res.send(userObj);
    });

  });
});

app.listen(3000, function () {
  console.log("app listening on port 3000!");
});

