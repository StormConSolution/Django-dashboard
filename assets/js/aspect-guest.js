import {openGuestModalWithID, openGuestModal} from './guest/modal'

openGuestModalWithID('create-aspect-model')
openGuestModalWithID('test-aspect-button')

document.querySelectorAll("[data-role='edit-aspect-button']").forEach((element) => {
    element.addEventListener("click", (e) => {
        openGuestModal()
    })
})

document.querySelectorAll("[data-role='delete-aspect']").forEach((element) => {
    element.addEventListener("click", (e) => {
        openGuestModal()
    })
})