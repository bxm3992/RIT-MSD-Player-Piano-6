const http = require('http');
const express = require('express');
const app = express();
const server = http.createServer(app);
const io = require('socket.io').listen(server);
const fs = require('fs');
const path = require('path');
const router = express.Router();
app.use(express.static("static"));

// Request route to index.html file located in the static/ directory
router.get('/',function(req,res){
    res.sendfile(path.join(__dirname+'/static/index.html'));
});

//Add the router
app.use('/', router);
server.listen(3000, '127.0.0.1');

console.log('Running at Port 0.0.0.0:3000');
let rawData = fs.readFileSync('json/library.json'); // Library Link: Song List
let allSongs = JSON.parse(rawData);
//console.log(allSongs); // PRINT: LIBRARY LIST
var currSongProc;
io.on('connection', function(socket){
    console.log('User connected...');

    // Provide the browser with a list of all available songs
    socket.on('request library', function (data) {
        //console.log(data);
        let library = JSON.parse(rawData);
        //console.log(library[0].duration);
        socket.emit('send library', library);
    });

    socket.on('request songpreproc', function(songname, tempo) {
        console.log(songname, tempo);  // Song name and tempo provided
        currSongProc = false; // Instantiate child process as 'false' for redundancy check

        const { spawn } = require('child_process');

        const reset = spawn('python3', ['play_midi.py', 'reset']); // play_midi.py reset
        reset.stdout.on('data', function(data) {
            console.log(String(data));
        });


        const tempoThread = spawn('python3', ['play_midi.py', 'tempo', songname]); // play_midi.py tempo
        tempoThread.stdout.on('data', function(data) {
            // Convert to string and emit tempo back to webpage
            console.log(String(data));
            socket.emit('send songpreproc', String(data));
        });

        currSongProc = spawn('python3', ['play_midi.py', 'play', songname]); // play_midi.py play 'songname' tempo
        currSongProc.stdout.on('data', function(data) {
            console.log(String(data));
        });

        //socket.emit('send songpreproc', tempo);
    });

    // Reset the whole system in a separate procedure
    socket.on('request reset', (data) => {
        //console.log(data);  // Nothing should be provided, but I'm curious to see what if any
        console.log("SONG RESET");
        if (currSongProc !== false) {
            currSongProc.kill('SIGINT');
        }
        const { spawn } = require('child_process');
        const reset = spawn('python3', ['play_midi.py', 'reset']); // play_midi.py reset

        socket.emit('send reset', 'exit');

        currSongProc = false;
    });

    // Create a file to play
    // Perform the Play action and play the song -- NOTE: currently done via file polling - TODO: convert to django framework
    // 'p' file is created to continue to play while 'x' file creation exits the python script
    socket.on('request play', (data) => {
        fs.open('p', 'w', function (err, file) {
            if (err) throw err;
            console.log('Created');
        });

        socket.emit('send play', 'exit');
    });
});