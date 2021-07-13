export let update = {
    startUpdate: startUpdate,
    finishUpdate: finishUpdate,
    canUpdate: canUpdate
}
function startUpdate() {
    updateCount++
}

function finishUpdate() {
    updateCount--
}

function canUpdate() {
    if(updateCount ===  0) {
        return true
    }
    return false
}
let updateCount = 0

export function hideAllGraphsTables() {
    document.querySelectorAll("[data-role='graph-table-container']").forEach((element) => {
        element.style.display = "none"
    })
}

export function showGraphTable(data_graph_table) {
    document.querySelector(`[data-graph-table="${data_graph_table}"]`).style.display="block"
}

function removeActiveFromClass(elements){
    elements.forEach((element)=>{
       element.classList.remove("active")
    })
}

export function manageTableOrderFilters(table, createTable){
    let orderElements = table.querySelectorAll("[data-order-by]")

    //add "active" to element class when arrows to order are clicked 
    orderElements.forEach((element)=>{

        element.addEventListener("click",(e)=>{

            //remove previous active
            removeActiveFromClass(orderElements)

            let currentTarget = e.currentTarget
            currentTarget.classList.add("active")
            createTable(1)
        })
    })
}

export function manageTableOrderFiltersWithOptions(table, createTable, options){
    let orderElements = table.querySelectorAll("[data-order-by]")

    //add "active" to element class when arrows to order are clicked 
    orderElements.forEach((element)=>{
        let clone = element.cloneNode(true);
    
        element.parentNode.replaceChild(clone, element);

    })


    orderElements = table.querySelectorAll("[data-order-by]")
    orderElements.forEach((element)=>{
        element.addEventListener("click",(e)=>{

            //remove previous active
            removeActiveFromClass(orderElements)
    
            let currentTarget = e.currentTarget
            currentTarget.classList.add("active")
            createTable(1, options)
        })
    })

}