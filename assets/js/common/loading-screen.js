let loadingSCreenDiv = document.querySelector("#loading-screen")
export function showLoadingScreen(){
    loadingSCreenDiv.style.display = "block"
}

export function hideLoadingScreen(){
    loadingSCreenDiv.style.display = "none"
}