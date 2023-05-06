var boxes = document.querySelectorAll(".box");

function revealBoxes() {
  for (var i = 0; i < boxes.length; i++) {
    var box = boxes[i];
    var boxTop = box.getBoundingClientRect().top;
    var windowBottom = window.innerHeight;
    
    if (boxTop < windowBottom) {
      box.classList.add("reveal");
    }
  }
}

window.addEventListener("scroll", revealBoxes);