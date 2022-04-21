addEventListener("message", event => {
    let pianoArray = event.data;
    getArrayData(pianoArray);
});

function getArrayData(array) {
    var keysDown = array[0];
    var pianoKeys88 = array[1];
    
}