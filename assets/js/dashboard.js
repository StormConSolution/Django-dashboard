import "./common/navbar"

$("#export-comments-source").change((e)=>{
    let placeholder = $(e.currentTarget).find(":selected").attr("data-placeholder")
    $("#export-comments-url").attr("placeholder", "e.g. " + placeholder)
})
/* document.querySelector("#export-comments-source").addEventListener("change",()=>{
    console.log("test")
}) */
