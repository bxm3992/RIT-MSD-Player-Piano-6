// // const getBox = document.querySelector('#box');

// // if (window.Worker) {
// //     const myWorker = new Worker("worker.js");
  
// //     getBox.onchange = function() {
// //       myWorker.postMessage();
// //       console.log('Message posted to worker');
// //     }
  
// //   } else {
// //     console.log('Your browser doesn\'t support web workers.');
// //   }

// // function changeColor (box) {
// //     const element = document.querySelector(box)
// //     element.style.backgroundColor = 'black';
// //     if (element.style.backgroundColor == 'black') {
// //         element.style.backgroundColor = 'pink';
// //     } else {
// //         element.style.backgroundColor = 'black';
// //     }
// // }

// var pink = false;
// var i = 0;
// const keyArray = [0, 1, 1, 0];
// $(document).ready(function () {
//     $("#btn").click(function () {
//         if (i == keyArray.length - 1) {
//             i = 0;
//         }
//         if (keyArray[i] == 1) {
//             $("#box").css("background-color", "black");
//             console.log("It went here.");
//             i++;
//         } else {
//             $("#box").css("background-color", "pink");
//             console.log("It also went here.");
//             i++;
//         }
//     });
// });

// var xhr = new XMLHttpRequest();
// xhr.open("GET", "test.py", true);
// xhr.responseType = "JSON";
// xhr.onload = function(e) {
//     var arrOfStrings = JSON.parse(JSON.stringify(xhr.response));
// }
// xhr.send();

function postData(input) {
    $.ajax({
        type: "POST",
        url: "http://127.0.0.1:5000/",
        data: { param: input },
        success: callbackFunc
    });
}

function callbackFunc(response) {
    // do something with the response
    console.log(response + " and acknowledged!")
}

postData("Hello from AJAX Javascript!");
