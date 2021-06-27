import {openGuestModalWithID, openGuestModal} from './guest/modal'

document.querySelectorAll("[data-role='delete-sentiment']").forEach((element) => {
    element.addEventListener("click", (e) => {
        openGuestModal()
    })
})

document.querySelectorAll("[data-role='edit-sentiment-button']").forEach((element) => {
    element.addEventListener("click", (e) => {
        openGuestModal()
    })
})

document.querySelector("#show-test-sentiment-modal").addEventListener("click", (e)=>{
    openGuestModal()
})

document.querySelector("#create-sentiment-button").addEventListener("click", (e)=>{
    openGuestModal()
})