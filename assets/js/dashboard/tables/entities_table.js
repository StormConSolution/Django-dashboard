import {createPagination} from './utils/utils'
import {createTable as dataEntityClassificationTable} from './data_table_modal_classification_entity'
import {getFilters} from "../helpers/filters"
import {update} from '../helpers/helpers'
export function createTable(page){
    update.startUpdate()
    let content = document.getElementById("entity-table-content");
    content.innerHTML = "";
    let pagination = document.getElementById("entity-table-pagination");
    pagination.innerHTML = ""
    let pageSize = document.getElementById("aspect-topic-table-page-size").value

    let filtersValues = getFilters() 
    let urlParams = new URLSearchParams({
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo,
        "languages": filtersValues.languages,
        "sources": filtersValues.sources
    })
    document.getElementById("entities-table-csv").href = `/api/entity-classification-count/${window.project_id}/?format=csv&` + urlParams
    fetch(`/api/entity-classification-count/${window.project_id}/?page=${page}&page-size=${pageSize}&` + urlParams)
    .then((response) => response.json())
    .then((data) => {
        for (let element of data.data) {
            let tr = document.createElement("tr");
            let row = `
        <td>
        <a href="#" class="data-link">${element.entityLabel}</a>
       </td>
       <td>
         ${element.classificationLabel}
       </td>
       <td class="text-center">
        <a class="info-button" style="cursor:pointer;" data-entity-id="${element.entityID}" data-classification-id="${element.classificationID}">${element.count}</a>
       </td>
        `;
            tr.innerHTML = row;
            let dataButton = tr.querySelector(".info-button")
            dataButton.addEventListener("click", (e)=>{
                let entityID = e.target.getAttribute("data-entity-id")
                let classificationID = e.target.getAttribute("data-classification-id")
                document.querySelector("#data-table-modal").style.display = "block"
                dataEntityClassificationTable(1, classificationID, entityID)
            })
            content.append(tr);
        }
        let firstElement = data.pageSize * (data.currentPage - 1);
        let lastElement = firstElement + data.pageSize;
        createPagination(firstElement, lastElement, data.total, data.currentPage, data.totalPages, pagination, createTable);
        update.finishUpdate()
    });
}
//createTable(1);