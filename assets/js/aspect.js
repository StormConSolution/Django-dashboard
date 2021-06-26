import "./aspect/aspect-modal"

document.querySelectorAll('[data-role="edit-aspect-button"]').forEach((element) => {

    element.addEventListener("click", (e) => {
        let modal = document.querySelector("#edit-aspect")
        modal.style.display = "block"
        createAspectEditModal(element.getAttribute("data-aspect-id"))
    })
})
document.querySelectorAll('[data-role="delete-aspect-rule"]').forEach((element) => {
    element.addEventListener("click", (e) => {
        e.currentTarget.parentNode.parentNode.remove()
        count_rules--
    })
})
document.querySelectorAll('[data-role="delete-aspect"]').forEach((e) => {
    e.addEventListener("click", (e) => {
        let aspectId = e.currentTarget.getAttribute("data-aspect-id")
        fetch("/aspect/" + aspectId + "/", { method: "DELETE" }).then(response => {
            if (response.status == 200) {
                location.reload()
            } else {
                alert("Error deleting aspect")
            }
        })
    })
})
document.querySelector("#test-aspect-button").addEventListener("click", ()=>{
    $("#test-aspect-modal").modal()
})
document.querySelector('#create-aspect-model').addEventListener('click',()=>{
    console.log("test")
    $('#createaspect').modal()
})