// $(function() {
//   $("p").click(function() {
//     alert("hello")
//   })
//   // var ul = document.getElementById("list")
//   // var list = ul.getElementsByTagName("li")
//   // for (var i = 0; i < list.length; i++) {
//   // var elem = list[i]
//   //   elem.onclick = function() {
//   //   alert("this is"+i)
//   //   }
//   // }
// })

function load_a_note(id) {
  $.getJSON('main', {note_id: id},function(data) {
    // document.getElementById("t").innerText=data.note
  });
  alert(id)
}

function doPost(id) {  // to:提交动作（action）,p:参数
  alert(1)
  var myForm = document.createElement("form");
  myForm.method = "post";
  // for (var i in p){
  var myInput = document.createElement("input");
  myInput.setAttribute("note_id", "1");  // 为input对象设置name
  alert(2)
  myForm.appendChild(myInput);
  // }
  alert(3)
  document.body.appendChild(myForm);
  myForm.submit();
  document.body.removeChild(myForm);  // 提交后移除创建的form
  window.document = "hello"

}


