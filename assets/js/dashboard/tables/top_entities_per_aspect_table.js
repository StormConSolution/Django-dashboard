import {createPagination} from './utils/utils'
import {createTable as dataEntityClassificationTable} from './data_table_modal'
import {update, manageTableOrderFilters} from '../helpers/helpers'
import wordCloud from '../graphs/word-cloud-modal'
import { metadataFiltersURL , normalFiltersURL, orderFilters} from "../helpers/filters";
let content = document.getElementById("top-entities-per-aspect-table-content");
let firstRun = true
let aspectLabel = ""
let selectAspect = document.querySelector("#top-entities-per-aspect-table-aspect")
let pageSizeDropdown = document.querySelector("#top-entities-per-aspect-table-page-size")

let table = document.querySelector("[data-graph-table='top-entities-per-aspect-table']")
manageTableOrderFilters(table, createTable)

export function createTable(page){
    if(firstRun){
        update.startUpdate()
        let urlParams = new URLSearchParams({
            "order-by":"label",
        })+ "&" +  metadataFiltersURL()+ "&" + normalFiltersURL()
        fetch(`/api/aspect-count/${window.project_id}/?` + urlParams).then(response => response.json()).then(data => {
            let first = true
            for(let element of data){
                let option  = document.createElement("option")
                option.value = element.aspectLabel
                option.innerHTML = element.aspectLabel
                selectAspect.append(option)
                if(first){
                    aspectLabel = element.aspectLabel
                    first = false
                    option.selected = true
                }
            }
            createTable(page)
        })
        update.finishUpdate()
        firstRun = false
    } else {
        update.startUpdate()
        aspectLabel = selectAspect.value
        content.innerHTML = "Loading...";
        let pagination = document.getElementById("top-entities-per-aspect-table-pagination");
        pagination.innerHTML = ""
        let pageSize = pageSizeDropdown.value
    
        let urlParams = metadataFiltersURL()+ "&" + normalFiltersURL()
        document.getElementById("top-entities-per-aspect-table-csv").href = `/api/entity-classification-count/${window.project_id}/?format=csv&aspect-label${aspectLabel}&` + urlParams
        fetch(`/api/entity-classification-count/${window.project_id}/?page=${page}&page_size=${pageSize}&` + urlParams + "&" + orderFilters(table))
        .then((response) => response.json())
        .then((data) => {
            content.innerHTML = ""
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
                    let selectAspect = document.querySelector("#top-entities-per-aspect-table-aspect").value
                    let wordCloudURL = `/api/data-per-classification-and-entity/${window.project_id}/?format=word-cloud&classification=${classificationID}&entity=${entityID}&aspect-label=${selectAspect}&` + metadataFiltersURL()+ "&" + normalFiltersURL()
                    let options = {}
                    options.csvURL =`/api/data-per-classification-and-entity/${window.project_id}/?format=csv&` + new URLSearchParams({
                        "aspect-label": selectAspect,
                        "entity": entityID, 
                        "classification": classificationID,
                    }) + "&" +  metadataFiltersURL()+ "&" + normalFiltersURL()
                    options.dataURL =`/api/data-per-classification-and-entity/${window.project_id}/?` + new URLSearchParams({
                        "aspect-label": selectAspect,
                        "entity": entityID, 
                        "classification": classificationID,
                    }) + "&" +  metadataFiltersURL()+ "&" + normalFiltersURL()
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
}
selectAspect.addEventListener("change", () =>{
    createTable(1)
})
pageSizeDropdown.addEventListener("change", () =>{
    createTable(1)
})
//createTable(1);