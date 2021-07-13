import {openGuestModalWithID, openGuestModal} from './guest/modal'
openGuestModalWithID("new-alert-rule")
document.querySelectorAll('[data-role="delete-alert"]').forEach((e) => {
    e.addEventListener("click", (e) => {
        openGuestModal()
    })
})

document.querySelectorAll('[data-role="edit-alert-button"]').forEach((element) => {
    element.addEventListener("click", (e) => {
        openGuestModal()
    })
})

document.querySelectorAll('[data-role="toggle-alert-rule"]').forEach((element) => {
    element.addEventListener("click", (e) => {
        e.preventDefault()
        openGuestModal()
    })
})
