export let update = {
    startUpdate: startUpdate,
    finishUpdate: finishUpdate,
    canUpdate: canUpdate
}
function startUpdate(){
    updateCount++
    console.log(updateCount)
}

function finishUpdate(){
    updateCount--
    console.log(updateCount)
}

function canUpdate(){
    if(updateCount ===  0){
        return true
    }
    return false
}
let updateCount = 0

export function hideAllGraphsTables(){
    document.querySelectorAll("[data-role='graph-table-container']").forEach((element) => {
        element.style.display="none"
    })
}

export function showGraphTable(data_graph_table){
    document.querySelector(`[data-graph-table="${data_graph_table}"]`).style.display="block"
}