import {createPagination} from './utils/utils'
import {createTable as dataEntityClassificationTable} from './data_table_modal_classification_entity'
import {getFilters} from "../helpers/filters"
import {update, createHTMLForGraphsContainer as createHTML} from '../helpers/helpers'
let html = 
`
<div class="col-12 project-card" id="entity-table">
    <div class="project-card-inner">
    <div class="chart-title align-items-center d-flex flex-wrap">
        <h4 class="col p-0">Entities <a href="#" data-toggle="tooltip" data-placement="top" title="Need help?">
            <i class="fe fe-help-circle"></i>
        </a> </h4>
        <div class="col-auto p-0 d-flex flex-wrap ">
        <div class="per-page align-items-center d-flex">
        Show <select class="custom-select" id="entity-table-page-size">
            <option value="10" selected>10</option>
            <option value="20">20</option>
            <option value="30">30</option>
            <option value="40">40</option>
        </select> Entries
        </div>
        <div class="data-search">
        <input type="text" class="form-control " placeholder="Search">
        </div>
        <a style="margin-left:1rem;display:flex;align-items:center;cursor:pointer;" id="entities-table-csv" target="_blank">Download CSV</a>
        </div>
    </div>
    <div class="data-table table-responsive">
        <table class="table table-striped table-borderless">
        <thead>
            <tr>
            <th scope="col">
                ENTITY <span class="data-short">
                <a href="#" class="active">
                    <i class="fe fe-chevron-up"></i>
                </a>
                <a href="#">
                    <i class="fe fe-chevron-down"></i>
                </a>
                </span>
            </th>
            <th scope="col">
                CLASSIFICATIONS <span class="data-short">
                <a href="#">
                    <i class="fe fe-chevron-up"></i>
                </a>
                <a href="#">
                    <i class="fe fe-chevron-down"></i>
                </a>
                </span>
            </th>
            <th scope="col" class="text-center" >
                FREQUENCY <span class="data-short">
                <a href="#">
                    <i class="fe fe-chevron-up"></i>
                </a>
                <a href="#">
                    <i class="fe fe-chevron-down"></i>
                </a>
                </span>
            </th>
            </tr>
        </thead>
        <tbody id="entity-table-content">
        </tbody>
        </table>
    </div>
    <div class="table-bottom" id="entity-table-pagination">
    </div>
    </div>
</div>
`
export function createTable(page){
    createHTML(html)
    let content = document.getElementById("entity-table-content");
    update.startUpdate()
    content.innerHTML = "Loading...";
    let pagination = document.getElementById("entity-table-pagination");
    pagination.innerHTML = ""
    let pageSize = document.getElementById("entity-table-page-size").value

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