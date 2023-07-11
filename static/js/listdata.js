const rooturl="http://localhost:5000/"
const tablerow=document.getElementById("table-row")
document.addEventListener("DOMContentLoaded", function() {
        data="{{url_for('static', filename='mingcute_delete-line.svg')}}"
        size=0
       fetch(rooturl+"admin/firstsize",{
        method: "GET",
        headers: {
          "Content-type": "application/json; charset=UTF-8"
        }
      }).then((response)=>response.json()).then((json)=>{
        size=json["data"];
      })
      fetch(rooturl+"admin/getdata",{
        method: "GET",
        headers: {
          "Content-type": "application/json; charset=UTF-8"
        }
      }).then((response)=>response.json()).then((json)=>{
            let mapped= json["data"].map((val)=>{return `<tr><td>${val["id"]}</td><td>${val["pertanyaan"]}</td><td>${val["jawaban"]}</td><td><img></img><img></img></td></tr>`});
            tablerow.innerHTML=mapped.join("");
      })
})