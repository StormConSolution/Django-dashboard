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