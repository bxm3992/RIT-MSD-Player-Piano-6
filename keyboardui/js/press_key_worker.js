addEventListener("message", event => {
    let pianoArray = event.data;
    getArrayData(pianoArray);
});

function getArrayData(array) {
    var keyArray = array[0];
    var keysDown = array[1];
    var pianoKeys88 = array[2];
    switch(keyArray[0]) {
        case 0:
            break;
        default:
            var keyNumber = 1;
			if (keysDown[keyNumber]) return ;
			keysDown[keyNumber] = true;
			var keys = Object.keys(keysDown);
			for (var j = 0; j < keys.length; j++) {
				var key = keys[j];
				pianoKeys88[key - 1].down();
			};
            modifyKey = pianoKeys88[keyNumber - 1].element;
            postMessage(modifyKey);
            break;
    }
    switch(keyArray[1]) {
        case 0:
            break;
        default:
            var keyNumber = 2;
			if (keysDown[keyNumber]) return ;
			keysDown[keyNumber] = true;
			var keys = Object.keys(keysDown);
			for (var j = 0; j < keys.length; j++) {
				var key = keys[j];
				pianoKeys88[key - 1].down();
			};
            modifyKey = pianoKeys88[keyNumber - 1].element;
            postMessage(modifyKey);
            break;
    }
    switch(keyArray[2]) {
        case 0:
            break;
        default:
            var keyNumber = 3;
			if (keysDown[keyNumber]) return ;
			keysDown[keyNumber] = true;
			var keys = Object.keys(keysDown);
			for (var j = 0; j < keys.length; j++) {
				var key = keys[j];
				pianoKeys88[key - 1].down();
			};
            modifyKey = pianoKeys88[keyNumber - 1].element;
            postMessage(modifyKey);
            break;
    }
    switch(keyArray[3]) {
        case 0:
            break;
        default:
            var keyNumber = 4;
			if (keysDown[keyNumber]) return ;
			keysDown[keyNumber] = true;
			var keys = Object.keys(keysDown);
			for (var j = 0; j < keys.length; j++) {
				var key = keys[j];
				pianoKeys88[key - 1].down();
			};
            modifyKey = pianoKeys88[keyNumber - 1].element;
            postMessage(modifyKey);
            break;
    }
    switch(keyArray[4]) {
        case 0:
            break;
        default:
            var keyNumber = 5;
			if (keysDown[keyNumber]) return ;
			keysDown[keyNumber] = true;
			var keys = Object.keys(keysDown);
			for (var j = 0; j < keys.length; j++) {
				var key = keys[j];
				pianoKeys88[key - 1].down();
			};
            modifyKey = pianoKeys88[keyNumber - 1].element;
            postMessage(modifyKey);
            break;
    }
}