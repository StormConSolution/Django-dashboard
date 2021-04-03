export function getFilters(){
    let dateFrom = document.getElementById("date-from").value
    let dateTo = document.getElementById("date-to").value

    return {
        dateFrom: dateFrom,
        dateTo: dateTo
    }
}