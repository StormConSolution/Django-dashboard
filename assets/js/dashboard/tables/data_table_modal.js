import {getFilters, orderFilters} from "../helpers/filters"
import {manageTableOrderFiltersWithOptions} from '../helpers/helpers'
import {createPagination} from './utils/utils'
let optionsState = {}

let table = document.querySelector("#data-items")
export function createTable(page, options){

    optionsState = options
    manageTableOrderFiltersWithOptions(table, createTable, optionsState)
    console.log(options)
    let content = document.getElementById("data-table-modal-content");
    content.innerHTML = "";
    let pagination = document.getElementById("data-table-modal-pagination");
    pagination.innerHTML = ""
    let pageSize = document.getElementById("data-table-modal-page-size").value
    document.getElementById("data-modal-table-csv").href = options.wordCloudURL
    fetch(options.dataURL + `&page-size=${pageSize}&page=${page}` + "&" + orderFilters(table))
    .then((response) => response.json())
    .then((data) => {
        for (let element of data.data) {
            let tr = document.createElement("tr");
            var length = 150;
            let text = "";
            if(element.text.length > length){
                text = element.text.substring(0, length) + "...";
            } else {
                text = element.text
            }
            let row = `
        <td>
        <small>${element.dateCreated}</small>
       </td>
       <td>
         ${text}
       </td>
       <td >
        <b><a href="${element.url}">${element.sourceLabel}</a></b>
       </td>
       <td class="text-center">
         ${element.sentimentValue.toFixed(4)}
       </td>
       <td class="text-center">
         <a href="#" class="info-button">${element.languageCode}</a>
       </td>
        `;
            tr.innerHTML = row;
            content.append(tr);
        }
        let firstElement = data.pageSize * (data.currentPage - 1) + 1;
        let lastElement = firstElement + data.pageSize - 1;
        createPagination(firstElement, lastElement, data.total, data.currentPage, data.totalPages, pagination, createTable, options);
    });
}

document.getElementById("data-table-modal-page-size").addEventListener("change",()=>{
    createTable(1, optionsState)
})
