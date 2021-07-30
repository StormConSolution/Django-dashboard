let createEntityModal = document.querySelector("#create-entity")
document.querySelector('#create-entity-button').addEventListener('click',()=>{
    $('#create-entity').modal()
})


document.querySelectorAll('[data-role="delete-entity"]').forEach((e) => {
    e.addEventListener("click", (e) => {
        let entityID = e.currentTarget.getAttribute("data-entity-id")
        fetch("/entity/" + entityID + "/", { method: "DELETE" }).then(response => {
            if (response.status == 200) {
                location.reload()
            } else {
                alert("Error deleting entity")
            }
        })
    })
});

