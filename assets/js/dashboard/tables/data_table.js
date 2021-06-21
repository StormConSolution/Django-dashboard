import {createPagination} from './utils/utils'
import {update} from '../helpers/helpers'
import wordCloud from '../graphs/word-cloud-modal'
import { metadataFiltersURL , normalFiltersURL} from "../helpers/filters";
let content = document.getElementById("data-table-content");
export function createTable(page){
    update.startUpdate()
    content.innerHTML = "Loading...";
    let pagination = document.getElementById("data-table-pagination");
    pagination.innerHTML = ""
    let pageSize = document.getElementById("data-table-page-size").value
    let urlParams = metadataFiltersURL()+ "&" + normalFiltersURL()
    document.getElementById("data-items-table-csv").href = `/api/new-data/project/${window.project_id}/?format=csv&` + urlParams
    fetch(`/api/new-data/project/${window.project_id}/?page=${page}&page-size=${pageSize}&` + urlParams)
    .then((response) => response.json())
    .then((data) => {
        content.innerHTML = "";
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
        <b>${element.sourceLabel}</b>
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
        createPagination(firstElement, lastElement, data.total, data.currentPage, data.totalPages, pagination, createTable);
        update.finishUpdate()
    });
}

document.querySelector("#show-word-cloud-data-items-table").addEventListener("click", (e)=>{
    document.querySelector("#word-cloud-modal").style.display = "block"
    let urlParams = metadataFiltersURL() + normalFiltersURL()
    let wordCloudURL = `/api/new-data/project/${window.project_id}/?format=word-cloud&` + urlParams
    wordCloud(wordCloudURL)
})
