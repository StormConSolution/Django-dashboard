export let update = {
    startUpdate: startUpdate,
    finishUpdate: finishUpdate,
    canUpdate: canUpdate
}
function startUpdate(){
    updateCount++
}

function finishUpdate(){
    updateCount--
}

function canUpdate(){
    if(updateCount ===  0){
        return true
    }
    return false
}
let updateCount = 0

export function createHTMLForGraphsContainer(html){
    let container = document.querySelector("#graphs-container")
    let div = document.createElement("div")
    div.className = "col-12 project-card"
    div.innerHTML = html
    container.append(div)
}

export function resetGraphsTablesContainer(){
    let container = document.querySelector("#graphs-container")
    container.innerHTML = ""
}