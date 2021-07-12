import {createPagination} from './utils/utils'
import {createTable as dataEntityClassificationTable} from './data_table_modal'
import {update, manageTableOrderFilters} from '../helpers/helpers'
import wordCloud from '../graphs//word-cloud-modal'
import { metadataFiltersURL , normalFiltersURL, orderFilters} from "../helpers/filters";
let content = document.getElementById("entity-table-content");
let pageSizeDropdown = document.getElementById("entity-table-page-size") 

let table = document.querySelector("[data-graph-table='entities-table']")
manageTableOrderFilters(table, createTable)
export function createTable(page){
    update.startUpdate()
    content.innerHTML = "Loading...";
    let pagination = document.getElementById("entity-table-pagination");
    pagination.innerHTML = ""
    let pageSize = pageSizeDropdown.value

    let urlParams = metadataFiltersURL()+ "&" + normalFiltersURL()
    document.getElementById("entities-table-csv").href = `/api/entity-classification-count/${window.project_id}/?format=csv&` + urlParams
    fetch(`/api/entity-classification-count/${window.project_id}/?page=${page}&page-size=${pageSize}&` + urlParams + "&" + orderFilters(table))
    .then((response) => response.json())
    .then((data) => {
        content.innerHTML = ""
        for (let element of data.data) {
            let tr = document.createElement("tr");
            let row = `
        <td>${element.entityLabel}</td>
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
                let wordCloudURL =  `/api/data-per-classification-and-entity/${window.project_id}/?format=word-cloud&classification=${classificationID}&entity=${entityID}&` +  metadataFiltersURL()+ "&" + normalFiltersURL()
                let options = {}
                options.csvURL =`/api/data-per-classification-and-entity/${window.project_id}/?format=csv&` + new URLSearchParams({
                    "entity": entityID,
                    "classification": classificationID,
                })+ "&" +  metadataFiltersURL() + "&" + normalFiltersURL()
                options.dataURL = `/api/data-per-classification-and-entity/${window.project_id}/?` + new URLSearchParams({
                    "entity": entityID,
                    "classification": classificationID, 
                })+ "&" +  metadataFiltersURL()+ "&" + normalFiltersURL()
                wordCloud(wordCloudURL)
                dataEntityClassificationTable(1, options)
            })
            content.append(tr);
        }
        let firstElement = data.pageSize * (data.currentPage - 1) + 1;
        let lastElement = firstElement + data.pageSize - 1;
        createPagination(firstElement, lastElement, data.total, data.currentPage, data.totalPages, pagination, createTable);
        update.finishUpdate()
    });
}
pageSizeDropdown.addEventListener("change", ()=>{
    createTable(1)
})
//createTable(1);
