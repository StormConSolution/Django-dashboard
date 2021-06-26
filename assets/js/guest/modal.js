export function openGuestModalWithID(id){
    document.querySelector(`#${id}`).addEventListener("click", ()=>{
        openGuestModal()
    })
}

export function openGuestModal(){
    $('#guest-modal-message').modal()
}